# Author: Ty Andrews, Jenit Jain
# Date: May 10, 2023

import os
import sys
import spacy

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from src.logs import get_logger
# logger = logging.getLogger(__name__)
logger = get_logger(__name__)

def spacy_extract_all(  
    text: str,
    ner_model=None):
    """
    Extracts entities from text using a spacy model

    Parameters
    ----------
    text : str
        The text to extract entities from
    ner_model : spacy model
        The spacy model to use for entity extraction
    
    Returns
    -------
    entities : list
        A list of entities and their metadata
    """

    if ner_model == None:
        logger.info("Empty model passed, return 0 labels.")
        return []

    entities = []
    doc = ner_model(text)

    for ent in doc.ents:
        entities.append({
            "start": ent.start_char,
            "end": ent.end_char,
            "labels": [ent.label_],
            "text": ent.text
        })

    return entities
