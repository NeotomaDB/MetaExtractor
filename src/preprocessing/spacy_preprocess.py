# Author: Jenit Jain
# Date: 2023-06-21
"""This script manages the custom training and fine tuning of spacy models.

Usage: spacy_preprocess.py --data_path=<data_path> --train_split=<train_split> --val_split=<val_split> --test_split=<test_split>

Options:
    --data_path=<data_path>         The path to the dataset in JSONLines format.
    --train_split=<train_split>     The ratio of files to include in the training set.
    --val_split=<val_split>         The ratio of files to include in the validation set.
    --test_split=<test_split>       The ratio of files to include in the testing set.
"""

import os
import spacy
import json
import logging
import glob
from docopt import docopt
from spacy.tokens import DocBin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    def get_doc(files):
        """Creates and saves a doc bin object for training
        
        Parameters
        ----------
        files: list
            List of files that contain labelled entities
            
        Returns
        ----------
        doc_bin: DocBin
            DocBin object that can be used for training the spacy model
        """
        doc_bin = DocBin()
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
            doc_bin.add(doc)
            
        return doc_bin
    
    train_doc_bin = get_doc(train_files)
    train_doc_bin.to_disk(os.path.join(data_path, "train.spacy"))
    
    val_doc_bin = get_doc(val_files)
    val_doc_bin.to_disk(os.path.join(data_path, "val.spacy"))
    
    # TODO: Else If the data_path consists of parquet files, load JSON files from all parquet files in the directory
    
if __name__ == "__main__":
    opt = docopt(__doc__)
    preprocess_data(opt['--data_path'])