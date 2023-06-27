# Author: Ty Andrews
# Date: June 23 2023

import os
import sys

import pytest
import pandas as pd
from collections import namedtuple

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


from src.entity_extraction.ner_eval import (
    Evaluator,
    collect_named_entities,
    compute_metrics,
)


@pytest.fixture
def sample_correct_labels():
    true_labels = ["B-TAXA", "I-TAXA", "O", "O", "B-GEOG", "O", "O", "B-SITE"]
    predicted_labels = ["B-TAXA", "I-TAXA", "O", "O", "B-GEOG", "O", "O", "B-SITE"]
    tags = ["AGE", "GEOG", "ALTI", "SITE", "REGION", "TAXA", "EMAIL"]

    return true_labels, predicted_labels, tags


@pytest.fixture
def sample_incorrect_labels():
    # TAXA partial match, correct GEOG, spurious TAXA, partial match with region instead of site
    true_labels = ["B-TAXA", "I-TAXA", "O", "O", "B-GEOG", "O", "O", "B-SITE"]
    predicted_labels = ["O", "B-TAXA", "O", "O", "B-GEOG", "O", "B-TAXA", "B-REGION"]
    tags = ["AGE", "GEOG", "ALTI", "SITE", "REGION", "TAXA", "EMAIL"]

    return true_labels, predicted_labels, tags


Entity = namedtuple("Entity", "e_type start_offset end_offset")


@pytest.fixture
def sample_entities():
    true_data = [
        Entity("PERSON", 0, 1),
        Entity("LOCATION", 2, 4),
        Entity("ORGANIZATION", 5, 6),
    ]
    pred_data = [
        Entity("PERSON", 0, 1),
        Entity("LOCATION", 2, 3),
        Entity("ORGANIZATION", 7, 8),
    ]
    tags = ["PERSON", "LOCATION", "ORGANIZATION"]
    return true_data, pred_data, tags


def test_collect_named_entities():
    tokens = ["O", "B-PERSON", "I-PERSON", "O", "O", "B-LOCATION", "I-LOCATION", "O"]
    expected_entities = [Entity("PERSON", 1, 2), Entity("LOCATION", 5, 6)]
    entities = collect_named_entities(tokens)

    assert len(entities) == len(expected_entities)
    for i in range(len(entities)):
        assert entities[i].e_type == expected_entities[i].e_type
        assert entities[i].start_offset == expected_entities[i].start_offset
        assert entities[i].end_offset == expected_entities[i].end_offset


def test_compute_metrics(sample_entities):
    true_data, pred_data, tags = sample_entities

    print(true_data, pred_data)
    evaluation, evaluation_agg_entities_type = compute_metrics(
        true_data, pred_data, tags
    )

    assert evaluation["strict"]["correct"] == 1
    assert evaluation["ent_type"]["correct"] == 2
    assert evaluation["partial"]["correct"] == 1
    assert evaluation["exact"]["correct"] == 1

    assert evaluation_agg_entities_type["PERSON"]["strict"]["correct"] == 1
    assert evaluation_agg_entities_type["LOCATION"]["ent_type"]["correct"] == 1
    assert evaluation_agg_entities_type["PERSON"]["exact"]["correct"] == 1


def test_evaluate(sample_correct_labels):
    true_labels, pred_labels, tags = sample_correct_labels
    evaluator = Evaluator([true_labels], [pred_labels], tags)
    results, evaluation_agg_entities_type = evaluator.evaluate()

    assert results["strict"]["correct"] == 3
    assert results["ent_type"]["correct"] == 3
    assert results["partial"]["correct"] == 3
    assert results["exact"]["correct"] == 3

    assert evaluation_agg_entities_type["TAXA"]["strict"]["correct"] == 1
    assert evaluation_agg_entities_type["GEOG"]["ent_type"]["correct"] == 1
    assert evaluation_agg_entities_type["SITE"]["exact"]["correct"] == 1
