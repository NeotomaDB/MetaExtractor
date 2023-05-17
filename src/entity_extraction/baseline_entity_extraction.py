# Author: Ty Andrews, Jenit Jain
# Date: May 10, 2023

import os
import sys

import re
import json
import pandas as pd
from nltk.corpus import stopwords
import spacy
from spacy.pipeline.ner import DEFAULT_NER_MODEL

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_taxa_data(file_path=os.path.join(os.pardir, "data", "raw", "taxa.csv")):
    """
    Loads the taxa names from a CSV file

    Returns
    -------
    dataframe
        Consists of the full taxa name and other metadata
    list
        Unique first words (common fossil names) of taxa names
    """

    def clean_name(name):
        # Removes special character at the start of the word#
        if name[0] == "?":
            name = name[1:]
        return name

    taxa = pd.read_csv(file_path, index_col=0)

    taxa["counts"] = 0
    taxa["num_words"] = taxa["taxonname"].str.split(" ").str.len()
    taxa = taxa.sort_values(by="num_words")

    taxa["taxonname"] = taxa["taxonname"].apply(clean_name)
    taxa["words"] = taxa["taxonname"].str.split("/")
    taxa["first_word"] = taxa["words"].apply(lambda x: x[0].split(" ")[0])

    all_taxa_words = []
    for word in taxa["first_word"].tolist():
        if len(word) > 2 and len(word) <= 25:
            all_taxa_words.append(word)

    stop = stopwords.words()
    all_taxa_words = list(set(all_taxa_words))
    all_taxa_words = [word for word in all_taxa_words if word not in stop]
    all_taxa_words.sort(key=lambda x: len(x), reverse=True)

    return taxa, all_taxa_words


def extract_geographic_coordinates(text: str) -> list:
    """
    Extracts the geographic coordinates from the text.

    Parameters
    ----------
    text : str
        The text to extract the geographic coordinates from.

    Returns
    -------
    list
        The list of geographic coordinates as dictionaries with the keys
        'start', 'end', and a list containing the label 'GEOG'.
    """
    group_1 = ["N", "E", "S", "W"]
    group_2 = ["°", "o", "◦", "'", "`", '"', "″", ":"]

    def check_groups(text):
        check_1 = False
        check_2 = False
        for i in group_1:
            if i in text:
                check_1 = True
                break
        for i in group_2:
            if i in text:
                check_2 = True
                break
        return check_1 and check_2

    pattern = r"""[-]?[NESW\d]+\s?[NESWd.:°o◦'"″]\s?[NESW]?\d{1,7}\s?[NESWd.:°o◦′'`"″]?\s?\d{1,6}[NESWd.:°o◦′'`"″]?\s?\d{0,3}[NESW]?"""

    labels = []

    matches = re.finditer(pattern, text)
    if matches:
        for match in matches:
            if check_groups(match.group()):
                labels.append(
                    {
                        "start": match.start(),
                        "end": match.end(),
                        "labels": ["GEOG"],
                        "text": text[match.start() : match.end()],
                    }
                )

    return labels


def extract_site_names(text: str, spacy_model: str = "en_core_web_lg") -> list:
    """
    Extracts the site names from the text.

    Parameters
    ----------
    text : str
        The text to extract the site names from.
    spacy_model: str
        Which spacy pretrained language model for named entity recognition.
        Default is 'en_core_web_lg'.
    Returns
    -------
    list
        The list of site names as dictionaries with the keys
        'start', 'end', and a list containing the label 'SITE'.
    """
    nlp = spacy.load(spacy_model)

    doc = nlp(text)
    labels = []
    for ent in doc.ents:
        if ent.label_ == "LOC":
            labels.append(
                {
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "labels": ["SITE"],
                    "text": ent.text,
                }
            )

    labels = sorted(labels, key=lambda label: label["start"])

    return labels


def extract_taxa(text: str) -> list:  # taxa: pd.DataFrame, all_taxa_words: list
    """
    Extracts the taxa from the text.

    Parameters
    ----------
    text : str
        The text to extract the taxa from.

    Returns
    -------
    list
        The list of taxa as dictionaries with the keys
        'start', 'end', and a list containing the label 'TAXA'.
    """

    def get_label(start_index, end_index, text):
        """Returns a single label object"""
        return {
            "start": start_index,
            "end": end_index,
            "labels": ["TAXA"],
            "text": text,
        }

    labels = []
    cur_len = 0

    taxa, all_taxa_words = load_taxa_data()

    # Split them into sentences to capture multiple instances of the same taxa
    for sentence in text.split(". "):
        for taxa_word in all_taxa_words:
            if taxa_word in sentence:
                possible_taxas = taxa[
                    taxa["first_word"].apply(lambda x: taxa_word == x)
                ]
                possible_taxas = possible_taxas.sort_values(
                    by="taxonname", key=lambda x: x.str.len(), ascending=False
                )
                for pt in possible_taxas.iterrows():
                    name = pt[1]["taxonname"]
                    if name in sentence:
                        taxa_index = pt[0]
                        taxa.loc[taxa_index, "counts"] += 1
                        index = sentence.index(name)

                        # If atleast 1 character is capital (i.e. start of the name of the fossil)
                        if name != name.lower():
                            try:
                                if sentence[index - 1] == " ":
                                    labels.append(
                                        get_label(
                                            cur_len + index,
                                            cur_len + index + len(name),
                                            sentence[index : index + len(name)],
                                        )
                                    )
                                else:
                                    continue
                            except:
                                labels.append(
                                    get_label(
                                        cur_len + index,
                                        cur_len + index + len(name),
                                        sentence[index : index + len(name)],
                                    )
                                )
                        break
        cur_len += len(sentence) + 2

    labels = sorted(labels, key=lambda label: label["start"])

    return labels


def extract_age(text: str) -> list:
    """
    Extracts the age of the samples from the text.

    Parameters
    ----------
    text : str
        The text to extract the age from.

    Returns
    -------
    list
        The list of age as dictionaries with the keys
        'start', 'end', and a list containing the label 'AGE'.
    """

    # matches any standalone date with BP at the end, can have decimal places
    is_date = re.compile(r"(\d+(?:[.]\d+)*) (([a-zA-Z]| )*BP)")

    # detects date ranges where its two numbers separated by a dash or to, they can
    # have decimal places then followed by any word to indicate units then BP
    is_date_range = re.compile(
        r"(\d+(?:[.]\d+)*) ((?:-{1,2})|(?:to)) (\d+(?:[.]\d+)*) (([a-zA-Z]| )*BP)"
    )

    # accumalate the labels
    labels = []

    # first check if its a date range and get start/end and set label to AGE
    for match in is_date_range.finditer(text):
        labels.append(
            {
                "start": match.start(),
                "end": match.end(),
                "labels": ["AGE"],
                "text": match.group(),
            }
        )

    # next check if its a date and get start/end and set label to AGE
    # ensure that the date is not part of a date range
    for match in is_date.finditer(text):
        if not any(
            match.start() >= label["start"] and match.end() <= label["end"]
            for label in labels
        ):
            labels.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "labels": ["AGE"],
                    "text": match.group(),
                }
            )

    # reoirder the labels by start index
    labels = sorted(labels, key=lambda label: label["start"])

    return labels


def extract_altitude(text: str) -> list:
    """
    Extracts the altitude of the samples from the text.

    Parameters
    ----------
    text : str
        The text to extract the altitude from.

    Returns
    -------
    list
        The list of altitude as dictionaries with the keys
        'start', 'end', and a list containing the label 'ALTI'.
    """

    is_altitude = re.compile(
        r"(\d+(?:[.]\d+)*) ?m ?(?:above sea level|a.s.l.|asl|elevation)"
    )

    # accumalate the labels
    labels = []
    for match in is_altitude.finditer(text):
        labels.append(
            {
                "start": match.start(),
                "end": match.end(),
                "labels": ["ALTI"],
                "text": match.group(),
            }
        )

    return labels


def extract_email(text: str) -> list:
    """
    Extracts the emails from the text.

    Parameters
    ----------
    text : str
        The text to extract the emails from.

    Returns
    -------
    list
        The list of emails as dictionaries with the keys
        'start', 'end', and a list containing the label 'EMAIL'.
    """

    # regex inspiration from: https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression
    is_email = re.compile(
        r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*)@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    )

    # accumalate the labels
    labels = []
    for match in is_email.finditer(text):
        labels.append(
            {
                "start": match.start(),
                "end": match.end(),
                "labels": ["EMAIL"],
                "text": match.group(),
            }
        )

    return labels


# define baseline method to extract all the labels
def baseline_extract_all(text: str, spacy_model: str = "en_core_web_lg") -> list:
    """Runs all baseline extractors on the text.

    Parameters
    ----------
    taxa: dataframe
        Consists of the full taxa name and other metadata
    all_taxa_words: list
        Unique first words (common fossil names) of taxa names
    text : str
        The text to extract the labels from.

    Returns
    -------
    list
        The list of labels as dictionaries with the keys
        'start', 'end', and a list containing the label.
    """

    # accumalate the labels
    labels = []

    taxa, all_taxa_words = load_taxa_data()

    nlp = spacy.load(spacy_model)

    # extract the labels from the text
    labels.extend(extract_age(text))
    labels.extend(extract_altitude(text))
    labels.extend(extract_email(text))
    labels.extend(extract_taxa(text, taxa, all_taxa_words))
    labels.extend(extract_site_names(text, nlp))
    labels.extend(extract_geographic_coordinates(text))

    # reorder the labels by start index
    labels = sorted(labels, key=lambda label: label["start"])

    return labels


if __name__ == "__main__":
    json_path = "../../data/train_files_json/"
    files = os.listdir(json_path)
    nlp = spacy.load("en_core_web_lg")

    taxa, all_taxa_words = load_taxa_data()

    for fin in files:
        with open(json_path + fin, "r") as f:
            data = json.load(f)
            text = data["text"]
            labels = baseline_extract_all(text, taxa, all_taxa_words, nlp)
            if len(labels) > 0:
                print(text)
                print(labels)
                print("---------------------------------------")
