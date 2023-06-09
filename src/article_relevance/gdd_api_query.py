# Author Kelly Wu
# 2023-06-07

# GDD Recent Article Query
# Input: parameters to specify article range
# output: JSON containing article gddid, doi, url, and other metadata about the query process

"""This script takes in user specified parameter values and query the GDD API for recently acquired articles. 

Usage: gdd_api_query.py --doi_path=<doi_path> [--n_recent=<n_recent>] [--min_date=<min_date>] [--max_date=<max_date>]

Options:
    --doi_path=<doi_path>                   The path to where the DOI list JSON file should be stored.
    --n_recent=<n_recent>                   If specified, n most recent articles will be returned. Default is None.
    --min_date=<min_date>                   Query by date. Articles acquired since this date will be returned. Default is None.
    --max_date=<max_date>                   Query by date. Articles acquired before this date will be returned. Default is None.
"""

import requests
import json
import os
import numpy as np
import pandas as pd
import re
from docopt import docopt
import logging

# Locate src module
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)
src_dir = os.path.dirname(current_dir)
print(src_dir)
sys.path.append(src_dir)

from logs import get_logger

logger = get_logger(__name__) # this gets the object with the current modules name

def get_new_gdd_articles(output_path, n_recent_articles = None, min_date = None, max_date = None):
    """ 
    Get newly acquired articles from min_date to (optional) max_date. 
    Or get the most recent new articles added to GeoDeepDive.
    Return API resuls as a list of article metadata information.

    Args:
        output_path (str)
        n_recent_articles (int)
        min_date
        max_date

        doi_path (str): Path to the doi list csv file.
        doi_col (str): Column name of DOI.
    
    Return:
        pandas Dataframe containing CrossRef metadata.

    Example:
        get_new_gdd_articles(min_date='2023-06-07')
        get_new_gdd_articles(min_date='2023-06-01', max_date = '2023-06-08')
        get_new_gdd_articles(n_recent_articles = 1000)

    """

    # ======== Tests for input data type ==========
    if (n_recent_articles is None) and (min_date is None and max_date is None):
            raise ValueError("Either n_recent_articles or a date range should be specified.")
    
    if (n_recent_articles is not None) and (min_date is not None or max_date is not None):
            raise ValueError("Only one of n_recent_articles or a date range should be specified.")
    
    if (n_recent_articles is None) and (min_date is not None or max_date is not None):
            pattern = r'^\d{4}-\d{2}-\d{2}$'
    
            if min_date is not None:
                if not isinstance(min_date, str):
                     raise ValueError("min_date should be a string. min_date should be a string with format 'yyyy-mm-dd'.")
                if re.match(pattern, min_date) is False:
                     raise ValueError("min_date does not follow the correct format. min_date should be a string with format 'yyyy-mm-dd'.")
            
            if max_date is not None:
                if not isinstance(max_date, str):
                     raise ValueError("min_date should be a string. min_date should be a string with format 'yyyy-mm-dd'.")
                if re.match(pattern, max_date) is False:
                     raise ValueError("min_date does not follow the correct format. min_date should be a string with format 'yyyy-mm-dd'.")
            
    if (n_recent_articles is not None) and (min_date is None and max_date is None):
         if not isinstance(n_recent_articles, int):
                raise ValueError("n_recent_articles should be an integer.")
            
    # ========== Query API by n most recent article ==========
    if n_recent_articles is not None:
        api_call = "https://geodeepdive.org/api/articles?recent" + f"&max={n_recent_articles}"

    # Query API by date range
    elif (min_date is not None) and (max_date is not None):
        api_call = f"https://xdd.wisc.edu/api/articles?min_acquired={min_date}&max_acquired={max_date}&full_results=true"
    
    elif (min_date is not None) and (max_date is None):
        api_call = f"https://xdd.wisc.edu/api/articles?min_acquired={min_date}&full_results=true"

    elif (min_date is None) and (max_date is not None):
        api_call = f"https://xdd.wisc.edu/api/articles?max_acquired={max_date}&full_results=true"
    
    else:
        raise ValueError("Please check input parameter values.")


    # =========== Format the API return to Json file ==========
    response = requests.get(api_call).json()

    data = response['success']['data']

    logger.info(f'{data.shape[0]} returned from GeoDeepDive.')


    # initialize the resulting dataframe
    gdd_df = pd.DataFrame()

    for article in data:
        one_article_dict = {}
        one_article_dict['gddid'] = [article['_gddid']]

        if article['identifier'][0]['type'] == 'doi':
            one_article_dict['DOI'] = [article['identifier'][0]['id']]
        else: 
            one_article_dict['DOI'] = ['Non-DOI Article ID type']
        
        one_article_dict['url'] = [article['link'][0]['url']]
        one_article_dict['status'] = 'queried'

        one_article = pd.DataFrame(one_article_dict)
        gdd_df = pd.concat([gdd_df, one_article])
    
    gdd_df = gdd_df.reset_index(drop=True)

    result_dict = {}
    result_dict['n_returned_article'] = gdd_df.shape[0]
    result_dict['param_min_date'] = min_date
    result_dict['param_max_date'] = max_date
    result_dict['param_n_recent_articles'] = n_recent_articles
    result_dict['data'] = gdd_df.to_dict()

    # Write the JSON object to a file
    directory = os.path.join(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(output_path + '/gdd_api_return.json', "w") as file:
        json.dump(result_dict, file)


def main():
    opt = docopt(__doc__)
    doi_file_storage = opt["--doi_path"]
    param_n_recent = opt["--n_recent"]
    param_min_date = opt["--min_date"]
    param_max_date = opt["--max_date"]

    get_new_gdd_articles(output_path = doi_file_storage, 
                         min_date = param_min_date, 
                         max_date = param_max_date, 
                         n_recent_articles= param_n_recent)
    

if __name__ == "__main__":
    main()
