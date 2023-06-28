import os
import sys
import pytest
import logging
import spacy
import pandas as pd

logger = logging.getLogger(__name__)

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.evaluation.spacy_evaluate import (
    get_spacy_token_labels,
    load_evaluation_data,
    load_ner_model_pipeline,
    get_labels
)


@pytest.fixture
def example_token_labels():
    labels = {
        "start": 24,
        "end": 38,
        "entity_group": "SITE",
        "entity_text": "Lake Garibaldi",
    }
    text = "Sample text with a site Lake Garibaldi"
    
    return labels, text


@pytest.fixture
def data_file_path():
    
    return  os.path.join(
        os.path.dirname(__file__),
        "test_labelling_data_split",
        "test-label-1.txt"
    )
    
    
@pytest.fixture
def sample_ner_model():
    nlp = spacy.blank("en")
    data = {
        "task": {
            "data": {
                "text": "Sample text with a site Lake Garibaldi",
            }
        },
        "result": [
            {
                "value": {
                    "start": 24,
                    "end": 38,
                    "labels": ["PERSON"],
                    "text": "Lake Garibaldi"
                },
            }
        ]
    }
    return nlp, data

def test_get_spacy_token_labels(example_token_labels):
    labelled_entities, raw_text = example_token_labels
    
    expected_split_text = ["Sample", "text", "with", "a", "site", "Lake", "Garibaldi"]
    expected_token_labels = ["O", "O", "O", "O", "O", "B-SITE", "I-SITE"]
    
    assert expected_split_text, expected_token_labels == get_spacy_token_labels(labelled_entities, raw_text)
    

def test_load_evaluation_data(data_file_path):

    data = load_evaluation_data(data_file_path)
    
    assert isinstance(data, dict)


def test_load_ner_model_pipeline():
    ner_model_name = "random_model"
    
    with pytest.raises(OSError):
        ner_pipe = load_ner_model_pipeline(ner_model_name)
        
def test_get_labels(sample_ner_model):
    ner_model, data = sample_ner_model
    
    expected_predicted_labels = ['O', 'O', 'O', 'O', 'O', 'O', 'O']
    expected_tagged_labels =     ['O', 'O', 'O', 'O', 'O', 'B-PERSON', 'I-PERSON']
    
    predicted_labels, tagged_labels = get_labels(ner_model, data)
    
    assert expected_predicted_labels == predicted_labels
    assert expected_tagged_labels == tagged_labels
