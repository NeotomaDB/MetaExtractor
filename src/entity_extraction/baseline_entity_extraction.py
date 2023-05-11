# Author: Ty Andrews, Jenit Jain
# Date: May 10, 2023

import os
import sys

import re

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


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

    return []


def extract_site_names(text: str) -> list:
    """
    Extracts the site names from the text.

    Parameters
    ----------
    text : str
        The text to extract the site names from.

    Returns
    -------
    list
        The list of site names as dictionaries with the keys
        'start', 'end', and a list containing the label 'SITE'.
    """

    return []


def extract_taxa(text: str) -> list:
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

    return []


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
                "label": ["AGE"],
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
                    "label": ["AGE"],
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

    is_altitude = re.compile(r"(\d+(?:[.]\d+)*) ?m ?(?:above sea level|a.s.l.|asl)")

    # accumalate the labels
    labels = []
    for match in is_altitude.finditer(text):
        labels.append(
            {
                "start": match.start(),
                "end": match.end(),
                "label": ["ALTI"],
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
                "label": ["EMAIL"],
                "text": match.group(),
            }
        )

    return labels
