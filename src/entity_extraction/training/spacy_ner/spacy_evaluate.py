# Author: Ty Andrews and Jenit Jain
# Date: 2023-06-01
"""This script manages custom evaluation of the fine tuned spacy models.

Usage: spacy_evaluate.py --data_path=<data_path> --model_path=<model_path> --output_path=<output_path> --model_name=<model_name> [--gpu=<gpu>]

Options:
    --data_path=<data_path>         The path to the evaluation data in json format.
    --model_path=<model_path>       The path to the model to load.
    --output_path=<output_path>     The path to export the results & plots to.
    --model_name=<model_name>       The name of the model.
    --gpu=<gpu>                     Whether to use a GPU for inference or not. [default: False]
    
"""

import os, sys

import pandas as pd
import numpy as np
import spacy
import json
import logging
from docopt import docopt

sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir)
)

from src.entity_extraction.entity_extraction_evaluation import (
    calculate_entity_classification_metrics,
    plot_token_classification_report,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

opt = docopt(__doc__)


def get_spacy_token_labels(labelled_entities, raw_text):
    """
    Returns a list of labels per token in the raw text from spacy generated labels.

    Parameters
    ----------
    labelled_entities : list
        A list of dictionaries containing the labelled entities including the
        start and end indices of the entity, the entity label, and the entity
        text.
    raw_text : str
        The raw text that the entities were extracted from.

    Returns
    -------
    token_labels : list
        A list of labels per token in the raw text.
    """

    # split the text by whitespace
    split_text = raw_text.split()

    # create a list of labels per token
    token_labels = ["O"] * len(split_text)

    for entity in labelled_entities:
        start = entity["start"]
        end = entity["end"]
        label = entity["entity_group"]

        # get the token indices that the entity spans
        token_start = len(raw_text[:start].split())
        token_end = len(raw_text[:end].split())

        try:
            # if the entity spans multiple tokens
            if token_start != token_end:
                token_labels[token_start] = f"B-{label}"
                for i in range(token_start + 1, token_end):
                    token_labels[i] = f"I-{label}"
            else:
                token_labels[token_start] = f"B-{label}"
        except Exception as e:
            print(e)
            print("Error with entity: ", entity)
            print("Raw text: ", raw_text)
            print("Token start: ", token_start)
            print("Token end: ", token_end)

    return split_text, token_labels


def load_ner_model_pipeline(model_path: str, gpu: bool = False):
    """
    Loads a spacy named entity recognition model.

    Parameters
    ----------
    model_path : str
        The path to the model to load.

    Returns
    -------
    model : spacy.lang.en.English
        The ner model.
    """

    if gpu.lower() == "true":
        spacy.require_gpu()
    else:
        spacy.require_cpu()
    # load the model
    model = spacy.load(model_path)
    
    return model


def load_evaluation_data(data_file_path: str):
    """
    Loads the evaluation data.

    Parameters
    ----------
    data_path : str
        The path to the evaluation data in json format.

    Returns
    -------
    data : dict
        The labelled validation file.
    """
    
    # ensure the data file is txt
    if not data_file_path.endswith(".txt"):
        raise Exception("Data file must be txt format.")

    # ensure the data file exists and is txt file
    if not os.path.exists(data_file_path):
        raise Exception("Data file does not exist.")
    
    # load the data
    # The extension is txt because the data is in json lines format with 1 per file
    with open(data_file_path, "r") as f:
        data = f.readlines()
    
    # convert the data to json
    data = json.loads(data[0])

    return data


def get_labels(ner_model, data):
    """
    Returns the predicted and tagged labels per token of text.

    Parameters
    ----------
    ner_model : spacy.lang.en.English
        The ner model pipeline.
    data : dict
        The labelled validation file.

    Returns
    -------
    predicted_labels : list
        The predicted labels per token.
    
    tagged_labels : list
        The tagged labels per token.
    """
    
    predicted_entities = []
    tagged_entities = []
    
    # parse the data
    for entity in data['result']:
        tagged_entities.append({
            "start": entity['value']['start'],
            "end": entity['value']['end'],
            "entity_group": entity['value']['labels'][0],
            "entity_text": entity['value']['text']
        })
    
    # Get predictions on the text from the model    
    text = data['task']['data']['text']
    doc = ner_model(text)
    
    for entity in doc.ents:
        predicted_entities.append({
            "start": entity.start_char,
            "end": entity.end_char,
            "entity_group": entity.label_,
            "entity_text": entity.text,
        })
    
    _, predicted_labels = get_spacy_token_labels(predicted_entities, text)
    _, tagged_labels = get_spacy_token_labels(tagged_entities, text)

    return (predicted_labels,
            tagged_labels)


def generate_classification_results(true_tokens, predicted_tokens):
    """
    Summarizes the classification results by both entity and token based methods.

    Parameters
    ----------
    true_tokens : list[list[str]]
        The true labels per token.
    predicted_tokens : list[list[str]]
        The predicted labels per token.

    Returns
    -------
    classification_results : dict
        The classification results.
    """

    (
        token_accuracy,
        token_f1,
        token_recall,
        token_precision,
    ) = calculate_entity_classification_metrics(
        predicted_tokens=predicted_tokens, labelled_tokens=true_tokens, method="tokens"
    )
    (
        entity_accuracy,
        entity_f1,
        entity_recall,
        entity_precision,
    ) = calculate_entity_classification_metrics(
        predicted_tokens=predicted_tokens,
        labelled_tokens=true_tokens,
        method="entities",
    )

    # make a dict of all the number of each label type
    label_counts = {}
    for document in true_tokens:
        for label in document:
            label = label.replace("B-", "").replace("I-", "")
            if label not in label_counts.keys():
                label_counts[label] = 1
            else:
                label_counts[label] += 1

    # make the results into a dict
    results_dict = {
        "token": {
            "accuracy": token_accuracy,
            "f1": token_f1,
            "recall": token_recall,
            "precision": token_precision,
        },
        "entity": {
            "accuracy": entity_accuracy,
            "f1": entity_f1,
            "recall": entity_recall,
            "precision": entity_precision,
        },
        # calculate total tokens from the true tokens list of lists
        "num_tokens": sum([len(document) for document in true_tokens]),
        "entity_counts": label_counts,
    }

    return results_dict


def export_classification_report_plots(
    true_tokens, predicted_tokens, output_path: str, model_name: str
):
    """
    Exports the classification report plots.

    Parameters
    ----------
    true_tokens : list[list[str]]
        The true labels per token.
    predicted_tokens : list[list[str]]
        The predicted labels per token.
    output_path : str
        The path to export the plots to.
    model_name : str
        The name of the model.
    """

    # plot the classification report
    token_results_fig = plot_token_classification_report(
        labelled_tokens=true_tokens,
        predicted_tokens=predicted_tokens,
        title=f"{model_name} Token Based Classification Report",
        method="tokens",
        display=False,
    )

    entity_results_fig = plot_token_classification_report(
        labelled_tokens=true_tokens,
        predicted_tokens=predicted_tokens,
        title=f"{model_name} Entity Based Classification Report",
        method="entities",
        display=False,
    )

    # export the plots
    token_results_fig.savefig(
        os.path.join(output_path, f"{model_name}_token_classification_report.png")
    )
    entity_results_fig.savefig(
        os.path.join(output_path, f"{model_name}_entity_classification_report.png")
    )


def export_classification_results(
    classification_results: dict, output_path: str, model_name: str
):
    """
    Exports the classification results.

    Parameters
    ----------
    classification_results : dict
        The classification results.
    output_path : str
        The path to export the plots to.
    model_name : str
        The name of the model.
    """

    # export the classification results
    with open(
        os.path.join(output_path, f"{model_name}_classification_results.json"), "w"
    ) as f:
        json.dump(classification_results, f, indent=4)


def main():
    # load the model
    model = load_ner_model_pipeline(opt["--model_path"], opt["--gpu"])
    all_predicted_labels = []
    all_tagged_labels = []
    # run evaluation for each json file in the data directory
    for file in os.listdir(opt["--data_path"]):
        # skip non json files
        if not file.endswith(".txt"):
            continue
        logger.info(f"Evaluating {file}")
        file_name = file.split(".")[0]
        
        # load the evaluation data
        labelled_data = load_evaluation_data(os.path.join(opt["--data_path"], file))

        logger.info("Loaded model, generating predictions, this may take a while.")
        # get the predicted labels
        predicted_labels, tagged_labels = get_labels(model, labelled_data)
        
        all_predicted_labels.append(predicted_labels)
        all_tagged_labels.append(tagged_labels)
        
    logger.info("Generated predictions, calculating classification results")
    # get the classification results
    classification_results = generate_classification_results(
        true_tokens=all_tagged_labels, predicted_tokens=all_predicted_labels
    )

    # export the classification results
    export_classification_results(
        classification_results,
        opt["--output_path"],
        opt["--model_name"] + "_" + file_name,
    )

    # export the classification report plots
    export_classification_report_plots(
        true_tokens=all_tagged_labels,
        predicted_tokens=all_predicted_labels,
        output_path=opt["--output_path"],
        model_name=opt["--model_name"] + "_" + file_name,
    )


if __name__ == "__main__":
    main()
