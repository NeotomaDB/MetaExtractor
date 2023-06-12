# Author: Ty Andrews, Jenit Jain
# Date: May 10, 2023

import os
import sys
import spacy

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def spacy_extract_all(text: str,
                            ner_model=None,
                            model_path=os.path.join(
                                os.pardir,
                                "models",
                                "v1",
                                "transformer")):
    """
    Extracts entities from text using a spacy model

    Parameters
    ----------
    text : str
        The text to extract entities from
    ner_model : spacy model
        The spacy model to use for entity extraction
    model_path : str
        The path to the spacy model to use for entity extraction
    
    Returns
    -------
    entities : list
        A list of entities and their metadata
    """

    if ner_model == None:
        spacy.require_cpu()
        ner_model = spacy.load(model_path)

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
