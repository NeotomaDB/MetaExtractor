import pandas as pd
import os
import re
import hashlib
import json
import spacy
from datetime import datetime
import sys

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.baseline_entity_extraction import baseline_extract_all
from src.entity_extraction.spacy_entity_extraction import spacy_extract_all

nlp = spacy.load(os.path.join("..", "..", "models", "v1", "transformer"))

def clean_words(words:list):
    """Perform basic preprocessing on individual words 
    
    Parameters
    ----------
    words : list
        List of words in a sentence

    Returns
    -------
    clean_words : list
        List of cleaned words
    """
    clean_words = []
    for i, w in enumerate(words):
        if w == '.':
            if len(clean_words)>0:
                clean_words[-1] += '.'
        else:
            clean_words.append(w.strip())
    return clean_words

def get_journal_articles(sentences_path):
    """
    Loads and formats sentences_nlp352 json file and converts to a dataframe

    Parameters
    ----------
    sentences_path : string
        Path where the individual sentences are stored.

    Returns
    -------
    journal_articles: pd.DataFrame
        pd.DataFrame with cleaned individual sentences for all articles 
    """
    journal_articles = pd.read_csv(sentences_path, 
                                sep='\t',
                                names = ['gddid', 
                                        'sentid',
                                        'wordidx',
                                        'words',
                                        'part_of_speech',
                                        'special_class',
                                        'lemmas',
                                        'word_type',
                                        'word_modified'], 
                                usecols = ['gddid', 'sentid', 'words'])

    journal_articles = (journal_articles.replace('"', '', regex = True)
                                .replace(',--,', '-', regex = True)
                                .replace('.,/,', '. / ', regex = True)
                                .replace('\{', '', regex = True)
                                .replace('}', '', regex = True)
                                .replace(r'\W{4,}', '', regex=True)
                                .replace(',,,', 'comma_sym', regex=True)
                                .replace(',', ' ', regex=True)
                                .replace('comma_sym', ', ', regex=True)
                                .replace('-LRB-', '(', regex=True)
                                .replace('-LSB-', '[', regex=True)
                                .replace('LRB', '(', regex=True)
                                .replace('LSB', '[', regex=True)
                                .replace('-RRB-', ')', regex=True)
                                .replace('-RSB-', ']', regex=True)
                                .replace('RRB', ')', regex=True)
                                .replace('RSB', ']', regex=True)
                                .replace('-RRB', ')', regex=True)
                                .replace('-RSB', ']', regex=True)
                                .replace('-RCB-', '-', regex=True)
                                .replace('-LCB-', '-', regex=True))
    
    return journal_articles

def preprocessed_bibliography(path):
    """
    Loads and formats bibliography json file and converts to a dataframe

    Parameters
    ----------
    path : string
        Path where the bibliography database is stored.

    Returns
    -------
    bibliography: pd.DataFrame
        pd.DataFrame with GDD ID and the Digital Object Identifier.
    """
    with open(path, 'r') as f:
        bib_dict = json.load(f)
    
    gdd = []
    doi = []
    
    for article in bib_dict:
        gdd.append(article['_gddid'])
        if "identifier" not in article:
            doi.append("")
        else:
            for iden in article['identifier']:
                if iden['type'] == "doi":
                    doi.append(iden['id'])
    
    return pd.DataFrame({"doi": doi,
                         "gddid": gdd})

def get_hash(text):
    """ Generates a hexadecimal code of a hash value given a string of any length

    Uses the Secure Hash Algorithm and Key Expansion techinque for hashing.

    Args:
        text: str
            String of text

    Returns:
        str: The first 8 characters of the hexadecimal hash string
    """
    return hashlib.shake_128(text.encode('utf-8')).hexdigest(8)

def return_json(chunk,
                chunk_local,
                chunk_global,
                chunk_subsection,
                gdd,
                doi,
                article_hash_code,
                model_version):
    """
    Creates a JSON file for an article to upload to LabelStudio for labelling.

    Parameters
    ----------
    chunk : str
        A chunk of text from a full text journal article
    chunk_local: int
        Index of the chunk in a particular subsection of the article
    chunk_global: int
        Index of the chunk in the entire article
    chunk_subsection: str
        The name of the subsection to which this chunk of text belongs
    gdd: str
        GeoDeepDive ID of the article
    doi: str
        Digital Object Identifier of the article
    article_hash_code: str
        Hash code generated using the full text article
    model_version: str
        Version of the model used to generate the labels
        
    Returns
    -------
    training_json: dict
        A dictionary containing the chunk of text and other metadata associated with the article
    """
    
    training_json = {
        "data": {
            "text": chunk,
            "subsection": chunk_subsection,
            "global_index": chunk_global,
            "local_index": chunk_local,
            "gdd_id": gdd,
            "doi": doi,
            "timestamp": str(datetime.today()),
            "chunk_hash": get_hash(chunk),
            "article_hash": article_hash_code
        },
        "predictions": [{
            "model_version": model_version,
            "result": []
        }]
    }
    
    # labels = baseline_extract_all(chunk)
    labels = spacy_extract_all(chunk, nlp)
    entities = []
    for label in labels:
        entities.append({
            "from_name": "label",
            "to_name": "text",
            "type": "labels", 
            "value": {
                "start": label['start'],
                "end": label['end'],
                "text": label['text'],
                "score": 0.5,
                "labels": label['labels']
            }}
        )
    training_json['predictions'][0]['result'] = entities

    return training_json

def chunk_text(article):
    # If a section is very long, each chunk will be approximately char_len in length
    char_len = 4500
    # If a section is very small (smaller than min_len), then it will be combined with the next section
    min_len = 1500
    # text chunk from full text articles
    chunks = [] 
    # Name of the subsection
    chunk_subsection = []
    # Local index of the chunk in the particular subsection
    chunk_local = []
    # Local index tracker 
    local_index = 0 
    # Current subsection name
    subsection = None
    # Current chunk of text
    cur_para = ""
    # Possible Subsection names 
    patterns = ["Introduction",
                "Abstract",
                "Material And Method",
                "Site Description", 
                "Interpretation", 
                "Results",
                "Background",
                "Discussion",
                "Objectives",
                "Conclusion"]
    # Possible Ending condition keywords names 
    endwords = ["Acknowledgement", "Reference"]
                
    sentences = article.split('. ')
    
    for sent in sentences:
        
        if subsection == None:
            subsection = sent.split(" ")[0]
            
        # If the paragraph is long enough, add it as a chunk
        # If the next sentence is very long, add the current paragraph as a chunk and reset cur_para
        if len(cur_para) > char_len or len(sent) > char_len:
            chunks.append(cur_para.strip())
            chunk_subsection.append(subsection)
            chunk_local.append(local_index)
            cur_para = ""
            local_index += 1
        
        check=True
        for pat in patterns:
            # If there is a pattern present:
            # then everything before the pattern goes in the current para
            # Text starting from the pattern goes in the next para after
            if pat in sent or pat.upper() in sent:
                try:
                    index = sent.index(pat)
                except ValueError:
                    index = sent.index(pat.upper())

                cur_para += sent[:index]
                
                if len(cur_para) > min_len:
                    chunks.append(cur_para.strip())
                    chunk_subsection.append(subsection)
                    chunk_local.append(local_index)
                    subsection = pat
                    local_index = 0
                    cur_para = sent[index: ] + '. '
                else:
                    cur_para += sent[index: ] + '. '
                    
                check = False
                break
                
        end=False
        # Check if there is an endwords
        for pat in endwords:
            if pat in sent or pat.upper() in sent:
                end=True
                break
        if end:
            break
        
        # If no pattern or ending condition is present in the current sentence, then add it to the current para
        if check:
            cur_para += sent + ". "
    if len(cur_para) > 0:
        chunks.append(cur_para.strip())
        chunk_subsection.append(subsection)
        chunk_local.append(local_index)

    return chunks, chunk_local, chunk_subsection
        
if __name__ == "__main__":
    
    model_version = "transformers-ner-0.0.1"
    
    bib_df = preprocessed_bibliography(os.path.join(os.pardir, os.pardir, "data", "original_files", "bibjson"))
    
    journal_articles = get_journal_articles(os.path.join(os.pardir, os.pardir, "data", "original_files", "sentences_nlp352"))
    
    # Minor preprocessing
    journal_articles['words']= journal_articles['words'].str.split(" ")
    journal_articles['words'] = journal_articles['words'].apply(clean_words)
    journal_articles['sentence'] = journal_articles['words'].apply(lambda x: ' '.join(map(str, x)))
    
    # Join sentences into full text articles
    full_text = (journal_articles 
                .groupby("gddid")['sentence'] 
                .agg(lambda x: ' '.join(x)).reset_index())
    
    doi_gdd = full_text.merge(bib_df, on ='gddid')
    
    # # Pass each raw text file to the chunking pipeline
    for row in full_text.iterrows():
        chunks, chunk_local, chunk_subsection = chunk_text(row[1]['sentence'])
        gdd = row[1]['gddid']
        doi = doi_gdd[doi_gdd['gddid'] == gdd].iloc[0]['doi']
        
        """ Generate a hash code using the full text article"""
        article_hash = get_hash(row[1]['sentence'])
        
        for i, chunk in enumerate(chunks):
            filename = get_hash(chunk)
            with open(f'{os.path.join(os.pardir, os.pardir, "data", "labelled", f"{model_version}_labeling")}/{gdd}_{i}.json','w') as fout:
                json_chunk = return_json(chunk, 
                                        chunk_local[i],
                                        i,
                                        chunk_subsection[i],
                                        gdd,
                                        doi,
                                        article_hash,
                                        model_version)
                json.dump(json_chunk, fout)            
