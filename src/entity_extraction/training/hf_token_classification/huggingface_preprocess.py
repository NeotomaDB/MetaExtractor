# Author: Ty Andrews
# Date: 2023-05-24
"""This script procsses the labelstudio output data into a format used by huggingface.

Usage: labelstudio_preprocessing.py --label_files=<label_files> [--max_seq_length=<max_seq_length>] [--stride=<stride>]

Options:
    --label_files=<label_files>         The path to where the label files are. [default: all]
    --max_seq_length=<max_seq_length>   How many tokens the text is split into per training example. [default: 256]
    --stride=<stride>                   How many tokens to move the window by. [default: 192]
"""

import os, sys

import pandas as pd
import numpy as np
import json
from docopt import docopt

sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir)
)

from src.logs import get_logger

logger = get_logger(__name__)

from src.entity_extraction.entity_extraction_evaluation import get_token_labels


def convert_labelled_data_to_hf_format(
    labelled_file_path: str,
    max_seq_length: int = 256,
    stride: int = 192,
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

        logger.info(f"Processing {folder} data.")

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
                    for i in range(0, len(tokens), stride)
                ]
                chunked_labels = [
                    token_labels[i : i + max_seq_length]
                    for i in range(0, len(token_labels), stride)
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

            logger.debug(f"Processed {file}, generated {len(chunked_data)} chunks.")

            # save the data to the hf_processed folder with each list item in a new line delimited json
            with open(os.path.join(labelled_file_path, f"{folder}.json"), "w") as f:
                for item in labelled_chunks:
                    f.write(json.dumps(item) + "\n")


# main function to process files using docopt
if __name__ == "__main__":
    opt = docopt(__doc__)
    convert_labelled_data_to_hf_format(
        labelled_file_path=opt["--label_files"],
        max_seq_length=int(opt["--max_seq_length"]),
        stride=int(opt["--stride"]),
    )
