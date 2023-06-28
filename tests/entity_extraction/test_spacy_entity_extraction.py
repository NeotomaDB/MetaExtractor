# Author: Jenit Jain
# Date: June 28, 2023

import os
import sys
import spacy
import pytest

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from src.entity_extraction.prediction.spacy_entity_extraction import spacy_extract_all

@pytest.fixture
def load_empty_model():
    return spacy.blank("en")

@pytest.fixture
def load_null_model():
    return None

def test_spacy_extract_all(load_empty_model):
    
    text = "Sample text with a site Lake Garibaldi"
    
    entities = spacy_extract_all(text, load_empty_model)
    
    assert isinstance(entities, list)
    assert len(entities) == 0
    
def test_spacy_extract_all_with_null_model(load_null_model):
    
    text = "Sample text with a site Lake Garibaldi"
    
    entities = spacy_extract_all(text, load_null_model)
    
    assert isinstance(entities, list)

    try:
        # If the default model was not installed.
        assert len(entities) == 0
    except:
        assert entities[0]["start"] == 24
        assert entities[0]["end"] == 38
        assert entities[0]["labels"] == ["SITE"]
        assert entities[0]["text"] == "Lake Garibaldi"