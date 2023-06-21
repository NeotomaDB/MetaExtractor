# Author: Ty Andrews
# Date: 2023-06-08

import os
import sys

import pandas as pd
import pytest
from distutils import dir_util

# ensure that the src directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.pipeline.entity_extraction_pipeline import (
    load_relevant_articles,
    load_article_text_data,
    extract_entities,
    post_process_extracted_entities,
    combine_sentence_data,
    recreate_original_sentences_with_labels,
)

from src.entity_extraction.hf_entity_extraction import load_ner_model_pipeline


# create test input_data
@pytest.fixture
def input_data():
    test_text_df = pd.DataFrame(
        {
            "gddid": ["gdd1", "gdd1", "gdd1"],
            "sentid": [1, 2, 3],
            "text": [
                "This sentence contains an age 1234 BP.",
                "This contains taxa Pinaceae.",
                "This is a region in North America.",
            ],
            "word_count": [7, 4, 7],
            "text_length": [38, 28, 33],
            "section_name": ["Introduction", "Background", "Results"],
        }
    )

    return test_text_df


@pytest.fixture
def raw_extracted_entities():
    extracted_df = pd.DataFrame(
        {
            "sentid_list": [[1, 2, 3]],
            "section_name_list": [["Introduction", "Background", "Results"]],
            "text": [
                "This sentence contains an age 1234 BP. This contains taxa Pinaceae. This is a region in North America."
            ],
            "word_count_list": [[7, 4, 7]],
            "text_length_list": [[38, 28, 33]],
            "total_word_count": [18],
            "gddid": ["gdd1"],
            "model_name": ["roberta-finetuned-v3"],
            "AGE": [
                [
                    {
                        "word": " 1234 BP",
                        "start": 30,
                        "end": 37,
                        "labels": ["AGE"],
                        "score": 1.0,
                    }
                ]
            ],
            "TAXA": [
                [
                    {
                        "word": " Pinaceae",
                        "start": 58,
                        "end": 66,
                        "labels": ["TAXA"],
                        "score": 1.0,
                    }
                ]
            ],
            "REGION": [
                [
                    {
                        "word": " North America",
                        "start": 88,
                        "end": 101,
                        "labels": ["REGION"],
                        "score": 1.0,
                    }
                ]
            ],
            "GEOG": [[]],
            "ALTI": [[]],
            "EMAIL": [[]],
            "SITE": [[]],
        }
    )

    return extracted_df


# create test output_data
@pytest.fixture
def output_data():
    test_results_df = pd.DataFrame(
        {
            "sentid": [1, 2, 3],
            "text": [
                "This sentence contains an age 1234 BP.",
                "This contains taxa Pinaceae.",
                "This is a region in North America.",
            ],
            "word_count": [7, 4, 7],
            "text_length": [38, 28, 33],
            "gddid": ["gdd1", "gdd1", "gdd1"],
            "TAXA": [
                [],
                [
                    {
                        "word": " Pinaceae",
                        "start": 19,
                        "end": 27,
                        "labels": ["TAXA"],
                        "score": 1.0,
                        "section_name": "Background",
                    }
                ],
                [],
            ],
            "REGION": [
                [],
                [],
                [
                    {
                        "word": " North America",
                        "start": 20,
                        "end": 33,
                        "labels": ["REGION"],
                        "score": 1.0,
                        "section_name": "Results",
                    }
                ],
            ],
            "AGE": [
                [
                    {
                        "word": " 1234 BP",
                        "start": 30,
                        "end": 37,
                        "labels": ["AGE"],
                        "score": 1.0,
                        "section_name": "Introduction",
                    }
                ],
                [],
                [],
            ],
            "GEOG": [[], [], []],
            "ALTI": [[], [], []],
            "EMAIL": [[], [], []],
            "SITE": [[], [], []],
        }
    )

    return test_results_df


# testing setup inspiration from: https://stackoverflow.com/questions/29627341/pytest-where-to-store-expected-data
@pytest.fixture
def gdd_data_dir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


def test_load_article_text_data(gdd_data_dir):
    data_path = os.path.join(str(gdd_data_dir), "test_gdd_text")

    article_text_df = load_article_text_data(data_path)

    # ensure it has the correct columns gddid, sentid, text, word_count, text_length
    assert "gddid" in article_text_df.columns
    assert "sentid" in article_text_df.columns
    assert "text" in article_text_df.columns
    assert "word_count" in article_text_df.columns
    assert "text_length" in article_text_df.columns
    assert "section_name" in article_text_df.columns

    # ensure section_name has non null values
    assert article_text_df["section_name"].isnull().sum() == 0


# combine_sentence_data function which should return a df a words column thats
# a string thats the same length as the input_df text column lengths plus a space
# between each word
def test_combine_sentence_data(input_data):
    test_results_df = combine_sentence_data(input_data)

    assert (
        test_results_df["text"][0]
        == "This sentence contains an age 1234 BP. This contains taxa Pinaceae. This is a region in North America."
    )


# test that minimum word length each sentence is kept in it's own row
def test_combine_sentence_data_max_word_length(input_data):
    test_results_df = combine_sentence_data(input_data, max_word_length=1)

    assert len(test_results_df) == 3

    # first example is 7 words, second is 4, this should make a total of 2 rows
    test_results_df = combine_sentence_data(input_data, max_word_length=12)

    assert len(test_results_df) == 2


# test that data is combined then recreated correctly
def test_combine_sentence_data_recreate(raw_extracted_entities, input_data):
    recreated_df = recreate_original_sentences_with_labels(
        raw_extracted_entities.iloc[0]
    )
    # TODO: make test independent of order of rows by using sentid comparison
    assert recreated_df["text"].iloc[0] == input_data["text"].iloc[0]
    assert recreated_df["text"].iloc[1] == input_data["text"].iloc[1]
    assert recreated_df["text"].iloc[2] == input_data["text"].iloc[2]

    assert recreated_df["sentid"].iloc[0] == input_data["sentid"].iloc[0]
    assert recreated_df["sentid"].iloc[1] == input_data["sentid"].iloc[1]
    assert recreated_df["sentid"].iloc[2] == input_data["sentid"].iloc[2]

    assert recreated_df["gddid"].iloc[0] == input_data["gddid"].iloc[0]
    assert recreated_df["gddid"].iloc[1] == input_data["gddid"].iloc[1]
    assert recreated_df["gddid"].iloc[2] == input_data["gddid"].iloc[2]


# test that data is combined then recreated correctly
def test_post_process_extracted_entities(raw_extracted_entities, output_data):
    postprocessed_df = post_process_extracted_entities(raw_extracted_entities)

    assert postprocessed_df["AGE"].iloc[0] == output_data["AGE"].iloc[0]
    assert postprocessed_df["TAXA"].iloc[1] == output_data["TAXA"].iloc[1]
    assert postprocessed_df["REGION"].iloc[2] == output_data["REGION"].iloc[2]
