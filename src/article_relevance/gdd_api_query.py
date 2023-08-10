# Author Kelly Wu
# 2023-06-07

# GDD Recent Article Query
# Input: parameters to specify article range
# output: JSON containing article gddid, doi, url, and other metadata about the query process

"""This script takes in user specified parameter values and query the GDD API for recently acquired articles.

Usage: gdd_api_query.py --doi_path=<doi_path> --parquet_path=<parquet_path> [--n_recent=<n_recent>] [--min_date=<min_date>] [--max_date=<max_date>] [--term=<term>] [--auto_min_date=<auto_min_date>] [--auto_check_dup=<auto_check_dup>]

Options:
    --doi_path=<doi_path>                   The path to where the DOI list JSON file will be stored.
    --parquet_path=<parquet_path>           The path to the folder that stores the processed parquet files.
    --n_recent=<n_recent>                   If specified, n most recent articles will be returned. Default is None.
    --min_date=<min_date>                   Query by date. Articles acquired since this date will be returned. Default is None.
    --max_date=<max_date>                   Query by date. Articles acquired before this date will be returned. Default is None.
    --term=<term>                           Query by term. Default is None.
    --auto_min_date=<auto_min_date>         Default is false. If true, max_date will be set to the date of last pipeline run.
    --auto_check_dup=<auto_check_dup>       Default is false. If true, articles that have been processed by the pipeline will be removed from this query output.
"""

import requests
import json
import os
import numpy as np
import pandas as pd
import re
from docopt import docopt
import sys
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, date


# Locate src module
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from logs import get_logger

logger = get_logger(__name__) # this gets the object with the current modules name

def get_new_gdd_articles(output_path,
                         parquet_path,
                         n_recent_articles = None,
                         min_date = None,
                         max_date = None,
                         term = None,
                         auto_check_dup = False):
    """
    Get newly acquired articles from min_date to (optional) max_date.
    Or get the most recent new articles added to GeoDeepDive.
    Return API resuls as a list of article metadata information.

    Args:
        output_path (str)       The path to where the output JSON file will be saved to.
        parquet_path (str)      The path to the folder that stores the processed parquet files.
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

    # == convert empty str to None to handle placeholder for docker compose arguments  ==
    if n_recent_articles == '':
        n_recent_articles = None
    if min_date == '':
        min_date = None
    if max_date == '':
        max_date = None
    if term == '':
        term = None

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
        logger.info(f'Querying by n_recent = {n_recent_articles}')
        api_call = "https://geodeepdive.org/api/articles?recent" + f"&max={n_recent_articles}"

    # Query API by date range
    elif (min_date is not None) and (max_date is not None):
        logger.info(f'Querying by min_date = {min_date} and max_date = {max_date}')
        api_call = f"https://xdd.wisc.edu/api/articles?min_acquired={min_date}&max_acquired={max_date}&full_results=true"

    elif (min_date is not None) and (max_date is None):
        logger.info(f'Querying by min_date = {min_date}.')
        api_call = f"https://xdd.wisc.edu/api/articles?min_acquired={min_date}&full_results=true"

    elif (min_date is None) and (max_date is not None):
        logger.info(f'Querying by max_date = {max_date}.')
        api_call = f"https://xdd.wisc.edu/api/articles?max_acquired={max_date}&full_results=true"

    else:
        raise ValueError("Please check input parameter values.")

    if term is not None:
        logger.info(f'Search term = {term}.')
        api_extend = f"&term={term}"
        api_call += api_extend


    # =========== Query xDD API to get data ==========
    logger.info(f'{api_call}')
    session = requests.Session()
    response = session.get(api_call)

    n_refresh = 0
    while response.status_code != 200 and n_refresh < 10:
        response = requests.get(api_call, headers={"User-Agent":"Neotoma-Article-Relevance-Tool (mailto:goring@wisc.edu)"})
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

    logger.info(f'GeoDeepDive query completed.')


    # ========= Convert gdd data to dataframe =========
    # initialize the resulting dataframe
    gdd_df = pd.DataFrame()

    counter = 0
    for article in data:
        counter +=1
        one_article_dict = {}
        one_article_dict['gddid'] = [article['_gddid']]

        if article['identifier'] == []:
             one_article_dict['DOI'] = ['Non-DOI Article ID type']
        elif article['identifier'][0]['type'] == 'doi':
            one_article_dict['DOI'] = [article['identifier'][0]['id']]
        else:
            one_article_dict['DOI'] = ['Non-DOI Article ID type']

        one_article_dict['url'] = [article['link'][0]['url']]
        one_article_dict['status'] = 'queried'

        one_article = pd.DataFrame(one_article_dict)
        gdd_df = pd.concat([gdd_df, one_article])

    gdd_df = gdd_df.reset_index(drop=True)
    logger.info(f'{gdd_df.shape[0]} articles returned from GeoDeepDive.')


    # ========== Get list of existing gddids from the parquet files =========
    if auto_check_dup == True:
        # Get the list of existing IDs from the Parquet files
        logger.info(f'auto_check_dup is True. Removing duplicates.')

        file_list = os.listdir(parquet_path)
        if len(file_list) == 0:
            logger.warning(f'auto_check_dup is True, but no existing parquet file found. All queried articles will be returned.')
            result_df = gdd_df.copy()

        else:
            existing_ids = set()
            for file_name in os.listdir(parquet_path):
                file_path = os.path.join(parquet_path, file_name)
                if file_name.endswith(".parquet") and os.path.isfile(file_path):
                    # Read only the ID column from the Parquet file
                    gdd_one_file = pq.read_table(file_path, columns=["gddid"]).to_pandas()
                    existing_ids.update(gdd_one_file["gddid"])

            # remove the duplicates
            result_df = gdd_df[~gdd_df["gddid"].isin(existing_ids)]
            logger.info(f'{result_df.shape[0]} articles are new addition for relevance prediction.')

    else:
         result_df = gdd_df.copy()

    # ========= Output JSON (intermediate file for next step, will be deleted by makefile)===========
    result_dict = {}

    # pass the query info to prediction step (for saving in the parquet file)
    result_dict['queryinfo_min_date'] = min_date

    if max_date is None:
        current_date = date.today()
        formatted_date = current_date.strftime("%Y-%m-%d")
        result_dict['queryinfo_max_date'] = formatted_date
    else:
        result_dict['queryinfo_max_date'] = max_date

    result_dict['queryinfo_n_recent'] = n_recent_articles
    result_dict['queryinfo_term'] = term

    result_dict['data'] = result_df.to_dict()

    # Write the JSON object to a file
    directory = os.path.join(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(output_path + '/gdd_api_return.json', "w") as file:
        json.dump(result_dict, file)


def find_max_date_from_parquet(parquet_path):
    """
    Based on the filename, find the last date when the pipeline was run.
    Return this data in yy-mm-dd format as a string.

    Args:
        parquet_path (str)      The path to the folder that stores the processed parquet files.

    Return:
        Date as a string.
    """
    # initialize the date with an very old date
    min_date = datetime.strptime('1800-01-01', "%Y-%m-%d").date()
    for file_name in os.listdir(parquet_path):
        file_path = os.path.join(parquet_path, file_name)
        if file_name.endswith(".parquet") and file_name.startswith('article-relevance-prediction_') and os.path.isfile(file_path):
            # Extract date from the file_name
            curr_date_str = file_name.split('_')[1][0:10]
            curr_date = datetime.strptime(curr_date_str, "%Y-%m-%d").date()

            # Compare with result and update if the date is newer
            if curr_date > min_date:
                 min_date = curr_date

    min_date_str = min_date.strftime("%Y-%m-%d")

    return min_date_str


def main():
    opt = docopt(__doc__)
    doi_file_storage = opt["--doi_path"]
    parquet_file_path = opt["--parquet_path"]
    param_n_recent = opt["--n_recent"]

    if param_n_recent == '': # case when n_recent is left empty in the ENV variable
         param_n_recent = None

    if param_n_recent is not None:
        param_n_recent = int(param_n_recent)

    param_min_date = opt["--min_date"]

    param_auto_min_date = opt['--auto_min_date']

    if param_auto_min_date.lower() == 'true':
        file_list = os.listdir(parquet_file_path)
        if len(file_list) == 0:
             logger.warning(f'auto_min_date is True, but no existing parquet file found. All queried articles up to max_date will be returned.')
        else:
             param_min_date = find_max_date_from_parquet(parquet_file_path)
             logger.warning(f'auto_min_date is True. {param_min_date} is set as the min_date.')


    param_auto_check_dup = opt['--auto_check_dup']
    if param_auto_check_dup is None:
        param_auto_check_dup = False

    param_max_date = opt["--max_date"]
    param_term = opt["--term"]

    get_new_gdd_articles(output_path = doi_file_storage,
                         parquet_path = parquet_file_path,
                         min_date = param_min_date,
                         max_date = param_max_date,
                         n_recent_articles= param_n_recent,
                         term = param_term,
                         auto_check_dup = param_auto_check_dup
                         )

if __name__ == "__main__":
    main()
