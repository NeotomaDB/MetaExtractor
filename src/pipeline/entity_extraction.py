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
import json
from docopt import docopt

from src.preprocessing.labelling_preprocessing import get_journal_articles
from src.logs import get_logger

logger = get_logger(__name__)


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

    # load json
    with open(relevance_results_path) as f:
        data = json.load(f)

    # convert results field to dataframe
    relevant_articles = pd.DataFrame(json.loads(data["results"]))

    keep_columns = ["gdd_id", "DOI", "title", "author", "journal", "published"]

    relevant_articles = relevant_articles[keep_columns]

    # if any of the columsn are empty ignore and log a warning
    if relevant_articles.isnull().values.any():
        original_length = len(relevant_articles)
        relevant_articles = relevant_articles.dropna()
        logger.warning(
            f"Relevance results file {relevance_results_path} contains empty values. Removed {original_length - len(relevant_articles)} rows."
        )

    # convert published field to datetime, it originally has format:
    # {'date-parts': [[2023, 4, 3]]} but can be missing day
    relevant_articles["published_date"] = pd.to_datetime(
        relevant_articles["published"].apply(lambda x: str(x["date-parts"][0])),
        format="[%Y, %m, %d]",
        errors="coerce",
    ).fillna(
        pd.to_datetime(
            relevant_articles["published"].apply(lambda x: str(x["date-parts"][0])),
            format="[%Y, %m]",
            errors="coerce",
        )
    )
    # remove published field
    relevant_articles = relevant_articles.drop(columns=["published"])

    return relevant_articles


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

    # read in article text data to dataframe
    article_text_data = get_journal_articles(article_text_path)

    return article_text_data


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
