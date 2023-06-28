# Author: Ty Andrews
# Date: 2023-05-15

import os
import sys

import pytest

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.evaluation.entity_extraction_evaluation import (
    get_token_labels,
    calculate_entity_classification_metrics,
    plot_token_classification_report,
)


@pytest.fixture
def sample_text():
    return "The site was 120m above sea level and 1234 BP and found Pediastrum"


@pytest.fixture
def sample_labelled_entities():
    test_labelled_entities = [
        {"start": 13, "end": 33, "labels": ["ALTI"], "text": "120m above sea level"},
        {"start": 38, "end": 45, "labels": ["AGE"], "text": "1234 BP"},
        {"start": 56, "end": 65, "labels": ["TAXA"], "text": "Pediastrum"},
    ]
    return test_labelled_entities


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


# first test that the correct tokens are labelled as entities and not "O"
def test_get_token_labels(sample_text, sample_labelled_entities):
    expected_non_null_labels = [3, 4, 5, 6, 8, 9, 12]

    split_text, token_labels = get_token_labels(sample_labelled_entities, sample_text)

    for i in expected_non_null_labels:
        assert token_labels[i] != "O"


def test_calculate_entity_classification_metrics_with_correct_input(
    example_correct_tokens,
):
    true_tokens, predicted_tokens = example_correct_tokens

    accuracy, f1, recall, precision = calculate_entity_classification_metrics(
        true_tokens, predicted_tokens, method="tokens"
    )

    # ensure the f1, accuracy, recall and precision are correct to 2 decimal places
    assert round(f1, 2) == 1.0
    assert round(accuracy, 2) == 1.0
    assert round(recall, 2) == 1.0
    assert round(precision, 2) == 1.0

    accuracy, f1, recall, precision = calculate_entity_classification_metrics(
        true_tokens, predicted_tokens, method="entity"
    )
    # ensure the f1, accuracy, recall and precision are correct to 2 decimal places
    assert round(f1, 2) == 1.0
    assert round(accuracy, 2) == 1.0
    assert round(recall, 2) == 1.0
    assert round(precision, 2) == 1.0


def test_calculate_entity_classification_metrics_with_incorrect_input(
    example_incorrect_tokens,
):
    true_tokens, predicted_tokens = example_incorrect_tokens

    accuracy, f1, recall, precision = calculate_entity_classification_metrics(
        true_tokens, predicted_tokens, method="tokens"
    )
    # ensure the f1, accuracy, recall and precision are correct to 2 decimpal places
    assert round(f1, 2) == 0.8
    assert round(accuracy, 2) == 0.75
    assert round(recall, 2) == 0.67
    assert round(precision, 2) == 1.0

    accuracy, f1, recall, precision = calculate_entity_classification_metrics(
        true_tokens, predicted_tokens, method="entity"
    )
    # ensure the f1, accuracy, recall and precision are correct to 2 decimpal places
    assert round(f1, 2) == 0.5
    assert round(accuracy, 2) == 0.5
    assert round(recall, 2) == 0.5
    assert round(precision, 2) == 0.5


def test_plot_classification_report(example_correct_tokens):
    true_tokens, predicted_tokens = example_correct_tokens

    plot = plot_token_classification_report(
        true_tokens, predicted_tokens, title="Test Plot", method="tokens", display=False
    )

    assert plot is not None
    assert plot.axes[0].get_title() == "Test Plot"
