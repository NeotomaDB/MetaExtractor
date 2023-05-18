# Author: Ty Andrews
# Date: 2023-05-15

import os
import sys

import pytest

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.entity_extraction_evaluation import (
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
        {"start": 56, "end": 66, "labels": ["TAXA"], "text": "Pediastrum"},
    ]
    return test_labelled_entities


# first test that the correct tokens are labelled as entities and not "O"
def test_get_token_labels(sample_text, sample_labelled_entities):
    expected_non_null_labels = [3, 4, 5, 6, 8, 9, 12]

    token_labels = get_token_labels(sample_labelled_entities, sample_text)

    for i in expected_non_null_labels:
        assert token_labels[i] != "O"


# test the ideal case of passing in the same labelled tokens and predicted tokens
def test_calculate_entity_classification_metrics(sample_text, sample_labelled_entities):
    sample_token_labels = get_token_labels(sample_labelled_entities, sample_text)

    # test that the accuracy, f1, and recall scores are equal to 1
    accuracy, f1, recall, precision = calculate_entity_classification_metrics(
        sample_token_labels, sample_token_labels, method="tokens"
    )

    assert accuracy == 1
    assert f1 == 1
    assert recall == 1
    assert precision == 1
