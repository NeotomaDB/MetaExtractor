# Author: Ty Andrews
# Date: 2023-05-30
"""This script manages custom evaluation of the fine tuned hugging face models.

Usage: hf_evaluate.py --data_path=<data_path> --model_path=<model_path> --output_path=<output_path> --model_name=<model_name> [--max_samples=<max_samples>]

Options:
    --data_path=<data_path>         The path to the evaluation data in json format.
    --model_path=<model_path>       The path to the model to load.
    --output_path=<output_path>     The path to export the results & plots to.
    --model_name=<model_name>       The name of the model.
    --max_samples=<max_samples>     The maximum number of samples to evaluate, set to 1 for CPU testing. [default: None]
"""

import os, sys

import pandas as pd
import numpy as np

import time
import json
from tqdm import tqdm
from docopt import docopt
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir)
)

from src.entity_extraction.evaluation.entity_extraction_evaluation import (
    calculate_entity_classification_metrics,
    plot_token_classification_report,
    generate_classification_results,
    generate_confusion_matrix,
    export_classification_results,
    export_classification_report_plots,
)
from src.logs import get_logger

logger = get_logger(__name__)


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
    # ensure raw_text is a string and labelled_entities is a list
    if not isinstance(raw_text, str):
        raise TypeError(f"raw_text must be a string. Got {type(raw_text)}")
    elif not isinstance(labelled_entities, list):
        raise TypeError(
            f"labelled_entities must be a list. Got {type(labelled_entities)}"
        )

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

    device_str = "cuda:0" if torch.cuda.is_available() else "cpu"
    if "cuda" in device_str:
        logger.info("Using GPU for predictions, batch size of 32")
        batch_size = 32
    else:
        logger.info("Using CPU for predictions, batch size of 1")
        batch_size = 1

    # load the model
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, model_max_length=512, padding=True, truncation=True
    )
    ner_pipe = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        device=torch.device(device_str),
        batch_size=batch_size,
        aggregation_strategy="simple",
    )

    return ner_pipe, model, tokenizer


def load_evaluation_data(data_file_path: str):
    """
    Loads the evaluation data.

    Parameters
    ----------
    data_path : str
        The path to the evaluation data in json format.

    Returns
    -------
    df : pandas.DataFrame
        The evaluation data.
    """

    # ensure the data file exists and is json file
    if not os.path.exists(data_file_path):
        raise Exception("Data file does not exist.")

    if not data_file_path.endswith(".json"):
        raise Exception("Data file must be json format.")

    # load the data
    df = pd.read_json(data_file_path, lines=True)

    return df


def get_predicted_labels(ner_pipe, df):
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

    if len(df) == 0:
        raise ValueError("The provided dataframe is empty.")

    # huggingface needs list of lists with strings for batch processing
    df["joined_text"] = df["tokens"].apply(lambda x: " ".join(x))

    # time the excution
    start = time.time()
    predicted_labels = ner_pipe(df.joined_text.to_list())
    df["predicted_labels"] = pd.Series(predicted_labels)
    logger.info(
        f"Prediction time for {len(df)} chunks: {time.time() - start:.2f} seconds"
    )

    df[["split_text", "predicted_tokens"]] = df.apply(
        lambda row: get_hf_token_labels(row.predicted_labels, row.joined_text),
        axis="columns",
        result_type="expand",
    )

    return df


def main():
    opt = docopt(__doc__)

    # run evaluation for each json file in the data directory
    for file in os.listdir(opt["--data_path"]):
        # skip non json files and only ones that contain the words train/val/test
        if not file.endswith(".json") or (
            "train" not in file and "val" not in file and "test" not in file
        ):
            continue
        logger.info(f"Evaluating {file}")
        file_name = file.split(".")[0]

        # load the evaluation data
        df = load_evaluation_data(os.path.join(opt["--data_path"], file))

        if opt["--max_samples"] != "None":
            logger.info(
                f"Using just a subsample of the data of size {opt['--max_samples']}"
            )
            # reset index and drop it
            df = df.sample(int(opt["--max_samples"])).reset_index(drop=True)

        # load the model
        ner_pipe, model, tokenizer = load_ner_model_pipeline(opt["--model_path"])

        logger.info("Loaded model, generating predictions, this may take a while.")
        # get the predicted labels
        df = get_predicted_labels(ner_pipe, df)

        logger.info("Generated predictions, calculating classification results")
        # get the classification results
        classification_results = generate_classification_results(
            df.ner_tags.tolist(), df.predicted_tokens.tolist()
        )

        # export the classification results
        export_classification_results(
            classification_results,
            opt["--output_path"],
            opt["--model_name"] + "_" + file_name,
        )

        # export the classification report plots
        export_classification_report_plots(
            true_tokens=df.ner_tags.tolist(),
            predicted_tokens=df.predicted_tokens.tolist(),
            output_path=opt["--output_path"],
            model_name=opt["--model_name"] + "_" + file_name,
        )

        generate_confusion_matrix(
            labelled_tokens=df.ner_tags.tolist(),
            predicted_tokens=df.predicted_tokens.tolist(),
            output_path=opt["--output_path"],
            model_name=opt["--model_name"] + "_" + file_name,
        )


if __name__ == "__main__":
    main()
