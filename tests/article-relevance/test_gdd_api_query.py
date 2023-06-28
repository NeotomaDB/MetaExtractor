# Author Kelly Wu
# June 26 2023

import os
import sys
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
import warnings
import json


# ensure that the parent directory is on the path for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
script_dir = os.path.join(parent_dir, "src", "article_relevance")

sys.path.append(script_dir)

from gdd_api_query import get_new_gdd_articles

def test_get_new_gdd_articles():
    json_path = 'test_data/gdd_api_return.json'

    # ======= Test 1: n_recent
    get_new_gdd_articles(output_path = 'test_data', 
                         parquet_path = '',
                         min_date = '', 
                         max_date = '', 
                         n_recent_articles= 10,
                         term = None,
                         auto_check_dup = 'False'
                         )
    
    with open(json_path) as json_file:
        data_dictionary = json.load(json_file)

    df = pd.DataFrame(data_dictionary['data'])
    assert df.shape[0] == 10

    # ======== Test 2: day range
    get_new_gdd_articles(output_path = 'test_data', 
                         parquet_path = '',
                         min_date = '2023-01-01', 
                         max_date = '2023-01-02', 
                         n_recent_articles= None,
                         term = None,
                         auto_check_dup = 'False'
                         )
    
    with open(json_path) as json_file:
        data_dictionary = json.load(json_file)

    df = pd.DataFrame(data_dictionary['data'])
    assert df.shape[0] == 4130

    # ======== Test 3: day range + term
    get_new_gdd_articles(output_path = 'test_data', 
                         parquet_path = '',
                         min_date = '2023-01-01', 
                         max_date = '2023-01-02', 
                         n_recent_articles= None,
                         term = 'gene',
                         auto_check_dup = 'False'
                         )
    
    with open(json_path) as json_file:
        data_dictionary = json.load(json_file)

    df = pd.DataFrame(data_dictionary['data'])
    assert df.shape[0] == 26





    
   