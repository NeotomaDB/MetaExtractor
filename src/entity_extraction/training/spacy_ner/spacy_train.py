# Author: Jenit Jain
# Date: 2023-06-21
"""This script manages the custom training and fine tuning of spacy models.

Usage: spacy_train.py --data_path=<data_path> --train_split=<train_split> --val_split=<val_split> --test_split=<test_split>

Options:
    --data_path=<data_path>         The path to the evaluation data in json format.
    --train_split=<train_split>     The ratio of files to include in the training set.
    --val_split=<val_split>         The ratio of files to include in the validation set.
    --test_split=<test_split>       The ratio of files to include in the testing set.
"""

import os, sys

import pandas as pd
import numpy as np
import spacy
import json
import logging
import shutil
import glob
from docopt import docopt
from spacy.tokens import DocBin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

opt = docopt(__doc__)

def preprocess_data():
    # If the data_path consists of JSON, load all the files in the directory
    nlp = spacy.blank("en")
    train_doc_bin, val_doc_bin = DocBin(), DocBin()
    test_data = {}
    
    train_path = os.path.join(opt['--data_path'], "train")
    val_path = os.path.join(opt['--data_path'], "val")
    test_path = os.path.join(opt['--data_path'], "test")

    if os.path.exists(train_path):
        shutil.rmtree(train_path)
        logger.info(f"The folder '{train_path}' has been deleted.")
    if os.path.exists(val_path):
        shutil.rmtree(val_path)
        logger.info(f"The folder '{val_path}' has been deleted.")
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
        logger.info(f"The folder '{test_path}' has been deleted.")

    files = glob.glob(os.path.join(opt['--data_path'], "*"))
    train_ids, val_ids, test_ids = split_train_val_test(opt['--data_path'],
                                                        float(opt['--train_split']),
                                                        float(opt['--val_split']),
                                                        float(opt['--test_split']))
    
    for labelled_file in files:
        entities = []
        with open(labelled_file, 'r') as fin:
            article = fin.readlines()
            article_data = json.loads(article[0])
            text = article_data['task']['data']["text"]
            gdd_id = article_data['task']['data']["gdd_id"]
        
        doc = nlp.make_doc(text)

        for label in article_data['result']:
            start = label['value']['start']
            end = label['value']['end']
            ent = label['value']['labels'][0]
            span = doc.char_span(start, end, label=ent)
            if span is not None:
                entities.append(span)
                
        doc.ents = entities
        
        if gdd_id in train_ids:
            train_doc_bin.add(doc)
        elif gdd_id in val_ids:
            val_doc_bin.add(doc)
        else:
            test_data[f'{labelled_file.split("/")[-1]}'] = article_data
    
    
    
    # Write the artifacts to the same data directory
    os.makedirs(train_path, exist_ok=True)
    os.makedirs(val_path, exist_ok=True)
    os.makedirs(test_path, exist_ok=True)

    train_doc_bin.to_disk(os.path.join(train_path, "train.spacy"))
    val_doc_bin.to_disk(os.path.join(val_path, "val.spacy"))
    for test_file_name, test_file_data in test_data.items():
        with open(os.path.join(test_path, test_file_name), 'w') as fout:
            json.dump(article_data, fout)
    
    # TODO: Else If the data_path consists of parquet files, load JSON files from all parquet files in the directory
    
def split_train_val_test(
    labelled_file_path: str,
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
    train_split: float
        The ratio of files to add to the training dataset
    val_split: float
        The ratio of files to add to the validation dataset
    test_split: float
        The ratio of files to add to the testing dataset
    seed: int
        Random number to set the seed
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
    os.makedirs(os.path.join(opt['--data_path'], "train"), exist_ok=True)
    os.makedirs(os.path.join(opt['--data_path'], "val"), exist_ok=True)
    os.makedirs(os.path.join(opt['--data_path'], "test"), exist_ok=True)

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

    logger.info("Finished separating files into train, val and test sets.")
    logger.info(f"Training dataset contains {len(train_gdd_ids)} full text articles")
    logger.info(f"Validation dataset contains {len(val_gdd_ids)} full text articles")
    logger.info(f"Testing dataset contains {len(test_gdd_ids)} full text articles")
    
    return (
        train_gdd_ids,
        val_gdd_ids,
        test_gdd_ids
    )

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

if __name__ == "__main__":
    preprocess_data()