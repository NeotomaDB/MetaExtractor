# Author: Ty Andrews
# Date: 2023-05-15

import os, sys

from seqeval.metrics import classification_report
from seqeval.metrics import accuracy_score, f1_score, recall_score, precision_score
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from spacy import displacy
from spacy.tokens import Doc
import spacy
import json
import copy
import numpy as np

def load_json_label_files(labelled_file_path:str):
    """
    Load the json files containing the labelled data and combines the text
    into a complete text string.
 
    Parameters
    ----------
    label_files : list
        List of json files containing the labelled data.

    Returns
    -------
    combined_text : str
        The combined text from all the files.
    all_labelled_entities : list
        List of all the labelled entities re-indexed to account for the combined text.
    """

    combined_text = ""
    all_labelled_entities = []
    for file in os.listdir(labelled_file_path):

        # if file is a txt file load it
        if  file.endswith(".txt"):
        
            with open(os.path.join(labelled_file_path, file), "r") as f:
                task = json.load(f)

            raw_text = task['task']['data']['text']

            annotation_result = task['result']
            labelled_entities = [annotation['value'] for annotation in annotation_result]

            # add the current text length to the start and end indices of labels plus one for the space
            for entity in labelled_entities:
                entity['start'] += len(combined_text)
                entity['end'] += len(combined_text)

            all_labelled_entities += labelled_entities

            # add the current text to the combined text with space in between
            combined_text += raw_text + " "

    return combined_text, all_labelled_entities

def get_token_labels(labelled_entities, raw_text):
    """
    Returns a list of labels per token in the raw text.

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
        label = entity["labels"][0]

        # get the token indices that the entity spans
        token_start = len(raw_text[:start].split())
        token_end = len(raw_text[:end].split())

        # if the entity spans multiple tokens
        if token_start != token_end:
            token_labels[token_start] = f"B-{label}"
            for i in range(token_start + 1, token_end):
                token_labels[i] = f"I-{label}"
        else:
            token_labels[token_start] = f"B-{label}"

    return split_text, token_labels

def generate_confusion_matrix(
    labelled_tokens: list,
    predicted_tokens: list,
    output_path: str,
    model_name: str
):
    """
    Generates confusion matrix 
    
    Parameters
    ----------
    labelled_tokens : list[list[str]]
        The true labels per token.
    predicted_tokens : list[list[str]]
        The predicted labels per token.
    output_path: str
        Path to output the confusion matrix diagram
    model_name: str
        Name of the model to include in the diagram title
    """
    
    def get_label_to_index(labels):
        """
        Generates dictionary of labels to index
    
        Parameters
        ----------
        labels : list[list[str]]
            The predicted labels per token.
        """
        # Create empty dictionary
        label_to_index = {}
        
        # Loop through each document
        for i in range(len(labels)):
            # Loop through each token
            for j in range(len(labels[i])):
                # Get the label
                label = labels[i][j]
                label = label.replace("B-", "").replace("I-", "")
                # If the label is not in the dictionary, add it
                if label not in label_to_index.keys():
                    label_to_index[label] = len(label_to_index)
                    
        return label_to_index
    
    label_to_index = get_label_to_index(labelled_tokens)
    
    num_tags = len(label_to_index)
    # Create empty confusion matrix
    confusion_matrix = np.zeros((num_tags, num_tags))
    
    labels = ["O"] * num_tags
    for key, value in label_to_index.items():
        labels[value] = key
        
    # Loop through each document
    for i in range(len(predicted_tokens)):
        # Loop through each token
        for j in range(len(predicted_tokens[i])):
            
            # Get the predicted and tagged labels
            predicted_label = predicted_tokens[i][j].replace("B-", "").replace("I-", "")
            tagged_label = labelled_tokens[i][j].replace("B-", "").replace("I-", "")
            
            # Get the index of the predicted and tagged labels
            predicted_index = label_to_index[predicted_label]
            tagged_index = label_to_index[tagged_label]
            
            # Add 1 to the confusion matrix
            confusion_matrix[tagged_index][predicted_index] += 1
    
    # normalize the matrix
    confusion_matrix = (
        confusion_matrix.astype('float') / confusion_matrix.sum(axis=1)[:, np.newaxis]
    )
    
    # Create a heatmap
    fig, ax = plt.subplots()
    heatmap = ax.imshow(confusion_matrix, cmap='viridis')
    
    # Add colorbar
    cbar = plt.colorbar(heatmap)

    # Add labels
    ax.set_xticks(np.arange(confusion_matrix.shape[1]))
    ax.set_yticks(np.arange(confusion_matrix.shape[0]))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    
    # set labels
    ax.set_title("Confusion Matrix")
    ax.set_ylabel('True')
    ax.set_xlabel('Predicted')
    ax.grid(False)
    
    #set labels for each grid box
    for i in range(confusion_matrix.shape[0]):
        for j in range(confusion_matrix.shape[1]):
            _ = ax.text(j, i, round(confusion_matrix[i, j], 2),
                           ha="center", va="center", color="w")
    
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")
    
    output_path = os.path.join(output_path, f"{model_name}_confusion_matrix.png")
    
    # Save the figure
    plt.savefig(output_path, dpi=300)


def plot_token_classification_report(
    labelled_tokens: list,
    predicted_tokens: list,
    title: str,
    method: str = "tokens",
    display: bool = True,
):
    """
    Plots a classification report for the token level entity extraction.

    Parameters
    ----------
    labelled_tokens : list[lists]
        A list of labels per token in the raw text.
    predicted_tokens : list[lists]
        A list of labels per token in the raw text.
    title : str
        The title of the plot.
    method : str, optional
        The method to use to calculate the scores, by default "entities"
        which calculates the scores based on complete entities extracted from BIO
        tags. "tokens" calculates the scores based on the token labels being
        exactly the same.
    display : bool, optional
        Whether to display the plot or return the figure, by default True

    Returns
    -------
    fig : matplotlib.pyplot.figure
        The figure containing the classification report.
    """

    # prevent over writing of original lists in memory
    predicted = copy.deepcopy(predicted_tokens)
    labelled = copy.deepcopy(labelled_tokens)

    if method == "tokens":
        # copy the lists so they aren't modified outside this function
        labelled = copy.deepcopy(labelled)
        predicted = copy.deepcopy(predicted)
        # in each list replace all I- labels with B- labels so each token is
        # considered a separate entity and update the token label objects
        for i, document in enumerate(labelled):
            document = [label.replace("I-", "B-") for label in document]
            labelled[i] = document
        for i, document in enumerate(predicted):
            document = [label.replace("I-", "B-") for label in document]
            predicted[i] = document

    clf_report = classification_report(
        labelled, predicted, output_dict=True, zero_division=0
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    # inspired from: https://stackoverflow.com/questions/28200786/how-to-plot-scikit-learn-classification-report
    sns.heatmap(
        pd.DataFrame(clf_report).iloc[:-1, :].T,
        annot=True,
        cmap="YlGnBu",
        fmt=".2g",
        ax=ax,
    )

    ax.set_title(title)
    ax.set_xlabel("Metrics")
    ax.set_ylabel("Labels")

    if display:
        plt.show()
    else:
        return fig


def calculate_entity_classification_metrics(
    labelled_tokens: list, predicted_tokens: list, method: str = "tokens"
):
    """Calculates the accuracy, f1, and recall scores for the entity extraction.

    Parameters
    ----------
    labelled_tokens : list[lists]
        The labelled tokens per document.
    predicted_tokens : list[lists]
        The predicted tokens per document.
    method : str, optional
        The method to use to calculate the scores, by default "entities"
        which calculates the scores based on complete entities extracted from BIO
        tags. "tokens" calculates the scores based on the token labels being
        exactly the same.

    Returns
    -------
    accuracy : float
        The accuracy score.
    f1 : float
        The f1 score.
    recall : float
        The recall score.
    """

    # prevent over writing of original lists in memory
    predicted = copy.deepcopy(predicted_tokens)
    labelled = copy.deepcopy(labelled_tokens)

    if method == "tokens":
        # copy the lists so they aren't modified outside this function
        labelled = copy.deepcopy(labelled)
        predicted = copy.deepcopy(predicted)
        # in each list replace all I- labels with B- labels so each token is
        # considered a separate entity and update the token label objects
        for i, document in enumerate(labelled):
            document = [label.replace("I-", "B-") for label in document]
            labelled[i] = document
        for i, document in enumerate(predicted):
            document = [label.replace("I-", "B-") for label in document]
            predicted[i] = document

    accuracy = accuracy_score(labelled, predicted)

    f1 = f1_score(labelled, predicted)

    recall = recall_score(labelled, predicted)

    precision = precision_score(labelled, predicted)

    return accuracy, f1, recall, precision

def visualize_mislabelled_entities(actual_labels: list, predicted_labels:list, text_tokens:list):
    """Shows the text with the mislabelled entities highlighted with false negatives in red, 
    false positives in orange and correct labels in green.

    Parameters
    ----------
    actual_labels : list
        A list of the actual labels for each token in the text.
    predicted_labels : list
        A list of the predicted labels for each token in the text.
    text : list
        A list of the text tokens matching the labels.
    """

    # all lists must be of same length 
    assert len(actual_labels) == len(predicted_labels) == len(text_tokens), "All lists must be of same length"


    # create a list of labels that are mislabelled with how they were mislabelled
    error_labels = []
    for i, (actual_lab, predicted_lab) in enumerate(zip(actual_labels, predicted_labels)):

        if actual_lab[2:] != predicted_lab[2:]:
            error_labels.append(f"B-GOT_{predicted_lab.replace('B-', '').replace('I-', '')}_EXPECTED_{actual_lab.replace('B-', '').replace('I-', '')}")
        else:
            error_labels.append(actual_lab)

    colors = {}
    ents = []
    # create dict of colors with red for false negative, orange for false positive and green for correct
    for tag in error_labels:
        # make false negatives red
        if "B-GOT_O" in tag:
            # remove the hyphenated B/I prefix and add to colors dict
            colors[tag[2:]] = "#ff0000"
            ents.append(tag.split("-")[1])
        elif "B-GOT" in tag:
            colors[tag[2:]] = "#ffa500"
            ents.append(tag.split("-")[1])
        elif tag != "O":
            colors[tag[2:]] = "#00ff00"
            ents.append(tag.split("-")[1])

    # load spacy model to use it's vocab
    nlp = spacy.load("en_core_web_lg")

    doc = Doc(
        vocab=nlp.vocab,
        words=text_tokens,
        ents=error_labels
    )
        
    displacy.render(doc, style="ent", jupyter=True, options={"colors": colors, "ents": ents})