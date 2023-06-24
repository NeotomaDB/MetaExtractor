# Author: Jenit Jain
# Date: 2023-06-23
"""
This script splits the original article text into bite-sized JSON with fields required for LabelStudio.


Usage: labelling_preprocessing.py --model_version <model_version> --output_path <output_path> [--model_path <model_path>] [--bib_path <bib_path>] [--sentences_path <sentences_path>] [--char_len <char_len>] [--min_len <min_len>]

Options:
    --model_version=<model_version>         The model version used to generate labels
    --output_path=<output_path>             The path to the output directory to store the generated labels to upload to LabelStudio
    --model_path=<model_path>               The path to the model artifacts to use to generate labels
    --bib_path=<bib_path>                   The path to the bibjson file containing article metadata
    --sentences_path=<sentences_path>       The path to the sentences_nlp file containing all sentences as returned by xDD
    --char_len=<char_len>                   If a section is very long, each chunk will be approximately char_len in length [default: 4000]
    --min_len=<min_len>                     If a section is very small (smaller than min_len), then it will be combined with the next section [default: 1500]
"""

import pandas as pd
import os
import logging
import hashlib
import json
import spacy
from datetime import datetime
from docopt import docopt
import sys

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from src.logs import get_logger
# logger = logging.getLogger(__name__)
logger = get_logger(__name__)
logger.setLevel(logging.INFO)

from src.entity_extraction.baseline_entity_extraction import baseline_extract_all
from src.entity_extraction.spacy_entity_extraction import spacy_extract_all


def clean_words(words: list):
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
        if w == ".":
            if len(clean_words) > 0:
                clean_words[-1] += "."
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
    
    assert os.path.exists(sentences_path)==True, f"Sentences NLP file does not exist {sentences_path}"
    
    journal_articles = pd.read_csv(
        sentences_path,
        sep="\t",
        names=[
            "gddid",
            "sentid",
            "wordidx",
            "words",
            "part_of_speech",
            "special_class",
            "lemmas",
            "word_type",
            "word_modified",
        ],
        usecols=["gddid", "sentid", "words"],
    )

    journal_articles["words"] = (
        journal_articles.words.str.replace('"', "", regex=True)
        .replace(",--,", "-", regex=True)
        .replace(".,/,", ". / ", regex=True)
        .replace("\{", "", regex=True)
        .replace("}", "", regex=True)
        .replace(r"\W{4,}", "", regex=True)
        .replace(",,,", "comma_sym", regex=True)
        .replace(",", " ", regex=True)
        .replace("comma_sym", ", ", regex=True)
        .replace("-LRB-", "(", regex=True)
        .replace("-LSB-", "[", regex=True)
        .replace("LRB", "(", regex=True)
        .replace("LSB", "[", regex=True)
        .replace("-RRB-", ")", regex=True)
        .replace("-RSB-", "]", regex=True)
        .replace("RRB", ")", regex=True)
        .replace("RSB", "]", regex=True)
        .replace("-RRB", ")", regex=True)
        .replace("-RSB", "]", regex=True)
        .replace("-RCB-", "-", regex=True)
        .replace("-LCB-", "-", regex=True)
    )

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
    assert os.path.exists(path)==True, f"Bibliography file does not exist {path}"
    
    with open(path, "r") as f:
        bib_dict = json.load(f)

    gdd = []
    doi = []

    for article in bib_dict:
        gdd.append(article["_gddid"])
        if "identifier" not in article:
            doi.append("")
        else:
            for iden in article["identifier"]:
                if iden["type"] == "doi":
                    doi.append(iden["id"])

    return pd.DataFrame({"doi": doi, "gddid": gdd})


def get_hash(text):
    """Generates a hexadecimal code of a hash value given a string of any length

    Uses the Secure Hash Algorithm and Key Expansion techinque for hashing.

    Args:
        text: str
            String of text

    Returns:
        str: The first 8 characters of the hexadecimal hash string
    """
    return hashlib.shake_128(text.encode("utf-8")).hexdigest(8)


def return_json(
    nlp,
    chunk,
    chunk_local,
    chunk_global,
    chunk_subsection,
    gdd,
    doi,
    article_hash_code,
    model_version,
):
    """
    Creates a JSON file for an article to upload to LabelStudio for labelling.

    Parameters
    ----------
    nlp: spacy.lang.en.English
        The NLP pipeline model used to generate new entities
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
            "article_hash": article_hash_code,
        },
        "predictions": [{"model_version": model_version, "result": []}],
    }

    try:
        # labels = baseline_extract_all(chunk)
        labels = spacy_extract_all(chunk, nlp)
        logger.info(f"Predicted {len(labels)} labels for the file {gdd}_{chunk_global}")
    except Exception as e:
        logger.exception(
            f"Error occured while using the model to predict entities.\n{str(e)}"
        )
        labels = []
            
    entities = []
    for label in labels:
        entities.append(
            {
                "from_name": "label",
                "to_name": "text",
                "type": "labels",
                "value": {
                    "start": label["start"],
                    "end": label["end"],
                    "text": label["text"],
                    # Spacy NER does not return a confidence score
                    "score": 0.5,
                    "labels": label["labels"],
                },
            }
        )
    training_json["predictions"][0]["result"] = entities

    return training_json


def chunk_text(opt, article):
    
    char_len = int(opt['--char_len'])
    min_len = int(opt['--min_len'])
    
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
    patterns = [
        "Introduction",
        "Abstract",
        "Material And Method",
        "Site Description",
        "Interpretation",
        "Results",
        "Background",
        "Discussion",
        "Objectives",
        "Conclusion",
    ]
    # Possible Ending condition keywords names
    endwords = ["Acknowledgement", "Reference"]

    #Split the article by sentences so that no chunk consists of partial sentences
    sentences = article.split(". ")

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

        check = True
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
                    cur_para = sent[index:] + ". "
                else:
                    cur_para += sent[index:] + ". "

                check = False
                break

        end = False
        # Check if there is an endwords
        for pat in endwords:
            if pat in sent or pat.upper() in sent:
                end = True
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


def load_data(opt):
    """Loads the original article text data

    Parameters
    ----------
    opt: Docopt object
        The docopt object that consists of input arguments

    Returns
    -------
    doi_gdd: pd.DataFrame
        A dataframe consists of 3 columns ["doi", "gddid", "sentence"]
    """
    
    model_version = opt["--model_version"]
    bib_path = opt["--bib_path"]
    sentences_path = opt["--sentences_path"]

    bib_df = preprocessed_bibliography(bib_path)
    journal_articles = get_journal_articles(sentences_path)

    # Minor preprocessing
    journal_articles["words"] = journal_articles["words"].str.split(" ")
    journal_articles["words"] = journal_articles["words"].apply(clean_words)
    journal_articles["sentence"] = journal_articles["words"].apply(
        lambda x: " ".join(map(str, x))
    )

    # Join sentences into full text articles
    full_text = (
        journal_articles.groupby("gddid")["sentence"]
        .agg(lambda x: " ".join(x))
        .reset_index()
    )

    doi_gdd = full_text.merge(bib_df, on="gddid")

    logger.info("Successfully merged the bibjson and sentences_nlp files")
    
    return doi_gdd


def main(opt, nlp):
    """
    Takes in a set of documents, chunks it smaller pieces, 
    finds entities using a pretrained model, and stores them in a format
    compatible with Label Studio
    
    Parameters
    ----------
    opt: Docopt
        Docopt object containing command line arguments
    nlp: spacy.lang.en.English
        Spacy NLP pipeline object for generating entities
    """
    
    # data below is a dataframe that we use to split articles into smaller chunks
    # If retraining from scratch for a different usecase than Paleoecology, 
    # YOU MUST UPDATE THE FOLLOWING
    # Format:
    # data: pd.DataFrame
    # columns: ["gddid", "sentence", "doi"]
    # gddid: xDD ID of an article (If it doesn't exist on xDD, provide a unique placeholder)
    # doi: Digital Object Identifier (If the articl hasn't been published, provide a unique placeholder)
    # sentence: The full text from an article/paper/other sources
    
    data = load_data(opt)
    
    os.makedirs(os.path.join(opt['--output_path'],
                             f"{opt['--model_version']}_labeling"),
                exist_ok=True)
    
    # Pass each raw text file to the chunking pipeline
    for row in data.iterrows():
        
        chunks, chunk_local, chunk_subsection = chunk_text(opt, row[1]["sentence"])
        gdd = row[1]["gddid"]
        doi = row[1]["doi"]

        logger.info(f"Split file {gdd} into {len(chunks)} chunks")
        
        """ Generate a hash code using the full text article"""
        article_hash = get_hash(row[1]["sentence"])

        for index, chunk in enumerate(chunks):
            filename = get_hash(chunk)
            with open(
                os.path.join(
                    opt['--output_path'],
                    f"{opt['--model_version']}_labeling",
                    f"{gdd}_{index}.json",
                ),
                "w",
            ) as fout:
                json_chunk = return_json(
                    nlp,
                    chunk,
                    chunk_local[index],
                    index,
                    chunk_subsection[index],
                    gdd,
                    doi,
                    article_hash,
                    opt['--model_version'],
                )
                json.dump(json_chunk, fout)


if __name__ == "__main__":
    opt = docopt(__doc__)
    
    try:
        nlp = spacy.load(opt['--model_path'])
        logger.info(f"Loading model from {opt['--model_path']}")
    except OSError as e:
        logger.warning(f"Could not load model from {opt['--model_path']}")
        nlp = None
        
    main(opt, nlp)