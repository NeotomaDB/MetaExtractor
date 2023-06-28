# Author: Jenit Jain
# Date: 2023-06-21
"""This script manages the custom data artifact creation for training and fine tuning of spacy models.

Usage: spacy_preprocess.py --data_path=<data_path>

Options:
    --data_path=<data_path>         The path to the dataset in JSONLines format.
"""

import os
import sys
import spacy
import json
import logging
import glob
from docopt import docopt
from spacy.tokens import DocBin

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

def preprocess_data(data_path: str):
    """Creates data artifacts used by the Spacy model for training

    Parameters
    ----------
    data_path: str
        Path to directory containing the train/val/test folders
    """
    
    # If the data_path consists of txt files with JSONLines, load all the files in the directory
    nlp = spacy.blank("en")
    train_files = glob.glob(os.path.join(data_path, "train", "*.txt"))
    val_files = glob.glob(os.path.join(data_path, "val", "*.txt"))
    train_files.extend(glob.glob(os.path.join(data_path, "train", "*.json")))
    val_files.extend(glob.glob(os.path.join(data_path, "val", "*.json")))
                
    train_doc_bin = get_doc(nlp, train_files)
    train_doc_bin.to_disk(os.path.join(data_path, "train.spacy"))
    
    val_doc_bin = get_doc(nlp, val_files)
    val_doc_bin.to_disk(os.path.join(data_path, "val.spacy"))

def get_doc(nlp, files):
    """Creates and saves a doc bin object for training
    
    Parameters
    ----------
    nlp: spacy.lang
        A blank nlp object for english language
    files: list
        List of files that contain labelled entities
        
    Returns
    ----------
    doc_bin: DocBin
        DocBin object that can be used for training the spacy model
    """
    doc_bin = DocBin()
    for labelled_file in files:
        
        with open(labelled_file, 'r') as fin:
            task = json.load(fin)
            
        if labelled_file.endswith(".txt"):
            text = task['task']['data']["text"]
        else:
            text = task['data']["text"]
        
        entities = []
        doc = nlp.make_doc(text)

        for label in task['result']:
            start = label['value']['start']
            end = label['value']['end']
            ent = label['value']['labels'][0]
            span = doc.char_span(start, end, label=ent)
            if span is not None:
                entities.append(span)
                
        doc.ents = entities
        doc_bin.add(doc)
    
    return doc_bin
if __name__ == "__main__":
    opt = docopt(__doc__)
    assert  os.path.exists(opt['--data_path']), \
            f"Path to data directory {opt['--data_path']} does not exist."
    preprocess_data(opt['--data_path'])