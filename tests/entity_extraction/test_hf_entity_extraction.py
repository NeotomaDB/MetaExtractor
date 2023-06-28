# Author: Ty Andrews
# Date: June 23 2023

import os
import sys

import pytest
import pandas as pd

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.prediction.hf_entity_extraction import (
    load_ner_model_pipeline,
    get_hf_token_labels,
    get_predicted_labels,
)


@pytest.fixture
def dummy_model_path():
    # this is a tiny randomly initialized model used to test model loading
    return "hf-internal-testing/tiny-random-distilbert"


# used to test parsing of NER results, not exact entities labelling
@pytest.fixture
def tiny_ner_model():
    ner_pipe = load_ner_model_pipeline("gagan3012/bert-tiny-finetuned-ner")
    return ner_pipe


def test_load_ner_model_pipeline_return_types(dummy_model_path):
    # Load the NER model pipeline
    ner_pipe = load_ner_model_pipeline(dummy_model_path)

    # Check the return types
    assert ner_pipe.task == "ner"
    assert "TokenClassificationPipeline" in str(type(ner_pipe))


def test_load_ner_model_pipeline_nonexistent_model():
    # Try to load a non-existent model
    with pytest.raises(OSError):
        load_ner_model_pipeline("nonexistent_model")


def test_get_hf_token_labels():
    # Example input
    labelled_entities = [
        {"start": 0, "end": 8, "entity_group": "PER"},
        {"start": 15, "end": 19, "entity_group": "LOC"},
        {"start": 30, "end": 36, "entity_group": "ORG"},
    ]
    raw_text = "John Doe is in Paris working at OpenAI."

    # Expected output
    expected_tokens = ["John", "Doe", "is", "in", "Paris", "working", "at", "OpenAI."]
    expected_labels = ["B-PER", "I-PER", "O", "O", "B-LOC", "O", "O", "B-ORG"]

    # Call the function
    tokens, labels = get_hf_token_labels(labelled_entities, raw_text)

    # Compare the actual output with the expected output
    assert tokens == expected_tokens
    assert labels == expected_labels


def test_get_predicted_labels(tiny_ner_model):
    # check the function returns correct types and required columns
    ner_pipe = tiny_ner_model

    dummy_df = pd.DataFrame(
        {
            "text": [
                # ["John", "Doe", "is", "in", "Paris", "working", "at", "OpenAI."],
                "John Doe is in Paris working at OpenAI.",
            ],
        }
    )

    extracted_df = get_predicted_labels(dummy_df, ner_pipe)

    assert isinstance(extracted_df, pd.DataFrame)
    assert "predicted_labels" in extracted_df.columns
    assert "split_text" in extracted_df.columns
    assert extracted_df.split_text[0] == [
        "John",
        "Doe",
        "is",
        "in",
        "Paris",
        "working",
        "at",
        "OpenAI.",
    ]
    assert isinstance(extracted_df.predicted_labels.iloc[0], list)
