# This script focuses on data cleaning for the article relevance prediction task
# All the observations has been joined in the relevance_preprocessing.py script
# The script below will remove unneccesary columns, format columns and create useful features
# The cleaned data will be saved as a csv file under  "../data/processed/metadata_processed.csv"


# imports
import pandas as pd
import os
import requests
import json
import sys
from langdetect import detect

def import_concatenated_data(path):
     '''Read in concatenated data from csv'''

     result = pd.read_csv(path)
     return result

def tidy_keepcol(input_data, keep_col):
     '''Keep the specified data columns.'''

     result = input_data.loc[:,keep_col]
     return result

def en_only_helper(value):
     ''' Helper function for en_only. 
     Apply row-wise to impute missing language data.'''
     
     if len(value.strip()) == 0: # missing language from CrossRef
        detect_lang = detect(value)
        if 'en' in detect_lang:
             return 'en'
        else:
             return 'non-en'
     else:
         return value     

def en_only(input_data):
     '''Impute missing language information and drop non-English articles'''
     
     # Impute missing lang
     result = input_data.copy()
     result['detect_language'] = result.apply(lambda x: en_only_helper(x))
     






if __name__ == "__main__":
    
    # import the data from Neotoma CSV
    metadata_df = import_concatenated_data("../data/processed/metadata.csv")
    
    # clean up, keep only useful columns
    meatadaa_df = tidy_keepcol(metadata_df, 
                               ['abstract', 'is-referenced-by-count','language', 
                                'subject', 'subtitle', 'title', 'target'])
    
    # gather negative examples from GeoDeepDive and the Metadata from Crossref
    get_negative_articles("negative")
    
    # Import the data
    positive_df = crossref_import("positive")
    positive_df["target"] = 1
    negative_df = crossref_import("negative")
    negative_df["target"] = 0
    
    # Import other examples from Simon
    maybe_list = maybe_relevant_import("data/raw/article_list/pollen_doc_labels.csv", "data/raw/article_list/project_2_labeled_data.csv")
    crossref_extract(maybe_list, "maybe")
    mixed_crossref_df = crossref_import("maybe")
    
    # Get information from Simon's other examples
    # Join target to the Data Frame
    maybe_list = maybe_list.rename(columns={'doi': 'DOI'})
    mixed_crossref_df['DOI'] = mixed_crossref_df['DOI'].str.lower()
    maybe_list['DOI'] = maybe_list['DOI'].str.lower()
    mixed_crossref_df_target = pd.merge(mixed_crossref_df, maybe_list, on='DOI')
    
    crossref_keep_col = ['DOI',
    'URL',
    'abstract_y',
    'author',
    'container-title',
    'is-referenced-by-count', # times cited
    'language',
    'published', # datetime
    'publisher', 
    'subject', # keywords
    'subtitle', # subtitle are missing sometimes
    'title', # article title
    'target'
    ]

    mixdata_df = mixed_crossref_df_target.loc[:, crossref_keep_col].rename(columns={'abstract_y' : 'abstract'})
    
    # combine the data
    metadata_df = pd.concat([positive_df, negative_df, mixdata_df])
    
    # save the data
    metadata_df.to_csv("data/processed/metadata.csv", index=False)
    
    
    
    
    
    