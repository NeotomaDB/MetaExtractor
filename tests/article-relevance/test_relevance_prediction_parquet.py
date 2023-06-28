# Author Kelly Wu
# June 26 2023

import os
import sys
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
import warnings



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
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_crossref_extract():
    
    # Test if result match with sample file
    doi_file_path = "test_data/gdd_api_return_forpredictiontest.json"
    crossref_extract(doi_file_path).to_csv('test_data/crossref_generated.csv')

    output_df = pd.read_csv('test_data/crossref_generated.csv', index_col=0)
    expected_df = pd.read_csv('test_data/crossref_validfile.csv', index_col=0)

    assert_frame_equal(output_df, expected_df, check_dtype=False)

    # Delete the temp file
    file_path = 'test_data/crossref_generated.csv'
    os.remove(file_path)


def test_data_preprocessing():

    # Ignore all DeprecationWarnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)


        # Test if result match with sample file
        doi_file_path = "test_data/gdd_api_return_forpredictiontest.json"
        input_df = crossref_extract(doi_file_path)
        data_preprocessing(input_df).to_csv('test_data/preprocess_generated.csv')

        output_df = pd.read_csv('test_data/preprocess_generated.csv', index_col=0)
        expected_df = pd.read_csv('test_data/preprocess_validfile.csv', index_col=0)
        assert_frame_equal(output_df, expected_df, check_dtype=False)
    
    # Delete the temp file
    file_path = 'test_data/preprocess_generated.csv'
    os.remove(file_path)

def test_add_embeddings():

    # Test if result match with sample file
    input_df = pd.read_csv('test_data/preprocess_validfile.csv', index_col=0)
    output_df = add_embeddings(input_df, 'text_with_abstract', model='allenai/specter2')

    expected_df = pd.read_csv('test_data/addembedding_validfile.csv', index_col=0)
    assert_frame_equal(output_df, expected_df, check_dtype=False)


def test_relevance_prediction():

    # Test if result match with sample file
    input_df = pd.read_csv('test_data/addembedding_validfile.csv', index_col=0)
    model_path = "test_data/logistic_regression_model.joblib"
    output_df = relevance_prediction(input_df, model_path, predict_thld=0.5)

    expected_df = pd.read_csv('test_data/predicted_validfile.csv', index_col=0)
    assert_frame_equal(output_df, expected_df, check_dtype=False)