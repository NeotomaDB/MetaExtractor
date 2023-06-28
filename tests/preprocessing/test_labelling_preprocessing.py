# Author: Jenit Jain
# Date: June 23 2023

import os
import sys

import pytest
import pandas as pd
from collections import namedtuple

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.preprocessing.labelling_preprocessing import (
    clean_words,
    return_json,
    chunk_text
)
    

@pytest.fixture
def sample_words():
    words = ["This", "is", "a", "test", "sentence", "."]
    return words

@pytest.fixture
def json_args():
    args = {
        'nlp': None,
        'chunk': 'This is sample text with a site Lake Garibaldi and taxa Pinus',
        'chunk_local': 1, 
        'chunk_global': 1, 
        'chunk_subsection': 'Sample Subsection', 
        'gdd': 'sample xDD ID', 
        'doi': 'Sample DOI', 
        'article_hash_code': '3567c4fb5ecd02be',
        'model_version': 'v1',
    }
    
    return args


@pytest.fixture
def chunking_args():
    args = {
        '--char_len': '4000',
        '--min_len': '500',
    }
    text = "This is a test chunk text"
    return args, text


def test_clean_words(sample_words):
    words = sample_words
    
    expected_cleaned_words = ["This", "is", "a", "test", "sentence."]
    
    assert expected_cleaned_words == clean_words(words)
    

def test_return_json(json_args):

    labeled_json = return_json(**json_args)
    
    # Check entity text
    assert isinstance(labeled_json['predictions'][0]['result'], list)
    
def test_chunk_text(chunking_args):
    args, text = chunking_args
    
    expected_chunks = [
        'This is a test chunk text.'
    ]
    expected_local_index = [0]
    expected_subsection = ["This"]
    
    assert chunk_text(args, text) == (expected_chunks,
                                      expected_local_index,
                                      expected_subsection)