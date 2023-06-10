# Author: Ty Andrews
# Date: 2023-05-31
"""This script splits the  labelled text into train, validation, and test sets.

Usage: labelstudio_preprocessing.py --raw_label_path=<raw_label_path> --output_path=<output_path> [--train_split=<train_split>] [--val_split=<val_split>] [--test_split=<test_split>]

Options:
    --raw_label_path=<raw_label_path>       The path to where the raw label files are.
    --output_path=<output_path>             The path to where the output files will be written.
    --train_split=<train_split>             What percentage of examples to dedicate to train set [default: 0.7]
    --val_split=<val_split>                 What percentage of examples to dedicate to validation set [default: 0.15]
    --test_split=<test_split>               What percentage of examples to dedicate to test set [default: 0.15]
"""

import os, sys
import pandas as pd
import numpy as np
import logging
import shutil
import json

from docopt import docopt

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

logger = logging.getLogger(__name__)
# set logging level to display info and above
logger.setLevel(logging.INFO)


def separate_labels_to_train_val_test(
    labelled_file_path: str,
    output_path: str,
    train_split: float = 0.7,
    val_split: float = 0.15,
    test_split: float = 0.15,
    seed: int = 42,
):
    """
    This function splits the labelled data into train, validation and test sets.

    Parameters
    ----------
    labelled_file_path : str
        The path to the folder containing the labelled data.

    Returns
    -------
    None.
    """

    # ensure the splits add up to 1 to within 2 decimal places
    if round(train_split + val_split + test_split, 2) != 1:
        raise ValueError(
            f"The splits must add up to 1, currently they add up to {round(train_split + val_split + test_split, 2)}"
        )

    # check the folder exists
    if not os.path.exists(labelled_file_path):
        raise FileNotFoundError(f"The folder {labelled_file_path} does not exist.")

    # check the folder contains files
    if len(os.listdir(labelled_file_path)) == 0:
        raise FileNotFoundError(
            f"The folder {labelled_file_path} does not contain any files."
        )

    # make sure the detination folder exists and subfolders
    if not os.path.exists(output_path):
        logger.info(f"Creating folder {output_path} and train/val/test subfolders")
        os.mkdir(output_path)
    else:
        logger.info(f"Folder {output_path} already exists.")

    os.makedirs(os.path.join(output_path, "train"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "val"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "test"), exist_ok=True)

    gdd_ids = get_article_gdd_ids(labelled_file_path)

    # set seed for reproducibility
    np.random.seed(seed)
    # split the gdd_ids into train, val and test and ensure not overlapping
    train_gdd_ids = np.random.choice(
        gdd_ids, size=round(train_split * len(gdd_ids)), replace=False
    )
    remaining_gdd_ids = np.setdiff1d(gdd_ids, train_gdd_ids)

    val_gdd_ids = np.random.choice(
        remaining_gdd_ids, size=round(val_split * len(gdd_ids)), replace=False
    )
    remaining_gdd_ids = np.setdiff1d(remaining_gdd_ids, val_gdd_ids)

    test_gdd_ids = np.random.choice(
        remaining_gdd_ids, size=round(test_split * len(gdd_ids)), replace=False
    )
    remaining_gdd_ids = np.setdiff1d(remaining_gdd_ids, test_gdd_ids)

    # check no gdd_ids' left over due to split rounding errors and if they are assign to train
    if len(np.setdiff1d(remaining_gdd_ids, test_gdd_ids)) > 0:
        train_gdd_ids = np.append(train_gdd_ids, remaining_gdd_ids)
        logger.info(
            f"Due to train/val/test split rounding anomaly, {len(remaining_gdd_ids)} gdd_ids were assigned to train."
        )

    # convert all gdd_id arrays to lists for json serialization
    train_gdd_ids = train_gdd_ids.tolist()
    val_gdd_ids = val_gdd_ids.tolist()
    test_gdd_ids = test_gdd_ids.tolist()

    # ensure no overlap between train, val and test
    assert len(np.intersect1d(train_gdd_ids, val_gdd_ids)) == 0
    assert len(np.intersect1d(train_gdd_ids, test_gdd_ids)) == 0
    assert len(np.intersect1d(val_gdd_ids, test_gdd_ids)) == 0

    # raise warning if any split is length zero when the split is not zero
    if len(train_gdd_ids) == 0 and train_split != 0:
        logger.warning(
            f"Train split is zero, check the train split ratio and the number of files in the folder."
        )
    if len(val_gdd_ids) == 0 and val_split != 0:
        logger.warning(
            f"Val split is zero, check the val split ratio and the number of files in the folder."
        )
    if len(test_gdd_ids) == 0 and test_split != 0:
        logger.warning(
            f"Test split is zero, check the test split ratio and the number of files in the folder."
        )

    data_metrics = {
        "split_seed": seed,
        "split_ratios": {
            "train": train_split,
            "val": val_split,
            "test": test_split,
        },
        "train": {
            "gdd_ids": train_gdd_ids,
            "article_count": len(train_gdd_ids),
            "num_words": 0,
            "entity_counts": {},
        },
        "val": {
            "gdd_ids": val_gdd_ids,
            "article_count": len(val_gdd_ids),
            "num_words": 0,
            "entity_counts": {},
        },
        "test": {
            "gdd_ids": test_gdd_ids,
            "article_count": len(test_gdd_ids),
            "num_words": 0,
            "entity_counts": {},
        },
    }

    # iterate through the files in the folder and convert them to the hf format
    for file in os.listdir(labelled_file_path):
        # if file doesn't end with txt skip it
        if not file.endswith(".txt"):
            continue

        with open(os.path.join(labelled_file_path, file), "r") as f:
            task = json.load(f)

        try:
            gdd_id = task["task"]["data"]["gdd_id"]
            raw_text = task["task"]["data"]["text"]
            annotation_result = task["result"]

            # get the number of words in the article
            num_words = len(raw_text.split())

            entity_counts = {}
            for entity in annotation_result:
                entity_name = entity["value"]["labels"][0]

                if entity_name not in entity_counts:
                    entity_counts[entity_name] = 1
                else:
                    entity_counts[entity_name] += 1

        except Exception as e:
            logger.warning(f"Issue detected with file, skipping: {file}, {e}")

        if gdd_id in train_gdd_ids:
            shutil.copy2(
                os.path.join(labelled_file_path, file),
                os.path.join(output_path, "train"),
            )

            data_metrics["train"]["num_words"] += num_words
            for entity_name, count in entity_counts.items():
                if entity_name not in data_metrics["train"]["entity_counts"]:
                    data_metrics["train"]["entity_counts"][entity_name] = count
                else:
                    data_metrics["train"]["entity_counts"][entity_name] += count
        elif gdd_id in val_gdd_ids:
            shutil.copy2(
                os.path.join(labelled_file_path, file),
                os.path.join(output_path, "val"),
            )
            data_metrics["val"]["num_words"] += num_words
            for entity_name, count in entity_counts.items():
                if entity_name not in data_metrics["val"]["entity_counts"]:
                    data_metrics["val"]["entity_counts"][entity_name] = count
                else:
                    data_metrics["val"]["entity_counts"][entity_name] += count
        elif gdd_id in test_gdd_ids:
            shutil.copy2(
                os.path.join(labelled_file_path, file),
                os.path.join(output_path, "test"),
            )
            data_metrics["test"]["num_words"] += num_words
            for entity_name, count in entity_counts.items():
                if entity_name not in data_metrics["test"]["entity_counts"]:
                    data_metrics["test"]["entity_counts"][entity_name] = count
                else:
                    data_metrics["test"]["entity_counts"][entity_name] += count

    # save the data metrics to json indented
    with open(os.path.join(output_path, "data_metrics.json"), "w") as f:
        json.dump(data_metrics, f, indent=2)

    logger.info("Finished separating files into train, val and test sets.")


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


def main():
    opt = docopt(__doc__)
    separate_labels_to_train_val_test(
        labelled_file_path=opt["--raw_label_path"],
        output_path=opt["--output_path"],
        train_split=float(opt["--train_split"]),
        val_split=float(opt["--val_split"]),
        test_split=float(opt["--test_split"]),
    )


if __name__ == "__main__":
    main()