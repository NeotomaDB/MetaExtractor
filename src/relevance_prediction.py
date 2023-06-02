# This script focuses on data cleaning for the article relevance prediction task
# All the observations has been joined in the relevance_preprocessing.py script
# The script below will remove unneccesary columns, format columns and create useful features
# The cleaned data will be saved as a csv file under  "../data/processed/metadata_processed.csv"

import pandas as pd
import numpy as np
import os
import requests
import json
import sys
from langdetect import detect
from sentence_transformers import SentenceTransformer
import joblib


# Step 1: extract CrossRef metadata using the provided DOI list.
def crossref_extract(doi_path, doi_colname, save_folder):
    """Extract metadata from the Crossref API for article's in the doi csv file.
    Extracted data are saved in the save_folder.

    If DOI is not found for a file, crossref_log.csv will have status code 404, sorted at top.

    Args:
        doi_path (str): Path to the doi list csv file.
        doi_col (str): Column name of DOI.
        save_folder (str): Destination of the CrossRef files.
    """
    df = pd.read_csv(doi_path)
    doi_col = doi_colname

    # a list of doi
    input_doi = df[doi_col].unique().tolist()
    
    # track status
    doi_status = {}
    doi_status['doi'] = input_doi
    doi_status['status_code'] = []

    
    for doi in input_doi:
        cross_ref_url = f"https://api.crossref.org/works/{doi}"

         # make a request to the API
        cross_ref_response = requests.get(cross_ref_url)
        
        doi_status['status_code'].append(cross_ref_response.status_code)

        if cross_ref_response.status_code == 200:

            # save data
            ref_data = cross_ref_response.json()
            
            # create the directory if it doesn't exist 
            directory = os.path.join(save_folder, 'crossref')
            if not os.path.exists(directory):
                os.makedirs(directory)

            # save the JSON data to a file
            doi_clean = doi.replace("/", "_")
            filename = f'crossref_{doi_clean}.json'
            filepath = os.path.join(directory, filename)
            with open(filepath, 'w') as outfile:
                json.dump(ref_data, outfile)

    
    # Save status as a log file
    log_directory = os.path.join(save_folder, 'log')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    doi_status_log = pd.DataFrame(doi_status).sort_values(by = ['status_code'], ascending = False)
    doi_status_log.to_csv(log_directory + 'crossref_log.csv')

def crossref_data_cleaning(crossref_dir):
    """Import the Crossref data from the specified folder.
    
    Args:
        crossref_folder (str): Name of the folder to import the data from.
        save_dir (str): Name of the folder to save the metadata data from.

    Returns:
        pandas DataFrame: Crossref data
    """  
    
    # Get a list of all files and directories in the directory
    files_and_directories = os.listdir(crossref_dir)

    # Filter out the directories to get only the files
    files = [file for file in files_and_directories if os.path.isfile(os.path.join(crossref_dir, file))]
    
    if '.DS_Store' in files:
        files.remove('.DS_Store')
    
     # initialize empty dataframe
    crossref = pd.DataFrame()

    # Populate the cross ref df
    for f in files:
        file_path = os.path.join(crossref_dir, f)
        onefile = pd.read_json(file_path)
        onefile = pd.DataFrame(onefile.loc[:, 'message']).T.reset_index()
    
        # merge
        crossref = pd.concat([crossref, onefile])
    
    crossref_keep_col = ['DOI',
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
    
    crossref = crossref.loc[:, crossref_keep_col]

    return crossref

def en_only_helper(value):
     ''' Helper function for en_only. 
     Apply row-wise to impute missing language data.'''
     
     detect_lang = detect(value)
     if 'en' in detect_lang:
        return 'en'
     else:
        return 'non-en'
     
    

def data_preprocessing(metadata_df, processed_dir):
    """
    Data management, feature engineer and save the data to save_dir.
    The output is ready to be used in model prediction.
    
    Args:
        processed_dir (str): Name of the folder to save the processed data.

    Returns:
        csv file with data ready for model prediction.
    """
    metadata_df = metadata_df.reset_index(drop = True)

    # Clean text in Subject
    metadata_df['subject_clean'] = metadata_df['subject'].fillna(value='').apply(lambda x: ' '.join(x))

    # Clean text in title, subtitle, abstract
    metadata_df['title_clean'] = metadata_df['title'].apply(lambda x: ''.join(x))
    metadata_df['subtitle_clean'] = metadata_df['subtitle'].apply(lambda x: ''.join(x))
    metadata_df['container-title'] = metadata_df['container-title'].apply(lambda x: ''.join(x))

    # Add has_abstract indicator
    metadata_df['has_abstract'] = metadata_df["abstract"].isnull().astype(int)

    # Remove tags from abstract
    metadata_df['abstract_clean'] = metadata_df['abstract'].fillna(value='').apply(lambda x: ''.join(x))
    metadata_df['abstract_clean'] = metadata_df['abstract_clean'].str.replace(pat = '<(jats|/jats):(p|sec|title|italic|sup|sub)>', repl = ' ')
    metadata_df['abstract_clean'] = metadata_df['abstract_clean'].str.replace(pat = '<(jats|/jats):(list|inline-graphic|related-article).*>', repl = ' ')

    # Concatenate descriptive text
    metadata_df['text_with_abstract'] =  metadata_df['title_clean'] + ' ' + metadata_df['subtitle_clean'] + ' ' + metadata_df['abstract_clean']

    # Impute missing Language
    condition = metadata_df['language'].apply(lambda x: len(x.strip()) == 0)
    metadata_df.loc[condition,'language'] = metadata_df.loc[condition, 'text_with_abstract'].apply(lambda x: en_only_helper(x))
    
    # clean up columns
    keep_col = ['DOI', 'URL', 'title_clean', 'subtitle_clean', 'abstract_clean',
                'subject_clean', 'container-title', 'author', 'text_with_abstract',
                'is-referenced-by-count', 'has_abstract', 'language', 'published', 'publisher']
    
    metadata_df = metadata_df.loc[:, keep_col]

    metadata_df = metadata_df.rename(columns={'title_clean': 'title',
                                'subtitle_clean': 'subtitle',
                                'abstract_clean': 'abstract',
                                'container-title': 'journal'})

    # Keep only English articles
    keep_df = metadata_df.query("language == 'en'")
    drop_df = metadata_df.query("language != 'en'")

    print(f"{keep_df.shape[0]} English articles will be processed." )
    print(f"{drop_df.shape[0]} Non-English articles will be dropped. Check log for more information.")

    #  Save files as csv
    df_directory = os.path.join(processed_dir)
    if not os.path.exists(df_directory):
        os.makedirs(df_directory)
    
    keep_df.to_csv(df_directory + '/processed_metadata.csv')
    drop_df.to_csv(df_directory + '/non-en-articles_log.csv')

    return keep_df

def add_embeddings(input_df, text_col, model = 'allenai/specter2'):
    
    embedding_model = SentenceTransformer(model)
    embeddings = input_df[text_col].apply(embedding_model.encode)
    embeddings_df = pd.DataFrame(embeddings.tolist())
    df_with_embeddings = pd.concat([input_df, embeddings_df], axis = 1)
    df_with_embeddings.columns = df_with_embeddings.columns.astype(str) 

    return df_with_embeddings

def relevance_prediction(df_with_embedding, model_object, processed_path, log_path, result_path):
    """
    Save result with full information in processed folder.
    Save relevant articles and non-relevant articles in results folder as two separate csv file. Keep only key information as reference.
    """
    result_df = df_with_embedding.copy()
    
    # Use the loaded model for prediction on a new dataset
    result_df['prediction'] = model_object.predict(result_df)
    result_df['predict_proba'] = model_object.predict_proba(result_df)[:, 1]

    # Filter results, store key information that could possibly be useful downstream
    keyinfo_col = ['DOI', 'URL', 'title', 'prediction',
       'predict_proba', 
       'subtitle', 'abstract', 'subject_clean',
       'journal', 'author', 'is-referenced-by-count'
       ]
    
    keyinfo_df = result_df[keyinfo_col]
    keyinfo_df = keyinfo_df.rename(columns={'subject_clean': 'subject'})
    relevant_df = keyinfo_df.query('prediction == 1')
    nonrelevant_df = keyinfo_df.query('prediction == 0')

    # Save result_df (with full info) in processed folder
    df_directory = os.path.join(processed_path)
    if not os.path.exists(df_directory):
        os.makedirs(df_directory)
    result_df.to_csv(processed_path + 'metadata_prediction_fullinfo.csv')

    # Save relevant articles in relevant_articles.csv in results folder 
    # Save non-relevant articles in non_relevant_articles.csv in results folder
    df_directory = os.path.join(result_path)
    if not os.path.exists(df_directory):
        os.makedirs(df_directory)
    relevant_df.to_csv(result_path + 'relevant_articles.csv')
    nonrelevant_df.to_csv(result_path + 'non_relevant_articles.csv')

    # Log prediction results in log folder under result path
    # Open the file in write mode
    file_path = log_path + '/log_relevance_prediction.txt'
    
    with open(file_path, 'w') as file:
      # Write the text to the file
      text = f'Total number of English articles processed: {result_df.shape[0]}\n'
      file.write(text)
      text = f'Number of articles predicted to be relevant: {relevant_df.shape[0]}\n'
      file.write(text)
      text = f'Number of articles predicted to be NOT relevant: {nonrelevant_df.shape[0]}\n'
      file.write(text)

if __name__ == "__main__":

    # download crossref metadata and save to json files
    crossref_extract('../data/article-relevance/raw/doi_list.csv', 'doi', 'data')

    # use metadata to create overall metadata dataframe 
    metadata_df = crossref_data_cleaning('../data/article-relevance/raw/crossref')

    # clean metadata, impute missing language, filter invalid articles
    metadata_cleaned = data_preprocessing(metadata_df, '../data/article-relevance/processed')

    # add sentence embeddings
    metadata_with_embedding = add_embeddings(metadata_cleaned, 'text_with_abstract', model = 'allenai/specter2')
    
    # run prediction, save logs and outputs
    loaded_model = joblib.load('../model/article-relevance/logistic_regression_model.joblib')
    processed_path = '../data/article-relevance/processed'
    log_path = '../results/article_relevance/log'
    result_path = '../results/article_relevance/output'
    
    relevance_prediction(metadata_with_embedding, loaded_model, processed_path, log_path, result_path)





