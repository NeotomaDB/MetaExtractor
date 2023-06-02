import os
import sys
import pytest
import logging
from transformers import pipeline
import pandas as pd

logger = logging.getLogger(__name__)

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.training.hf_token_classification.hf_evaluate import (
    get_hf_token_labels,
    get_predicted_labels,
    generate_classification_results,
)


@pytest.fixture
def example_inputs():
    labelled_entities = [
        {"start": 0, "end": 8, "entity_group": "PERSON"},
        {"start": 18, "end": 24, "entity_group": "LOCATION"},
    ]
    raw_text = "John Doe lives in London."
    return labelled_entities, raw_text


@pytest.fixture
def example_data():
    df = pd.DataFrame(
        {
            "tokens": [
                ["This", "is", "an", "example", "sentence."],
                ["Another", "example."],
            ],
        }
    )
    return df


@pytest.fixture
def ner_pipe():
    ner_model_name = "dslim/bert-base-NER"
    tokenizer_name = "dslim/bert-base-NER"

    ner_pipe = pipeline("ner", model=ner_model_name, tokenizer=tokenizer_name)
    yield ner_pipe


@pytest.fixture
def example_correct_tokens():
    true_tokens = [
        ["B-TAXA", "I-TAXA", "O", "B-AGE"],
    ]
    predicted_tokens = [
        ["B-TAXA", "I-TAXA", "O", "B-AGE"],
    ]

    return true_tokens, predicted_tokens


@pytest.fixture
def example_incorrect_tokens():
    true_tokens = [
        ["B-TAXA", "I-TAXA", "O", "B-AGE"],
    ]
    predicted_tokens = [
        ["O", "B-TAXA", "O", "B-AGE"],
    ]

    return true_tokens, predicted_tokens


def test_get_hf_token_labels(example_inputs):
    labelled_entities, raw_text = example_inputs

    expected_split_text = ["John", "Doe", "lives", "in", "London."]
    expected_token_labels = ["B-PERSON", "I-PERSON", "O", "O", "B-LOCATION"]

    split_text, token_labels = get_hf_token_labels(labelled_entities, raw_text)

    assert split_text == expected_split_text
    assert token_labels == expected_token_labels


def test_get_hf_token_labels_with_invalid_labelled_entities():
    labelled_entities = "invalid"  # Invalid input type: should be a list
    raw_text = "Some text"

    with pytest.raises(TypeError):
        get_hf_token_labels(labelled_entities, raw_text)


def test_get_hf_token_labels_with_invalid_raw_text():
    labelled_entities = []
    raw_text = 123  # Invalid input type: should be a string

    with pytest.raises(TypeError):
        get_hf_token_labels(labelled_entities, raw_text)


def test_get_predicted_labels(example_data, ner_pipe):
    df = example_data.copy()

    df = get_predicted_labels(ner_pipe, df)

    assert "joined_text" in df.columns
    assert "predicted_labels" in df.columns
    assert "split_text" in df.columns
    assert "predicted_tokens" in df.columns
    assert len(df) == len(example_data)


def test_get_predicted_labels_with_empty_dataframe(ner_pipe):
    df = pd.DataFrame()  # Empty DataFrame

    with pytest.raises(ValueError):
        get_predicted_labels(ner_pipe, df)


def test_get_predicted_labels_with_missing_tokens_column(ner_pipe):
    df = pd.DataFrame({"text": ["This is an example sentence.", "Another example."]})

    with pytest.raises(KeyError):
        get_predicted_labels(ner_pipe, df)


def test_generate_classification_results_with_correct_input(example_correct_tokens):
    true_tokens, predicted_tokens = example_correct_tokens

    results = generate_classification_results(true_tokens, predicted_tokens)

    # ensure the f1, accuracy, recall and precision are correct to 2 decimal places
    assert round(results["token"]["f1"], 2) == 1.0
    assert round(results["token"]["accuracy"], 2) == 1.0
    assert round(results["token"]["recall"], 2) == 1.0
    assert round(results["token"]["precision"], 2) == 1.0
    assert round(results["entity"]["f1"], 2) == 1.0
    assert round(results["entity"]["accuracy"], 2) == 1.0
    assert round(results["entity"]["recall"], 2) == 1.0
    assert round(results["entity"]["precision"], 2) == 1.0


def test_generate_classification_results_with_incorrect_input(example_incorrect_tokens):
    true_tokens, predicted_tokens = example_incorrect_tokens

    results = generate_classification_results(true_tokens, predicted_tokens)

    # ensure the f1, accuracy, recall and precision are correct to 2 decimpal places
    assert round(results["token"]["f1"], 2) == 0.80
    assert round(results["token"]["accuracy"], 2) == 0.75
    assert round(results["token"]["recall"], 2) == 0.67
    assert round(results["token"]["precision"], 2) == 1.0
    assert round(results["entity"]["f1"], 2) == 0.5
    assert round(results["entity"]["accuracy"], 2) == 0.5
    assert round(results["entity"]["recall"], 2) == 0.5
    assert round(results["entity"]["precision"], 2) == 0.5


def test_generate_classification_results_with_empty_input():
    true_tokens = []
    predicted_tokens = []

    with pytest.raises(ValueError):
        generate_classification_results(true_tokens, predicted_tokens)


def test_generate_classification_results_with_invalid_input_lengths():
    true_tokens = [["B-TAXA", "I-TAXA", "O", "B-PER"]]
    predicted_tokens = [["B-TAXA", "I-TAXA", "O"]]

    with pytest.raises(ValueError):
        generate_classification_results(true_tokens, predicted_tokens)
