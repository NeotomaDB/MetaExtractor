# Author: Ty Andrews
# Date: 2023-05-24
"""This script procsses the labelstudio output data into a format used by huggingface.

Usage: labelstudio_preprocessing.py --label_files=<label_files> [--max_token_length=<max_token_length>] [--train_split=<train_split>] [--val_split=<val_split>] [--test_split=<test_split>]

Options:
    --label_files=<label_files>             The path to where the label files are. [default: all]
    --max_token_length=<max_token_length>   How many tokens the text is split into per training example. [default: 512]
    --train_split=<train_split>             What percentage of examples to dedicate to train set [default: 0.7]
    --val_split=<val_split>                 What percentage of examples to dedicate to validation set [default: 0.15]
    --test_split=<test_split>               What percentage of examples to dedicate to test set [default: 0.15]
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

id2label = {
    0: "O",
    1: "B-GEOG",
    2: "I-GEOG",
    3: "B-SITE",
    4: "I-SITE",
    5: "B-EMAIL",
    6: "I-EMAIL",
    7: "B-ALTI",
    8: "I-ALTI",
    9: "B-TAXA",
    10: "I-TAXA",
    11: "B-REGION",
    12: "I-REGION",
    13: "B-AGE",
    14: "I-AGE",
}

label2id = {
    "O": 0,
    "B-GEOG": 1,
    "I-GEOG": 2,
    "B-SITE": 3,
    "I-SITE": 4,
    "B-EMAIL": 5,
    "I-EMAIL": 6,
    "B-ALTI": 7,
    "I-ALTI": 8,
    "B-TAXA": 9,
    "I-TAXA": 10,
    "B-REGION": 11,
    "I-REGION": 12,
    "B-AGE": 13,
    "I-AGE": 14,
}


# function that takes a folder location in data/labelled and produces a
# folder called hf_processed in data/labelled with the same files but
# with the format required for the hf-token-classification model
def convert_labelled_data_to_hf_format(
    labelled_file_path: str,
    max_seq_length: int = 128,
    train_split: float = 0.65,
    val_split: float = 0.2,
    test_split: float = 0.15,
    seed: int = 42,
):
    """
    Parameters
    ----------
    labelled_file_path : str
        The path to the folder containing the labelled data.

    Returns
    -------
    None.
    """

    # check the folder exists
    if not os.path.exists(labelled_file_path):
        raise FileNotFoundError(f"The folder {labelled_file_path} does not exist.")

    # check the folder contains files
    if len(os.listdir(labelled_file_path)) == 0:
        raise FileNotFoundError(
            f"The folder {labelled_file_path} does not contain any files."
        )

    # create output folder if it does not exist
    hf_processed_folder = os.path.join(labelled_file_path, "hf_processed")
    if not os.path.exists(hf_processed_folder):
        os.mkdir(hf_processed_folder)

    gdd_ids = get_article_gdd_ids(labelled_file_path)

    # set seed for reproducibility
    np.random.seed(seed)
    # split the gdd_ids into train, val and test and ensure not overlapping
    train_gdd_ids = np.random.choice(
        gdd_ids, size=int(train_split * len(gdd_ids)), replace=False
    )
    remaining_gdd_ids = np.setdiff1d(gdd_ids, train_gdd_ids)

    val_gdd_ids = np.random.choice(
        remaining_gdd_ids, size=int(val_split * len(gdd_ids)), replace=False
    )
    remaining_gdd_ids = np.setdiff1d(remaining_gdd_ids, val_gdd_ids)

    test_gdd_ids = np.random.choice(
        remaining_gdd_ids, size=int(test_split * len(gdd_ids)), replace=False
    )

    # assert no overlap between train, val and test
    assert len(np.intersect1d(train_gdd_ids, val_gdd_ids)) == 0
    assert len(np.intersect1d(train_gdd_ids, test_gdd_ids)) == 0
    assert len(np.intersect1d(val_gdd_ids, test_gdd_ids)) == 0

    train_data = []
    val_data = []
    test_data = []

    # iterate through the files in the folder and convert them to the hf format
    for file in os.listdir(labelled_file_path):
        # if file doesn't end with txt skip it
        if not file.endswith(".txt"):
            continue

        with open(os.path.join(labelled_file_path, file), "r") as f:
            task = json.load(f)

        try:
            raw_text = task["task"]["data"]["text"]
            annotation_result = task["result"]
            gdd_id = task["task"]["data"]["gdd_id"]

            labelled_entities = [
                annotation["value"] for annotation in annotation_result
            ]

            tokens, token_labels = get_token_labels(labelled_entities, raw_text)

            token_label_ids = [label2id[label] for label in token_labels]

            # split the data into chunks of tokens and labels
            chunked_tokens = [
                tokens[i : i + max_seq_length]
                for i in range(0, len(tokens), max_seq_length)
            ]
            chunked_token_label_ids = [
                token_label_ids[i : i + max_seq_length]
                for i in range(0, len(token_label_ids), max_seq_length)
            ]
            chunked_labels = [
                token_labels[i : i + max_seq_length]
                for i in range(0, len(token_labels), max_seq_length)
            ]

            # make each chunk a dict with keys ner_tags and tokens
            chunked_data = [
                {
                    "ner_tags": chunked_labels[i],
                    "text": chunked_tokens[i],
                    # "label_ids": chunked_token_label_ids[i],
                }
                for i in range(len(chunked_tokens))
            ]
        except Exception as e:
            logger.warning(f"Issue detected with file, skipping: {file}, {e}")

        # put the data into the correct split
        if gdd_id in train_gdd_ids:
            train_data.extend(chunked_data)
        elif gdd_id in val_gdd_ids:
            val_data.extend(chunked_data)
        elif gdd_id in test_gdd_ids:
            test_data.extend(chunked_data)

    # save the data to the hf_processed folder with each list item in a new line delimited json
    with open(os.path.join(hf_processed_folder, "train.json"), "w") as f:
        for item in train_data:
            f.write(json.dumps(item) + "\n")

    with open(os.path.join(hf_processed_folder, "val.json"), "w") as f:
        for item in val_data:
            f.write(json.dumps(item) + "\n")

    with open(os.path.join(hf_processed_folder, "test.json"), "w") as f:
        for item in test_data:
            f.write(json.dumps(item) + "\n")


def get_article_gdd_ids(labelled_file_path: str):
    """
    Parameters
    ----------
    labelled_file_path : str
        The path to the folder containing the labelled data.

    Returns
    -------
    list
        A list of the gdd_ids of the articles in the labelled data.
    """

    # check the folder exists
    if not os.path.exists(labelled_file_path):
        raise FileNotFoundError(f"The folder {labelled_file_path} does not exist.")

    # check the folder contains files
    if len(os.listdir(labelled_file_path)) == 0:
        raise FileNotFoundError(
            f"The folder {labelled_file_path} does not contain any files."
        )

    # iterate through the files and get the unique gdd_ids
    gdd_ids = []
    for file in os.listdir(labelled_file_path):
        # if file doesn't end with txt skip it
        if not file.endswith(".txt"):
            continue

        with open(os.path.join(labelled_file_path, file), "r") as f:
            task = json.load(f)

        try:
            gdd_id = task["task"]["data"]["gdd_id"]
        except Exception as e:
            logger.warning(f"Issue with file data: {file}, {e}")

        if gdd_id not in gdd_ids:
            gdd_ids.append(gdd_id)

    return gdd_ids


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
