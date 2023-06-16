# Author Kelly Wu
# 2023-06-07

# GDD Recent Article Query
# Input: parameters to specify article range
# output: JSON containing article gddid, doi, url, and other metadata about the query process

"""This script takes in user specified parameter values and query the GDD API for recently acquired articles. 

Usage: gdd_api_query.py --doi_path=<doi_path> [--n_recent=<n_recent>] [--min_date=<min_date>] [--max_date=<max_date>] [--term=<term>]

Options:
    --doi_path=<doi_path>                   The path to where the DOI list JSON file should be stored.
    --n_recent=<n_recent>                   If specified, n most recent articles will be returned. Default is None.
    --min_date=<min_date>                   Query by date. Articles acquired since this date will be returned. Default is None.
    --max_date=<max_date>                   Query by date. Articles acquired before this date will be returned. Default is None.
    --term=<term>                           Query by term. Default is None.
"""

import requests
import json
import os
import numpy as np
import pandas as pd
import re
from docopt import docopt
import logging
import sys
import pyarrow as pa
import pyarrow.parquet as pq
import datetime


# Locate src module
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)
src_dir = os.path.dirname(current_dir)
print(src_dir)
sys.path.append(src_dir)

from logs import get_logger

logger = get_logger(__name__) # this gets the object with the current modules name

def get_new_gdd_articles(output_path, 
                         n_recent_articles = None, 
                         min_date = None, 
                         max_date = None, 
                         term = None):
    """ 
    Get newly acquired articles from min_date to (optional) max_date. 
    Or get the most recent new articles added to GeoDeepDive.
    Return API resuls as a list of article metadata information.

    Args:
        output_path (str)       The path where the output JSON file is saved to.
        n_recent_articles (int) Number of most recent articles GeoDeepDive acquired.
        min_date (str)          Lower limit of GeoDeepDive acquired date.
        max_date (str)          Upper limit of GeoDeepDive acquired date.
        term (str)              Term to search for.
    
    Return:
        Write JSON output to output_path.

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
            
    # ========== Query API ==========
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
    
    if term is not None:
         api_extend = f"&term={term}"
         api_call += api_extend


    # =========== Format the API return to Json file ==========
    session = requests.Session()
    response = session.get(api_call)

    n_refresh = 0
    while response.status_code != 200 and n_refresh < 10:
        response = requests.get(api_call)
        n_refresh += 1
    
    response_dict = response.json()
    data = response_dict['success']['data']

    i = 1
    logger.info(f'{len(data)} articles queried from GeoDeepDive (page {i}).')

    if 'next_page' in response_dict['success'].keys():

        next_page = response_dict['success']['next_page']
        n_refresh = 0

        while (next_page != '') :
            i += 1
            logger.info(f"going to the next page: page{i}")

            next_response = session.get(next_page)
            while next_response.status_code != 200:
                next_response = session.get(next_page)

            next_response_dict = next_response.json()
            new_data = next_response_dict['success']['data']
            logger.info(f'{len(new_data)} articles queried from GeoDeepDive (page {i}).')
            data.extend(new_data)
            
            next_page = next_response_dict['success']['next_page']
            n_refresh += 1

    logger.info(f'GeoDeepDive query completed. Converting to JSON output.')

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

    #JSON output
    result_dict = {}
    result_dict['n_returned_article'] = gdd_df.shape[0]
    result_dict['param_min_date'] = min_date
    result_dict['param_max_date'] = max_date
    result_dict['param_n_recent_articles'] = n_recent_articles
    result_dict['data'] = gdd_df.to_dict()
    logger.info(f'{gdd_df.shape[0]} articles returned from GeoDeepDive.')

    # Write the JSON object to a file
    directory = os.path.join(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(output_path + '/gdd_api_return.json', "w") as file:
        json.dump(result_dict, file)

    # Export Parquet
    # The parquet contains: parameters used when queried, predicted(gddid, DOI, metadata & prediction results)
    gdd_df['n_recent'] = n_recent_articles
    gdd_df['min_date'] = min_date

    if max_date is None:
         current_date = datetime.date.today()
         formatted_date = current_date.strftime("%Y-%m-%d")
         gdd_df['max_date'] = formatted_date
    else:
        gdd_df['max_date'] = max_date

    gdd_df['term'] = term

     # Create a PyArrow table from the DataFrame
    table = pa.Table.from_pandas(gdd_df)
    # Specify the Parquet file path
    parquet_file = output_path + '/gdd_api_return.parquet'
    # Write the table to a Parquet file
    pq.write_table(table, parquet_file)


def main():
    opt = docopt(__doc__)
    doi_file_storage = opt["--doi_path"]
    param_n_recent = opt["--n_recent"]

    if param_n_recent is not None:
        param_n_recent = int(opt["--n_recent"])

    param_min_date = opt["--min_date"]
    param_max_date = opt["--max_date"]
    param_term = opt["--term"]


    get_new_gdd_articles(output_path = doi_file_storage, 
                         min_date = param_min_date, 
                         max_date = param_max_date, 
                         n_recent_articles= param_n_recent,
                         term = param_term)
    

if __name__ == "__main__":
    main()
