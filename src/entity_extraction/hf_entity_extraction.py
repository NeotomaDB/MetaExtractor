# Author: Ty Andrews
# Date: 2023-06-07

import os
import sys

import pandas as pd
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from torch import cuda

from src.logs import get_logger

logger = get_logger(__name__)


def load_ner_model_pipeline(model_path: str):
    """
    Loads a hugging face named entity recognition model.

    Parameters
    ----------
    model_path : str
        The path to the model to load.

    Returns
    -------
    ner_pipe : transformers.pipelines.Pipeline
        The ner model pipeline.
    model : transformers.modeling_outputs.TokenClassifierOutput
        The loaded model.
    tokenizer : transformers.tokenization_bert.BertTokenizer
        The loaded tokenizer.
    """

    device = "cuda" if cuda.is_available() else "cpu"
    if device == "cuda":
        logger.info("Using GPU for predictions, batch size of 8")
        batch_size = 8
    else:
        logger.info("Using CPU for predictions, batch size of 1")
        batch_size = 1

    # load the model
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, model_max_length=512)
    ner_pipe = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        device=device,
        batch_size=batch_size,
        aggregation_strategy="simple",
    )

    return ner_pipe


def get_hf_token_labels(labelled_entities, raw_text):
    """
    Returns a list of labels per token in the raw text from hugging face generated labels.

    Parameters
    ----------
    labelled_entities : list
        A list of dictionaries containing the labelled entities including the
        start and end indices of the entity, the entity label, and the entity
        text.
    raw_text : str
        The raw text that the entities were extracted from.

    Returns
    -------
    token_labels : list
        A list of labels per token in the raw text.
    """

    # split the text by whitespace
    split_text = raw_text.split()

    # create a list of labels per token
    token_labels = ["O"] * len(split_text)

    for entity in labelled_entities:
        start = entity["start"]
        end = entity["end"]
        label = entity["entity_group"]

        # get the token indices that the entity spans
        token_start = len(raw_text[:start].split())
        token_end = len(raw_text[:end].split())

        try:
            # if the entity spans multiple tokens
            if token_start != token_end:
                token_labels[token_start] = f"B-{label}"
                for i in range(token_start + 1, token_end):
                    token_labels[i] = f"I-{label}"
            else:
                token_labels[token_start] = f"B-{label}"
        except Exception as e:
            print(e)
            print("Error with entity: ", entity)
            print("Raw text: ", raw_text)
            print("Token start: ", token_start)
            print("Token end: ", token_end)

    return split_text, token_labels


def get_predicted_labels(text, ner_pipe):
    """
    Gets the predicted labels from the hugging face model.

    Parameters
    ----------
    ner_pipe : transformers.pipelines.Pipeline
        The ner model pipeline.
    df : pandas.DataFrame
        The evaluation data.

    Returns
    -------
    df : pandas.DataFrame
        The evaluation data with the predicted labels added.
    """

    # get the predicted labels
    df["predicted_labels"] = df["text"].apply(lambda x: ner_pipe(" ".join(x)))

    df[["split_text", "predicted_tokens"]] = df.apply(
        lambda row: get_hf_token_labels(row.predicted_labels, " ".join(row.text)),
        axis="columns",
        result_type="expand",
    )

    return df
