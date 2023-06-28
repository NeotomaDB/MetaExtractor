# Author Kelly Wu
# June 26 2023

import os
import sys
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
import warnings

import shutil
from pathlib import Path


# ensure that the parent directory is on the path for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
script_dir = os.path.join(parent_dir, "src", "article_relevance")

sys.path.append(script_dir)

from relevance_prediction_parquet import (crossref_extract, 
                                              data_preprocessing, 
                                              add_embeddings, 
                                              relevance_prediction)

# Locate test files
@pytest.fixture(autouse=True)
def setup_test_data(tmp_path):
    # Path to the test data folder in your local environment
    local_test_data_path = Path(__file__).resolve().parent / 'test_data'

    # Copy the test data files to the temporary directory
    shutil.copytree(local_test_data_path, tmp_path / 'test_data')


def test_crossref_extract(tmp_path):
    
    # Test if result match with sample file
    doi_file_path = tmp_path / 'test_data' / 'gdd_api_return_forpredictiontest.json'
    generated_file_path = tmp_path / 'test_data' / 'crossref_generated.csv'
    reference_file_path = tmp_path / 'test_data' / 'crossref_validfile.csv'

    crossref_extract(doi_file_path).to_csv(generated_file_path)

    output_df = pd.read_csv(generated_file_path, index_col=0)
    expected_df = pd.read_csv(reference_file_path, index_col=0)

    assert output_df.shape == expected_df.shape
    # write a test to compare two series to check if they are equal
    assert_series_equal(
        output_df['gddid'], 
        expected_df['gddid'],
        check_index_type=False,
        check_dtype=False
    ) 


def test_data_preprocessing(tmp_path):

    # Ignore all DeprecationWarnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Test if result match with sample file
        doi_file_path = tmp_path / 'test_data' / 'gdd_api_return_forpredictiontest.json'
        input_df = crossref_extract(doi_file_path)
        generated_file_path = tmp_path / 'test_data' / 'preprocess_generated.csv'
        reference_file_path = tmp_path / 'test_data' / 'preprocess_validfile.csv'

        data_preprocessing(input_df).to_csv(generated_file_path)

        output_df = pd.read_csv(generated_file_path, index_col=0)
        expected_df = pd.read_csv(reference_file_path, index_col=0)
        
        assert output_df.shape == expected_df.shape


def test_add_embeddings(tmp_path):
    
    input_file_path = tmp_path / 'test_data' / 'preprocess_validfile.csv'

    # Test if result match with sample file
    input_df = pd.read_csv(input_file_path, index_col=0)
    output_df = add_embeddings(input_df, 'text_with_abstract', model='allenai/specter2')
    
    ref_file_path = tmp_path / 'test_data' / 'addembedding_validfile.csv'

    expected_df = pd.read_csv(ref_file_path, index_col=0)
    assert_frame_equal(output_df, expected_df, check_dtype=False, atol=0.01)