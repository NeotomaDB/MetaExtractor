# Author Kelly Wu
# 2023-06-03

# Relevance prediction pipeline
# Input: list of doi
# output: df containing all metadata, predicted relevance, predict_proba

"""This script takes a list of DOI as input and output a dataframe containing all metadata, predicted relevance, predict_proba of each article.

Usage: relevance_prediction.py --doi_path=<doi_path> --model_path=<model_path> --output_path=<output_path>

Options:
    --doi_path=<doi_path>                   The path to where the list of DOI is.
    --model_path=<model_path>               The path to where the model object is stored.
    --output_path=<output_path>             The path to where the output files will be saved.
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
import logging
from docopt import docopt
from src.logs import get_logger

logger = get_logger(__name__) # this gets the object with the current modules name


def crossref_extract(doi_path, doi_colname):
    """Extract metadata from the Crossref API for article's in the doi csv file.
    Extracted data are returned in a pandas dataframe.

    If certain DOI is not found on CrossRef, the DOI will be logged in the prediction_pipeline.log file. 
    
    Args:
        doi_path (str): Path to the doi list csv file.
        doi_col (str): Column name of DOI.
    
    Return:
        pandas Dataframe containing CrossRef metadata.
    """

    df = pd.read_csv(doi_path)
    doi_col = doi_colname

    # a list of doi
    input_doi = df[doi_col].unique().tolist()

    # Initialize
    crossref = pd.DataFrame()
    num_invalid = 0    # track number of not found articles 

    # Loop through all doi, concatenate metadata into dataframe
    for doi in input_doi:
        cross_ref_url = f"https://api.crossref.org/works/{doi}"

         # make a request to the API
        cross_ref_response = requests.get(cross_ref_url)

        if cross_ref_response.status_code == 200:

            ref_json = pd.DataFrame(cross_ref_response.json())
            ref_df = pd.DataFrame(ref_json.loc[:, 'message']).T.reset_index()
            ref_df['valid_for_prediction'] = 1
            crossref = pd.concat([crossref, ref_df])

        else: 
            pass
    
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


    # join gdd_id to the metadata df
    df = df.loc[:, [doi_colname, 'gdd_id']].rename(columns = {doi_colname: 'DOI'})
    df['DOI'] = df['DOI'].str.lower()
    result_df = pd.merge(df, crossref, on='DOI', how='left')
    result_df = result_df.rename(columns = {'container-title': 'journal'})

    # Add valid_for_prediction indicator
    result_df['valid_for_prediction'] = result_df['valid_for_prediction'].fillna(value=0).astype(int)

    return result_df


def en_only_helper(value):
     ''' Helper function for en_only. 
     Apply row-wise to impute missing language data.'''
     
     detect_lang = detect(value)
     if 'en' in detect_lang:
        return 'en'
     else:
        return 'non-en'
     

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

    metadata_df = metadata_df.reset_index(drop = True)

    # Clean text in Subject
    metadata_df['subject_clean'] = metadata_df['subject'].fillna(value='').apply(lambda x: ' '.join(x))

    # Clean text in title, subtitle, abstract
    metadata_df['title_clean'] = metadata_df['title'].fillna(value='').apply(lambda x: ''.join(x))
    metadata_df['subtitle_clean'] = metadata_df['subtitle'].fillna(value='').apply(lambda x: ''.join(x))
    metadata_df['journal'] = metadata_df['journal'].fillna(value='').apply(lambda x: ''.join(x))

    # Add has_abstract indicator
    valid_condition = (metadata_df['valid_for_prediction'] == 1)
    metadata_df.loc[valid_condition, 'has_abstract'] = metadata_df.loc[valid_condition, "abstract"].isnull()

    # Remove tags from abstract
    metadata_df['abstract_clean'] = metadata_df['abstract'].fillna(value='').apply(lambda x: ''.join(x))
    metadata_df['abstract_clean'] = metadata_df['abstract_clean'].str.replace(pat = '<(jats|/jats):(p|sec|title|italic|sup|sub)>', repl = ' ')
    metadata_df['abstract_clean'] = metadata_df['abstract_clean'].str.replace(pat = '<(jats|/jats):(list|inline-graphic|related-article).*>', repl = ' ')

    # Concatenate descriptive text
    metadata_df['text_with_abstract'] =  metadata_df['title_clean'] + ' ' + metadata_df['subtitle_clean'] + ' ' + metadata_df['abstract_clean']

    # Impute missing language
    metadata_df['language'] = metadata_df['language'].fillna(value = '')
    metadata_df['text_with_abstract'] = metadata_df['text_with_abstract'].fillna(value = '')
    condition_row = (metadata_df['language'].str.len() == 0) & (metadata_df['text_with_abstract'].str.contains('[a-zA-Z]'))
    metadata_df.loc[condition_row,'language'] = metadata_df.loc[condition_row, 'language'].apply(lambda x: en_only_helper(x))
    
    # Set valid_for_prediction col to 0 if detected language is not English
    en_condition = metadata_df['language'] != 'en' 
    metadata_df.loc[en_condition, 'valid_for_prediction'] = 0

    keep_col = ['DOI', 'URL', 'gdd_id', 'valid_for_prediction', 'title_clean', 'subtitle_clean', 'abstract_clean',
                'subject_clean', 'journal', 'author', 'text_with_abstract',
                'is-referenced-by-count', 'has_abstract', 'language', 'published', 'publisher']
    
    metadata_df = metadata_df.loc[:, keep_col]

    metadata_df = metadata_df.rename(columns={'title_clean': 'title',
                                'subtitle_clean': 'subtitle',
                                'abstract_clean': 'abstract'})
    
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
    
    embedding_model = SentenceTransformer(model)

    valid_df = input_df.query("valid_for_prediction == 1")
    invalid_df = input_df.query("valid_for_prediction != 1")

    # add embeddings to valid_df
    embeddings = valid_df[text_col].apply(embedding_model.encode)
    embeddings_df = pd.DataFrame(embeddings.tolist())
    df_with_embeddings = pd.concat([valid_df, embeddings_df], axis = 1)
    df_with_embeddings.columns = df_with_embeddings.columns.astype(str)

    # concatenate invalid_df with valid_df
    result = pd.concat([df_with_embeddings, invalid_df])

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
    # load model
    model_object = joblib.load(model_path)

    # split by valid_for_prediction
    valid_df = input_df.query('valid_for_prediction == 1')
    invalid_df = input_df.query('valid_for_prediction != 1')

    # Use the loaded model for prediction on a new dataset
    valid_df['predict_proba'] = model_object.predict_proba(valid_df)[:, 1]
    print
    valid_df['prediction'] = valid_df.loc[:,'predict_proba'].apply(lambda x: 1 if x >= predict_thld else 0)

    # Filter results, store key information that could possibly be useful downstream
    keyinfo_col = ['DOI', 'URL', 'gdd_id', 'valid_for_prediction',
                    'prediction', 'predict_proba', 'title', 'subtitle', 'abstract',
                'subject_clean', 'journal', 'author', 'text_with_abstract',
                'is-referenced-by-count', 'has_abstract', 'language', 'published', 'publisher']
    invalid_col = ['DOI', 'URL', 'gdd_id', 'valid_for_prediction',
                 'title', 'subtitle', 'abstract',
                'subject_clean', 'journal', 'author', 'text_with_abstract',
                'is-referenced-by-count', 'has_abstract', 'language', 'published', 'publisher']
    keyinfo_df = valid_df.loc[:, keyinfo_col]
    keyinfo_df = keyinfo_df.rename(columns={'subject_clean': 'subject'})

    # Join it with invalid df to get back to the full dataframe
    result = pd.concat([keyinfo_df, invalid_df.loc[:, invalid_col]])

    return result


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
    df_directory = os.path.join(output_path)
    if not os.path.exists(df_directory):
        os.makedirs(df_directory)
    df_json = input_df.to_dict()

    # ==== Add other info in the json file ===
    result_dict = {}
    result_dict['total_article'] = input_df.shape[0]
    result_dict['valid_article'] = input_df.query('valid_for_prediction == 1').shape[0]
    result_dict['num_relevant_article'] = input_df.query('prediction == 1').shape[0]
    result_dict['pct_relevant_article'] = round(input_df.query('prediction == 1').shape[0]/input_df.shape[0] * 100, 3)
    result_dict['results'] = df_json

    # Write the JSON object to a file
    with open(output_path + '/relevance_prediction_output.json', "w") as file:
        json.dump(result_dict, file)

    # ===== log important information ======
    # Set up logging configuration
    logging.basicConfig(filename='prediction_pipeline.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')
    # Create a logger
    logger = logging.getLogger(__name__)

    logger.info(f'Total number of DOI processed: {input_df.shape[0]}')
    logger.info(f"Number of valid articles: {input_df.query('valid_for_prediction == 1').shape[0]}")
    logger.info(f"Number of invalid articles: {input_df.query('valid_for_prediction != 1').shape[0]}")


def main():
    opt = docopt(__doc__)

    doi_list_file_path = opt["--doi_path"]
    model_path = opt['--model_path']
    output_path = opt['--output_path']

    metadata_df = crossref_extract(doi_list_file_path, 'doi')
    preprocessed = data_preprocessing(metadata_df)
    embedded = add_embeddings(preprocessed, 'text_with_abstract', model = 'allenai/specter2')
    predicted = relevance_prediction(embedded, model_path, predict_thld = 0.5)
    prediction_export(predicted, output_path)


if __name__ == "__main__":
    main()