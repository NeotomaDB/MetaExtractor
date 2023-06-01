# Author: Ty Andrews
# Date: 2023-05-24
"""This script procsses the labelstudio output data into a format used by huggingface.

Usage: labelstudio_preprocessing.py --label_files=<label_files> [--max_seq_length=<max_token_length>]

Options:
    --label_files=<label_files>             The path to where the label files are. [default: all]
    --max_seq_length=<max_token_length>   How many tokens the text is split into per training example. [default: 256]
"""

import os, sys

import pandas as pd
import numpy as np
import json
from docopt import docopt
import logging

sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir)
)

logger = logging.getLogger(__name__)

from src.entity_extraction.entity_extraction_evaluation import get_token_labels

opt = docopt(__doc__)


# function that takes a folder location in data/labelled and produces a
# folder called hf_processed in data/labelled with the same files but
# with the format required for the hf-token-classification model
def convert_labelled_data_to_hf_format(
    labelled_file_path: str,
    max_seq_length: int = 256,
):
    """
    Processes train/val/test data from labelstudio into a format used by huggingface.

    Parameters
    ----------
    labelled_file_path : str
        The path to the folder containing the labelled data.
    max_seq_length : int, optional
        The maximum number of words per training example, by default 256.

    Returns
    -------
    None.
    """

    # check the folder exists
    if not os.path.exists(labelled_file_path):
        raise FileNotFoundError(f"The folder {labelled_file_path} does not exist.")

    # check the folder contains folders train/test/val
    if not os.path.exists(os.path.join(labelled_file_path, "train")):
        raise FileNotFoundError(
            f"The folder {labelled_file_path} does not contain a train folder."
        )
    if not os.path.exists(os.path.join(labelled_file_path, "test")):
        raise FileNotFoundError(
            f"The folder {labelled_file_path} does not contain a test folder."
        )
    if not os.path.exists(os.path.join(labelled_file_path, "val")):
        raise FileNotFoundError(
            f"The folder {labelled_file_path} does not contain a val folder."
        )

    for folder in ["train", "test", "val"]:
        data_folder = os.path.join(labelled_file_path, folder)

        labelled_chunks = []

        for file in os.listdir(data_folder):
            # if file doesn't end with txt skip it
            if not file.endswith(".txt"):
                continue

            with open(os.path.join(data_folder, file), "r") as f:
                task = json.load(f)

            try:
                raw_text = task["task"]["data"]["text"]
                annotation_result = task["result"]
                gdd_id = task["task"]["data"]["gdd_id"]

                labelled_entities = [
                    annotation["value"] for annotation in annotation_result
                ]

                tokens, token_labels = get_token_labels(labelled_entities, raw_text)

                # split the data into chunks of tokens and labels
                chunked_tokens = [
                    tokens[i : i + max_seq_length]
                    for i in range(0, len(tokens), max_seq_length)
                ]
                chunked_labels = [
                    token_labels[i : i + max_seq_length]
                    for i in range(0, len(token_labels), max_seq_length)
                ]

                # make each chunk a dict with keys ner_tags and tokens
                chunked_data = [
                    {
                        "ner_tags": chunked_labels[i],
                        "tokens": chunked_tokens[i],
                    }
                    for i in range(len(chunked_tokens))
                ]

                labelled_chunks.extend(chunked_data)

            except Exception as e:
                logger.warning(f"Issue detected with file, skipping: {file}, {e}")

            # save the data to the hf_processed folder with each list item in a new line delimited json
            with open(os.path.join(labelled_file_path, f"{folder}.json"), "w") as f:
                for item in labelled_chunks:
                    f.write(json.dumps(item) + "\n")


# needed as tokenizing adds CLS and SEP tokens, doesn't match labels
# see here for more detail: https://huggingface.co/docs/transformers/tasks/token_classification
# It does:
# 1. Mapping all tokens to their corresponding word with the word_ids method.
# 2. Assigning the label -100 to the special tokens [CLS] and [SEP] so they’re ignored by the PyTorch loss function.
# 3. Only labeling the first token of a given word. Assign -100 to other subtokens from the same word.
def tokenize_and_align_labels(examples, tokenizer):
    tokenized_inputs = tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True
    )

    labels = []
    for i, label in enumerate(examples[f"ner_tags"]):
        word_ids = tokenized_inputs.word_ids(
            batch_index=i
        )  # Map tokens to their respective word.
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:  # Set the special tokens to -100.
            if word_idx is None:
                label_ids.append(-100)
            elif (
                word_idx != previous_word_idx
            ):  # Only label the first token of a given word.
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs


# main function to process files using docopt
if __name__ == "__main__":
    convert_labelled_data_to_hf_format(
        labelled_file_path=opt["--label_files"],
        max_seq_length=int(opt["--max_token_length"]),
        train_split=float(opt["--train_split"]),
        val_split=float(opt["--val_split"]),
        test_split=float(opt["--test_split"]),
    )
