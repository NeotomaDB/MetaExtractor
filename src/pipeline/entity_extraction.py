# Author: Ty Andrews
# Date: 2023-06-05
"""
Usage: entity_extraction.py --relevance_results_path=<relevance_results_path> --article_text_path <article_text_path> --output_path=<output_path>

Options:
--relevance_results_path=<relevance_results_path> The path to the article relevance results file.
--article_text_path=<article_text_path> The path to the article text data file.
--output_path=<output_path> The path to export the extracted entities to.
"""

import os
import sys

import pandas as pd
from docopt import docopt


def load_relevant_articles(relevance_results_path: str) -> pd.DataFrame:
    """
    Loads the relevant articles from the article relevance results file.

    Parameters
    ----------
    relevance_results_path : str
        The path to the article relevance results file.

    Returns
    -------
    pd.DataFrame
        The relevant articles.
    """

    return pd.DataFrame()


def load_article_text_data(article_text_path: str) -> pd.DataFrame:
    """
    Loads the article text data from the article text data file.

    Parameters
    ----------
    article_text_path : str
        The path to the article text data file.

    Returns
    -------
    pd.DataFrame
        The article text data.
    """

    return pd.DataFrame()


def preprocess_article_text_data(article_text_data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the article text data.

    Parameters
    ----------
    article_text_data : pd.DataFrame
        The article text data.

    Returns
    -------
    pd.DataFrame
        The preprocessed article text data.
    """

    return pd.DataFrame()


def extract_entities(article_text_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the entities from the article text data.

    Parameters
    ----------
    article_text_data : pd.DataFrame
        The article text data.

    Returns
    -------
    pd.DataFrame
        The extracted entities.
    """

    return pd.DataFrame()


def post_process_extracted_entities(extracted_entities: pd.DataFrame) -> dict:
    """
    Post-processes the extracted entities into the format to be exported to json.

    Parameters
    ----------
    extracted_entities : pd.DataFrame
        The extracted entities.

    Returns
    -------
    dict
        The post-processed extracted entities.
    """

    return dict()


def export_extracted_entities(extracted_entities: dict, output_path: str) -> None:
    """
    Exports the extracted entities to json.

    Parameters
    ----------
    extracted_entities : dict
        The extracted entities.
    output_path : str
        The path to export the extracted entities to.
    """

    return None


def main():
    opt = docopt(__doc__)

    relevant_articles = load_relevant_articles(opt["--relevance_results_path"])

    article_text_data = load_article_text_data(opt["--article_text_path"])

    for article_gdd in relevant_articles["gddid"].unique():
        article_text = article_text_data[article_text_data["gddid"] == article_gdd]

        preprocessed_article_text_data = preprocess_article_text_data(article_text)

        extracted_entities = extract_entities(preprocessed_article_text_data)

        post_processed_extracted_entities = post_process_extracted_entities(
            extracted_entities
        )

        export_extracted_entities(
            post_processed_extracted_entities, opt["--output_path"]
        )


if __name__ == "__main__":
    main()
