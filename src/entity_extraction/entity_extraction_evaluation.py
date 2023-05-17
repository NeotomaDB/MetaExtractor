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

    return token_labels


def plot_token_classification_report(
    labelled_tokens: list, predicted_tokens: list, title: str, display: bool = True
):
    """
    Plots a classification report for the token level entity extraction.

    Parameters
    ----------
    labelled_tokens : list
        A list of labels per token in the raw text.
    predicted_tokens : list
        A list of labels per token in the raw text.
    title : str
        The title of the plot.
    display : bool, optional
        Whether to display the plot or return the figure, by default True

    Returns
    -------
    fig : matplotlib.pyplot.figure
        The figure containing the classification report.
    """

    clf_report = classification_report(
        [labelled_tokens], [predicted_tokens], output_dict=True, zero_division=0
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
    labelled_tokens: list, predicted_tokens: list
):
    """Calculates the accuracy, f1, and recall scores for the entity extraction.

    Parameters
    ----------
    labelled_tokens : list
        The labelled tokens.
    predicted_tokens : list
        The predicted tokens.

    Returns
    -------
    accuracy : float
        The accuracy score.
    f1 : float
        The f1 score.
    recall : float
        The recall score.
    """

    accuracy = accuracy_score([labelled_tokens], [predicted_tokens])

    f1 = f1_score([labelled_tokens], [predicted_tokens])

    recall = recall_score([labelled_tokens], [predicted_tokens])


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
            error_labels.append(f"B-GOT_{predicted_lab.replace('-', '')}_EXPECTED_{actual_lab.replace('-', '')}")
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