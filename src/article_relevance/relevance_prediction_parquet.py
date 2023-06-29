# Author Kelly Wu
# 2023-06-03

# Relevance prediction pipeline
# Input: list of doi
# output: df containing all metadata, predicted relevance, predict_proba

"""This script takes a list of DOI as input and output a dataframe containing all metadata, predicted relevance, predict_proba of each article.

Usage: relevance_prediction_parquet.py --doi_file_path=<doi_path> --model_path=<model_path> --output_path=<output_path> --send_xdd=<send_xdd>

Options:
    --doi_file_path=<doi_file_path>         The path to where the list of DOI is.
    --model_path=<model_path>               The path to where the model object is stored.
    --output_path=<output_path>             The path to where the output files will be saved.
    --send_xdd=<send_xdd>                   When True, relevant articles will be sent to xDD through API query. Default is False.
"""

import pandas as pd
import numpy as np
import os
import requests
import json
import sys
from langdetect import detect
from sentence_transformers import SentenceTransformer
import joblib
from docopt import docopt
import pyarrow as pa
import pyarrow.parquet as pq
import datetime

# Locate src module
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from logs import get_logger

logger = get_logger(__name__) # this gets the object with the current modules name


def crossref_extract(doi_path):
    """Extract metadata from the Crossref API for article's in the doi csv file.
    Extracted data are returned in a pandas dataframe.

    If certain DOI is not found on CrossRef, the DOI will be logged in the prediction_pipeline.log file. 
    
    Args:
        doi_path (str): Path to the doi list JSON file.
        doi_col (str): Column name of DOI.
    
    Return:
        pandas Dataframe containing CrossRef metadata.
    """

    logger.info(f'Running crossref_extract function.')


    with open(doi_path) as json_file:
        data_dictionary = json.load(json_file)

    df = pd.DataFrame(data_dictionary['data'])

    if df.shape[0] == 0:
        logger.warning(f'Last xDD API query did not retrieve any article. Please verify the arguments.')
        raise ValueError("No article to process. Script terminated.")

    doi_col = 'DOI'

    # a list of doi
    input_doi = df[doi_col].unique().tolist()

    # Initialize
    crossref = pd.DataFrame()

    logger.info(f'Querying CrossRef API for article metadata.')

    # Loop through all doi, concatenate metadata into dataframe
    for doi in input_doi:
        cross_ref_url = f"https://api.crossref.org/works/{doi}"

         # make a request to the API
        cross_ref_response = requests.get(cross_ref_url)

        if cross_ref_response.status_code == 200:

            ref_json = pd.DataFrame(cross_ref_response.json())
            ref_df = pd.DataFrame(ref_json.loc[:, 'message']).T.reset_index()
            ref_df['valid_for_prediction'] = 1
            if 'abstract' not in ref_df.columns:
                ref_df['abstract'] = ''
            crossref = pd.concat([crossref, ref_df])

        else: 
            pass
    
    logger.info(f'CrossRef API query completed for {len(input_doi)} articles.')

    
    # Clean up columns and return the resulting pandas data frame
    crossref_keep_col = ['valid_for_prediction', 'DOI',
        'URL',
        'abstract',
        'author',
        'container-title',
        'is-referenced-by-count', # times cited
        'language',
        'published', # datetime
        'publisher', 
        'subject', # keywords of journal
        'subtitle', # subtitle are missing sometimes
        'title'
        ]
    
    crossref = crossref.loc[:, crossref_keep_col].reset_index(drop = True)


    # join gddid to the metadata df
    df = df.loc[:, ['DOI', 'gddid']]
    df['DOI'] = df['DOI'].str.lower() # CrossRef return lowercase DOI
    result_df = pd.merge(df, crossref, on='DOI', how='left')
    result_df = result_df.rename(columns = {'container-title': 'journal'})

    # Add valid_for_prediction indicator
    result_df['valid_for_prediction'] = result_df['valid_for_prediction'].fillna(value=0).astype(int)

    # Add metadata about article query info
    result_df['queryinfo_min_date'] = data_dictionary['queryinfo_min_date']
    result_df['queryinfo_max_date'] = data_dictionary['queryinfo_max_date']
    result_df['queryinfo_n_recent'] = data_dictionary['queryinfo_n_recent']
    result_df['queryinfo_term'] = data_dictionary['queryinfo_term']

    return result_df


def en_only_helper(value):
    ''' Helper function for en_only. 
    Apply row-wise to impute missing language data.'''
     
    try:
        detect_lang = detect(value)
    except:
        detect_lang = "error"
        logger.info("This text throws an error:", value)
     
    return detect_lang
     

def data_preprocessing(metadata_df):
    """
    Clean up title, subtitle, abstract, subject.
    Feature engineer for descriptive text column.
    Impute language.
    The outputted dataframe is ready to be used in model prediction.
    
    Args:
        metadata_df (pd DataFrame): Input data frame. 

    Returns:
        pd DataFrame containing all info required for model prediction.
    """

    logger.info(f'Prediction data preprocessing begin.')

    metadata_df = metadata_df.reset_index(drop = True)

    # Clean text in Subject
    metadata_df['subject_clean'] = metadata_df['subject'].fillna(value='').apply(lambda x: ' '.join(x))

    # Clean text in title, subtitle, abstract
    metadata_df['title_clean'] = metadata_df['title'].fillna(value='').apply(lambda x: ''.join(x))
    metadata_df['subtitle_clean'] = metadata_df['subtitle'].fillna(value='').apply(lambda x: ''.join(x))
    metadata_df['journal'] = metadata_df['journal'].fillna(value='').apply(lambda x: ''.join(x))

    # Add has_abstract indicator for valid articles
    valid_condition = (metadata_df['valid_for_prediction'] == 1)
    metadata_df.loc[valid_condition, 'has_abstract'] = metadata_df.loc[valid_condition, "abstract"].isnull()

    # Remove tags from abstract
    metadata_df['abstract_clean'] = metadata_df['abstract'].fillna(value='').apply(lambda x: ''.join(x))
    metadata_df['abstract_clean'] = metadata_df['abstract_clean'].str.replace(pat = '<(jats|/jats):(p|sec|title|italic|sup|sub)>', repl = ' ', regex=True)
    metadata_df['abstract_clean'] = metadata_df['abstract_clean'].str.replace(pat = '<(jats|/jats):(list|inline-graphic|related-article).*>', repl = ' ', regex=True)

    # Concatenate descriptive text
    metadata_df['text_with_abstract'] =  metadata_df['title_clean'] + ' ' + metadata_df['subtitle_clean'] + ' ' + metadata_df['abstract_clean']

    # Impute missing language
    logger.info(f'Running article language imputation.')

    metadata_df['language'] = metadata_df['language'].fillna(value = '')
    metadata_df['text_with_abstract'] = metadata_df['text_with_abstract'].fillna(value = '')


    # impute only when there are > 5 characters for langdetect to impute accurately
    need_impute_condition = (metadata_df['language'].str.len() == 0) & (metadata_df['text_with_abstract'].str.contains('[a-zA-Z]', regex=True)) & (metadata_df['text_with_abstract'].str.len() >= 5)
    cannot_impute_condition = (metadata_df['language'].str.len() == 0) & ~((metadata_df['text_with_abstract'].str.contains('[a-zA-Z]', regex=True)) & (metadata_df['text_with_abstract'].str.len() >= 5))

    # Record info
    n_missing_lang = sum(metadata_df['language'].str.len() == 0)
    logger.info(f'{n_missing_lang} articles require language imputation')
    n_cannot_impute = sum(cannot_impute_condition)
    logger.info(f'{n_cannot_impute} cannot be imputed due to too short text metadata(title, subtitle and abstract less than 5 character).')

    # Apply imputation
    metadata_df.loc[need_impute_condition,'language'] = metadata_df.loc[need_impute_condition, 'text_with_abstract'].apply(lambda x: en_only_helper(x))

    # Set valid_for_prediction col to 0 if cannot be imputed or detected language is not English
    metadata_df.loc[cannot_impute_condition, 'valid_for_prediction'] = 0
    en_condition = (metadata_df['language'] != 'en')
    metadata_df.loc[en_condition, 'valid_for_prediction'] = 0
    
    logger.info("Missing language imputation completed")
    logger.info(f"After imputation, there are {metadata_df.loc[en_condition, :].shape[0]} non-English articles in total excluded from the prediction pipeline.")

    keep_col = ['DOI', 'URL', 'gddid', 'valid_for_prediction', 'title_clean', 'subtitle_clean', 'abstract_clean',
                'subject_clean', 'journal', 'author', 'text_with_abstract',
                'is-referenced-by-count', 'has_abstract', 'language', 'published', 'publisher',
                'queryinfo_min_date',
                'queryinfo_max_date',
                'queryinfo_term',
                'queryinfo_n_recent']
    
    metadata_df = metadata_df.loc[:, keep_col]

    metadata_df = metadata_df.rename(columns={'title_clean': 'title',
                                'subtitle_clean': 'subtitle',
                                'abstract_clean': 'abstract'})
    
    # invalid when required input field is Null
    mask = metadata_df[['text_with_abstract', 'subject_clean', 'is-referenced-by-count', 'has_abstract']].isnull().any(axis=1)
    metadata_df.loc[mask, 'valid_for_prediction'] = 0

    mask_text = (metadata_df['text_with_abstract'].str.strip() == '')
    metadata_df.loc[mask_text, 'valid_for_prediction'] = 0

    with_missing_df = metadata_df.loc[mask, :]
    logger.info(f'{with_missing_df.shape[0]} articles has missing feature and its relevance cannot be predicted.')
    logger.info(f'Data preprocessing completed.')

    
    return metadata_df


def add_embeddings(input_df, text_col, model = 'allenai/specter2'):
    """
    Add sentence embeddings to the dataframe using the specified model.
    
    Args:
        input_df (pd DataFrame): Input data frame. 
        text_col (str): Column with text feature.
        model(str): model name on hugging face model hub.

    Returns:
        pd DataFrame with origianl features and sentence embedding features added.
    """
    logger.info(f'Sentence embedding start.')

    embedding_model = SentenceTransformer(model)

    valid_df = input_df.query("valid_for_prediction == 1")
    invalid_df = input_df.query("valid_for_prediction != 1")

    # add embeddings to valid_df
    embeddings = valid_df[text_col].apply(embedding_model.encode)
    embeddings_df = pd.DataFrame(embeddings.tolist())
    embeddings_df.index = valid_df.index

    df_with_embeddings = pd.concat([valid_df, embeddings_df], axis = 1)
    df_with_embeddings.columns = df_with_embeddings.columns.astype(str)

    # concatenate invalid_df with valid_df
    result = pd.concat([df_with_embeddings, invalid_df])

    logger.info(f'Sentence embedding completed.')

    return result


def relevance_prediction(input_df, model_path, predict_thld = 0.5):
    """
    Make prediction on article relevancy. 
    Add prediction and predict_proba to the resulting dataframe.
    Save resulting dataframe with all information in output_path directory.
    Return the resulting dataframe.

    Args:
        input_df (pd DataFrame): Input data frame. 
        model_path (str): Directory to trained model object.

    Returns:
        pd DataFrame with prediction and predict_proba added.
    """
    logger.info(f'Prediction start.')
    
    try:
        # load model
        model_object = joblib.load(model_path)
    except OSError:
        logger.error("Model for article relevance not found.")
        raise(FileNotFoundError)

    # split by valid_for_prediction
    valid_df = input_df.query('valid_for_prediction == 1')
    invalid_df = input_df.query('valid_for_prediction != 1')

    logger.info(f"Running prediction for {valid_df.shape[0]} articles.")

    # filter out rows with NaN value
    feature_col = ['has_abstract', 'subject_clean', 'is-referenced-by-count'] + [str(i) for i in range(0,768)]
    nan_exists = valid_df.loc[:, feature_col].isnull().any(axis = 1)
    df_nan_exist = valid_df.loc[nan_exists, :]
    valid_df.loc[nan_exists, 'valid_for_prediction'] = 0
    logger.info(f"{df_nan_exist.shape[0]} articles's input feature contains NaN value.")

    # Use the loaded model for prediction on a new dataset
    valid_df.loc[:, 'predict_proba'] = model_object.predict_proba(valid_df)[:, 1]
    valid_df['prediction'] = valid_df.loc[:,'predict_proba'].apply(lambda x: 1 if x >= predict_thld else 0)

    # Filter results, store key information that could possibly be useful downstream
    keyinfo_col = (['DOI', 'URL', 'gddid', 'valid_for_prediction',
                    'prediction', 'predict_proba'] + 
                    feature_col + 
                    ['title', 'subtitle', 'abstract', 'journal', 
                     'author', 'text_with_abstract', 'language', 'published', 'publisher',
                     'queryinfo_min_date',
                     'queryinfo_max_date',
                     'queryinfo_term',
                     'queryinfo_n_recent'])
    invalid_col = ['DOI', 'URL', 'gddid', 'valid_for_prediction',
                 'title', 'subtitle', 'abstract',
                'subject_clean', 'journal', 'author', 'text_with_abstract',
                'is-referenced-by-count', 'has_abstract', 'language', 'published', 'publisher',
                'queryinfo_min_date',
                'queryinfo_max_date',
                'queryinfo_term',
                'queryinfo_n_recent']
    
    keyinfo_df = valid_df.loc[:, keyinfo_col]

    # Join it with invalid df to get back to the full dataframe
    result = pd.concat([keyinfo_df, invalid_df.loc[:, invalid_col]])

    # Change col name on the final result to make it more readable
    result = result.rename(columns={'subject_clean': 'subject',
                                    'text_with_abstract': 'title_with_abstract'})

    logger.info(f'Prediction completed.')

    return result

def xdd_put_request(row):
    """
    If the article is predicted to be relevant, query xDD for full text.
    
    Args:
        row (a row in pd DataFrame) 

    Returns:
        'success' if the query was successful, otherwise 'failed'
        """

    if row['prediction'] == 1:

        # ========= To Be Completed after figuring out the API call ========
        # query xDD API
        # gddid = row['gddid']
        # api_call = f"API_CALL_for{gddid}"
        # xdd_response = requests.get(api_call)
        # status = xdd_response.status_code

        # ========= Mock output ========
        status = 200

        # ===== 
        if status == 200:
            return "success"
        else:
            return "failed"


def prediction_export(input_df, output_path):
    """
    Make prediction on article relevancy. 
    Add prediction and predict_proba to the resulting dataframe.
    Save resulting dataframe with all information in output_path directory.
    Return the resulting dataframe.

    Args:
        input_df (pd DataFrame): Input data frame. 
        model_path (str): Directory to trained model object.

    Returns:
        pd DataFrame with prediction and predict_proba added.
    """

    # ==== Save result to output_path directory =====
    parquet_folder = os.path.join(output_path, 'prediction_parquet')
    if not os.path.exists(parquet_folder):
        os.makedirs(parquet_folder)
    
    # Generate file name based on run date and batch
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%dT%H-%M-%S")

    # Check if a file with the current batch number already exists
    parquet_file_name = os.path.join(parquet_folder, f"article-relevance-prediction_{formatted_datetime}.parquet")
    while os.path.isfile(parquet_file_name):
        parquet_file_name = os.path.join(parquet_folder, f"article-relevance-prediction_{formatted_datetime}.parquet")

    # Write the Parquet file
    input_df.to_parquet(parquet_file_name)

    # ===== log important information ======
    logger.info(f'Total number of DOI processed: {input_df.shape[0]}')
    logger.info(f"Number of valid articles: {input_df.query('valid_for_prediction == 1').shape[0]}")
    logger.info(f"Number of invalid articles: {input_df.query('valid_for_prediction != 1').shape[0]}")
    logger.info(f"Number of relevant articles: {input_df.query('prediction == 1').shape[0]}")


def main():
    opt = docopt(__doc__)

    doi_list_file_path = opt["--doi_file_path"]
    output_path = opt['--output_path']
    send_xdd = opt['--send_xdd']
    
    # # /models directory is a mounted volume, containing the model object
    # models = os.listdir("/models")
    # models = [f for f in models if f.endswith(".joblib")]
    
    # if models:
    #     model_path = os.path.join("/models", models[0])
    # else:
    #     model_path = ""
    
    model_path = opt['--model_path']

    metadata_df = crossref_extract(doi_list_file_path)

    preprocessed = data_preprocessing(metadata_df)

    embedded = add_embeddings(preprocessed, 'text_with_abstract', model = 'allenai/specter2')

    predicted = relevance_prediction(embedded, model_path, predict_thld = 0.5)

    if send_xdd =="True":
        # run xdd_put_request function, add the xddquery_status column to the parquet
        predicted.loc[:, 'xdd_querystatus'] = predicted.apply(xdd_put_request, axis=1)
    
    prediction_export(predicted, output_path)



if __name__ == "__main__":
    main()