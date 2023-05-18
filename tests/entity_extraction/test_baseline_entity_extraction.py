# Author: Ty Andrews, Jenit Jain
# Date: May 11, 2023

import os
import sys

import pytest

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.baseline_entity_extraction import (
    extract_geographic_coordinates,
    extract_region_names,
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
                "1234 ka BP",
                "1234 a BP",
                "1234 Ma BP",
                "1234 kyr BP",
                "1234 cal yr BP",
                "1234 YBP",
                "1234 14C BP",
            ],
            [
                [{"start": 0, "end": 7, "labels": ["AGE"], "text": "1234 BP"}],
                [{"start": 0, "end": 10, "labels": ["AGE"], "text": "1234 Ma BP"}],
                [{"start": 0, "end": 15, "labels": ["AGE"], "text": "1234 to 1235 BP"}],
                [{"start": 0, "end": 14, "labels": ["AGE"], "text": "1234 - 1235 BP"}],
                [{"start": 0, "end": 15, "labels": ["AGE"], "text": "1234 -- 1235 BP"}],
                [
                    {"start": 0, "end": 7, "labels": ["AGE"], "text": "1234 BP"},
                    {
                        "start": 12,
                        "end": 25,
                        "labels": ["AGE"],
                        "text": "456 to 789 BP",
                    },
                ],
                [
                    {"start": 0, "end": 7, "labels": ["AGE"], "text": "1234 BP"},
                    {
                        "start": 12,
                        "end": 28,
                        "labels": ["AGE"],
                        "text": "456 to 789 Ma BP",
                    },
                ],
                [{"start": 0, "end": 10, "labels": ["AGE"], "text": "1234 ka BP"}],
                [{"start": 0, "end": 9, "labels": ["AGE"], "text": "1234 a BP"}],
                [{"start": 0, "end": 10, "labels": ["AGE"], "text": "1234 Ma BP"}],
                [{"start": 0, "end": 11, "labels": ["AGE"], "text": "1234 kyr BP"}],
                [{"start": 0, "end": 14, "labels": ["AGE"], "text": "1234 cal yr BP"}],
                [{"start": 0, "end": 8, "labels": ["AGE"], "text": "1234 YBP"}],
                [{"start": 0, "end": 11, "labels": ["AGE"], "text": "1234 14C BP"}],
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
                "120m elevation",
                "120 m elevation",
            ],
            [
                [
                    {
                        "start": 0,
                        "end": 20,
                        "labels": ["ALTI"],
                        "text": "120m above sea level",
                    }
                ],
                [{"start": 0, "end": 11, "labels": ["ALTI"], "text": "120m a.s.l."}],
                [
                    {
                        "start": 0,
                        "end": 21,
                        "labels": ["ALTI"],
                        "text": "120 m above sea level",
                    }
                ],
                [{"start": 0, "end": 12, "labels": ["ALTI"], "text": "120 m a.s.l."}],
                [{"start": 0, "end": 8, "labels": ["ALTI"], "text": "120m asl"}],
                [{"start": 0, "end": 9, "labels": ["ALTI"], "text": "120 m asl"}],
                [
                    {
                        "start": 13,
                        "end": 33,
                        "labels": ["ALTI"],
                        "text": "120m above sea level",
                    }
                ],
                [{"start": 13, "end": 24, "labels": ["ALTI"], "text": "120m a.s.l."}],
                [
                    {
                        "start": 13,
                        "end": 34,
                        "labels": ["ALTI"],
                        "text": "120 m above sea level",
                    }
                ],
                [{"start": 13, "end": 25, "labels": ["ALTI"], "text": "120 m a.s.l."}],
                [
                    {"start": 15, "end": 23, "labels": ["ALTI"], "text": "120m asl"},
                    {"start": 43, "end": 52, "labels": ["ALTI"], "text": "300 m asl"},
                ],
                [{"start": 0, "end": 14, "labels": ["ALTI"], "text": "120m elevation"}],
                [
                    {
                        "start": 0,
                        "end": 15,
                        "labels": ["ALTI"],
                        "text": "120 m elevation",
                    }
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
                        "labels": ["EMAIL"],
                        "text": "ty.elgin.andrews@gmail.com",
                    }
                ],
                [
                    {
                        "start": 0,
                        "end": 18,
                        "labels": ["EMAIL"],
                        "text": "john.smith@aol.com",
                    }
                ],
                [
                    {
                        "start": 0,
                        "end": 23,
                        "labels": ["EMAIL"],
                        "text": "andrews9@student.ubc.ca",
                    }
                ],
                [
                    {
                        "start": 19,
                        "end": 40,
                        "labels": ["EMAIL"],
                        "text": "carina.hoorn@milne.cc",
                    },
                    {
                        "start": 54,
                        "end": 79,
                        "labels": ["EMAIL"],
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

@pytest.mark.parametrize(
    "test_sentences, expected_results",
    [
        (
            [
                "40:26:46.302N",
                "079:58:55.903W",
                "40°26′46″N",
                "40d 26′ 46″ N",
                "N40:26:46.302",
                "N40°26′46″",
                "N40d 26′ 46″",
                "52°05.75′ N",
                "10°50'E",
            ],
            [
                [{'start': 0, 'end': 13, 'labels': ['GEOG'], 'text': '40:26:46.302N'}],
                [{'start': 0, 'end': 14, 'labels': ['GEOG'], 'text': '079:58:55.903W'}],
                [{'start': 0, 'end': 10, 'labels': ['GEOG'], 'text': '40°26′46″N'}],
                [{'start': 0, 'end': 13, 'labels': ['GEOG'], 'text': '40d 26′ 46″ N'}],
                [{'start': 0, 'end': 13, 'labels': ['GEOG'], 'text': 'N40:26:46.302'}],
                [{'start': 0, 'end': 10, 'labels': ['GEOG'], 'text': 'N40°26′46″'}],
                [{'start': 0, 'end': 12, 'labels': ['GEOG'], 'text': 'N40d 26′ 46″'}],
                [{'start': 0, 'end': 11, 'labels': ['GEOG'], 'text': '52°05.75′ N'}],
                [{'start': 0, 'end': 7, 'labels': ['GEOG'], 'text': "10°50'E"}]
            ],
        )
    ],
)
def test_extract_geographic_coordinates(test_sentences, expected_results):
    """
    Tests the extract_geographic_coordinates function.
    """

    for test_sentence, expected_result in zip(test_sentences, expected_results):
        assert extract_geographic_coordinates(test_sentence) == expected_result

@pytest.mark.parametrize(
    "test_sentences, expected_results",
    [
        (
            [
                "Its relevance to northwestern Europe in the Late Quaternary Period ( H. NICHOLS -)231 Chronology of Postglacial pollen profiles in the Pacific Northwest ( U.S.A. )",
                "The scenery around Garibaldi lake is pristine",
                "This movie was shot in the old towns of Europe",
                "Philosophical Transactions of and tbe pollen record in the British Isles, In : Birks HH, Birks HJb, Kaland PE, Moe D, eds.",
                "Holocene fluctuations of cold climate in the Swiss Alps ( H. ZOLLER -)"
            ],
            [
                [{'start': 30, 'end': 36, 'labels': ['REGION'], 'text': 'Europe'}, {'start': 131, 'end': 152, 'labels': ['REGION'], 'text': 'the Pacific Northwest'}],
                [{'start': 19, 'end': 33, 'labels': ['REGION'], 'text': 'Garibaldi lake'}],
                [{'start': 40, 'end': 46, 'labels': ['REGION'], 'text': 'Europe'}],
                [{'start': 55, 'end': 72, 'labels': ['REGION'], 'text': 'the British Isles'}],
                [{'start': 41, 'end': 55, 'labels': ['REGION'], 'text': 'the Swiss Alps'}]
            ],
        )
    ],
)
def test_extract_region_names(test_sentences, expected_results):
    """
    Tests the extract_region_names function.
    """

    for test_sentence, expected_result in zip(test_sentences, expected_results):
        assert extract_region_names(test_sentence) == expected_result

@pytest.mark.parametrize(
    "test_sentences, expected_results",
    [
        (
            [
                "Percentage calculation is based on the terrestrial pollen sum from which Betula was excluded KM/1 KM/2 KM/3 NM/1 NM/2 NM/3 NM/4 NM/5 NM/6 NM/7 NM/8",
                "The palaeoecology of an Early Neolithic waterlogged site in northwestern England ( F. OLovmLo -)A pollen-analytical study of cores from the Outer Silver Pit", #False positive
                "Description Salix 0.57 1.76 0.73 13.3 1.67 8.78 1.50 2.88 Solanum dulcamara 0 0 0.73 0 0 1.58 0 0 Lysimachia vulgaris 0 0 4.90 0 0.84 0.53 0 0 Mentha-type 00 0 1.04 0 0 00 Lemna 00 0 7.44 0 1.58 0 0",
                "The first major impacts upon the vegetation record become eident from about 3610 BP with sharp reductions in arboreal taxa, the appearance of cerealtype pollen in L.A.BI, and marked increases in Calluna, Foaceae and Cyperaceae.",
                "The overlying Sphagnum peat is devoid of clastic elements for a short period during which sediment inorganic content declines.",
                "Abstract ) ( A. T. CROSS, G. G. THOMPSON and J. B. ZAITZEFF ) 3 - 1 1 Gymnospermae, general The gymnospermous affinity of Eucommiidites ERDTMAN, 1948"
            ],
            [
                [{'start': 73, 'end': 79, 'labels': ['TAXA'], 'text': 'Betula'}],
                [{'start': 146, 'end': 152, 'labels': ['TAXA'], 'text': 'Silver'}], # False positive
                [
                    {'start': 12, 'end': 17, 'labels': ['TAXA'], 'text': 'Salix'}, 
                    {'start': 58, 'end': 75, 'labels': ['TAXA'], 'text': 'Solanum dulcamara'},
                    {'start': 98, 'end': 117, 'labels': ['TAXA'], 'text': 'Lysimachia vulgaris'}, 
                    {'start': 143, 'end': 154, 'labels': ['TAXA'], 'text': 'Mentha-type'},
                    {'start': 143, 'end': 149, 'labels': ['TAXA'], 'text': 'Mentha'}, 
                    {'start': 172, 'end': 177, 'labels': ['TAXA'], 'text': 'Lemna'}],
                [
                    {'start': 195, 'end': 202, 'labels': ['TAXA'], 'text': 'Calluna'}, 
                    {'start': 216, 'end': 226, 'labels': ['TAXA'], 'text': 'Cyperaceae'}],
                [{'start': 14, 'end': 22, 'labels': ['TAXA'], 'text': 'Sphagnum'}],
                [{'start': 70, 'end': 81, 'labels': ['TAXA'], 'text': 'Gymnosperma'}]
            ],
        )
    ],
)
def test_extract_taxa(test_sentences, expected_results):
    """
    Tests the extract_taxa function.
    """

    for test_sentence, expected_result in zip(test_sentences, expected_results):
        assert extract_taxa(test_sentence, os.path.join("data", "raw", "taxa.csv")) == expected_result
