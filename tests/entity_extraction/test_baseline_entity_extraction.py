# Author: Ty Andrews, Jenit Jain
# Date: May 11, 2023

import os
import sys

import pytest

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.baseline_entity_extraction import (
    extract_geographic_coordinates,
    extract_site_names,
    extract_taxa,
    extract_age,
    extract_altitude,
    extract_email,
)


@pytest.mark.parametrize(
    "test_sentences, expected_results",
    [
        (
            [
                "1234 BP",
                "1234 Ma BP",
                "1234 to 1235 BP",
                "1234 - 1235 BP",
                "1234 -- 1235 BP",
                "1234 BP and 456 to 789 BP",
                "1234 BP and 456 to 789 Ma BP",
            ],
            [
                [{"start": 0, "end": 7, "label": ["AGE"], "text": "1234 BP"}],
                [{"start": 0, "end": 10, "label": ["AGE"], "text": "1234 Ma BP"}],
                [{"start": 0, "end": 15, "label": ["AGE"], "text": "1234 to 1235 BP"}],
                [{"start": 0, "end": 14, "label": ["AGE"], "text": "1234 - 1235 BP"}],
                [{"start": 0, "end": 15, "label": ["AGE"], "text": "1234 -- 1235 BP"}],
                [
                    {"start": 0, "end": 7, "label": ["AGE"], "text": "1234 BP"},
                    {"start": 12, "end": 25, "label": ["AGE"], "text": "456 to 789 BP"},
                ],
                [
                    {"start": 0, "end": 7, "label": ["AGE"], "text": "1234 BP"},
                    {
                        "start": 12,
                        "end": 28,
                        "label": ["AGE"],
                        "text": "456 to 789 Ma BP",
                    },
                ],
            ],
        )
    ],
)
def test_extract_age(test_sentences, expected_results):
    """
    Tests the extract_age function.
    """

    for test_sentence, expected_result in zip(test_sentences, expected_results):
        assert extract_age(test_sentence) == expected_result


@pytest.mark.parametrize(
    "test_sentences, expected_results",
    [
        (
            [
                "120m above sea level",
                "120m a.s.l.",
                "120 m above sea level",
                "120 m a.s.l.",
                "120m asl",
                "120 m asl",
                "The site was 120m above sea level",
                "The site was 120m a.s.l.",
                "The site was 120 m above sea level",
                "The site was 120 m a.s.l.",
                "First site was 120m asl and the second was 300 m asl",
            ],
            [
                [
                    {
                        "start": 0,
                        "end": 20,
                        "label": ["ALTI"],
                        "text": "120m above sea level",
                    }
                ],
                [{"start": 0, "end": 11, "label": ["ALTI"], "text": "120m a.s.l."}],
                [
                    {
                        "start": 0,
                        "end": 21,
                        "label": ["ALTI"],
                        "text": "120 m above sea level",
                    }
                ],
                [{"start": 0, "end": 12, "label": ["ALTI"], "text": "120 m a.s.l."}],
                [{"start": 0, "end": 8, "label": ["ALTI"], "text": "120m asl"}],
                [{"start": 0, "end": 9, "label": ["ALTI"], "text": "120 m asl"}],
                [
                    {
                        "start": 13,
                        "end": 33,
                        "label": ["ALTI"],
                        "text": "120m above sea level",
                    }
                ],
                [{"start": 13, "end": 24, "label": ["ALTI"], "text": "120m a.s.l."}],
                [
                    {
                        "start": 13,
                        "end": 34,
                        "label": ["ALTI"],
                        "text": "120 m above sea level",
                    }
                ],
                [{"start": 13, "end": 25, "label": ["ALTI"], "text": "120 m a.s.l."}],
                [
                    {"start": 15, "end": 23, "label": ["ALTI"], "text": "120m asl"},
                    {"start": 43, "end": 52, "label": ["ALTI"], "text": "300 m asl"},
                ],
            ],
        )
    ],
)
def test_extract_altitude(test_sentences, expected_results):
    """
    Tests the extract_altitude function.
    """

    for test_sentence, expected_result in zip(test_sentences, expected_results):
        assert extract_altitude(test_sentence) == expected_result


@pytest.mark.parametrize(
    "test_sentences, expected_results",
    [
        (
            [
                "ty.elgin.andrews@gmail.com",
                "john.smith@aol.com",
                "andrews9@student.ubc.ca",
                # from GGD 54b4324ae138239d8684a37b segment 0
                "E-mail addresses : carina.hoorn@milne.cc (C. Hoorn -) mauro.cremaschi@libero.it",
            ],
            [
                [
                    {
                        "start": 0,
                        "end": 26,
                        "label": ["EMAIL"],
                        "text": "ty.elgin.andrews@gmail.com",
                    }
                ],
                [
                    {
                        "start": 0,
                        "end": 18,
                        "label": ["EMAIL"],
                        "text": "john.smith@aol.com",
                    }
                ],
                [
                    {
                        "start": 0,
                        "end": 23,
                        "label": ["EMAIL"],
                        "text": "andrews9@student.ubc.ca",
                    }
                ],
                [
                    {
                        "start": 19,
                        "end": 40,
                        "label": ["EMAIL"],
                        "text": "carina.hoorn@milne.cc",
                    },
                    {
                        "start": 54,
                        "end": 79,
                        "label": ["EMAIL"],
                        "text": "mauro.cremaschi@libero.it",
                    },
                ],
            ],
        )
    ],
)
def test_extract_email(test_sentences, expected_results):
    """
    Tests the extract_email function.
    """

    for test_sentence, expected_result in zip(test_sentences, expected_results):
        assert extract_email(test_sentence) == expected_result
