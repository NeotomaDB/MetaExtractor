# Author: Ty Andrews, Jenit Jain
# Date: May 10, 2023

import os
import sys

import pandas as pd

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

    return []


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

    return []


def extract_emails(text: str) -> list:
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

    return []
