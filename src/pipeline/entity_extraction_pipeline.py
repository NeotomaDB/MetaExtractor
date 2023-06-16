# Author: Ty Andrews
# Date: 2023-06-05
"""
Usage: entity_extraction.py --article_text_path=<article_text_path> --output_path=<output_path> [--max_sentences=<max_sentences>] [--max_articles=<max_articles>]

Options:
--article_text_path=<article_text_path> The path to the article text data file.
--output_path=<output_path> The path to export the extracted entities to.
--max_sentences=<max_sentences> The maximum number of sentences to extract entities from. [default: -1]
--max_articles <max_articles> The maximum number of articles to extract entities from. [default: -1]
"""

import os
import sys

import pandas as pd
import json
from docopt import docopt
import spacy
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.preprocessing.labelling_preprocessing import get_journal_articles
from src.logs import get_logger
from src.entity_extraction.hf_entity_extraction import (
    load_ner_model_pipeline,
)
from src.entity_extraction.spacy_entity_extraction import (
    spacy_extract_all,
)

logger = get_logger(__name__)

ALL_LABELS = ["TAXA", "GEOG", "ALTI", "EMAIL", "SITE", "REGION", "AGE"]


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

    logger.info(f"Loading relevance results from {relevance_results_path}")
    # load json
    with open(relevance_results_path) as f:
        data = json.load(f)

    # convert results field to dataframe
    relevant_articles = pd.DataFrame(data["results"])

    keep_columns = [
        "gdd_id",
        "DOI",
        "title",
        "author",
        "journal",
        "published",
        "predict_proba",
    ]

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

    logger.info(f"Loading article text data from {article_text_path}")
    # read in article text data to dataframe
    article_text_data = get_journal_articles(article_text_path)

    # rename words column to text
    article_text_data = article_text_data.rename(columns={"words": "text"})

    # add column for the length in characters of the article text for use in reconstruction.
    article_text_data["text_length"] = article_text_data["text"].apply(len)

    # have the length in word counts split by spaces
    article_text_data["word_count"] = article_text_data["text"].apply(
        lambda x: len(x.split(" "))
    )

    # get the subsection name from pattern matching in each sentence
    patterns = [
        "Introduction",
        "Abstract",
        "Material And Method",
        "Site Description",
        "Interpretation",
        "Results",
        "Background",
        "Discussion",
        "Objectives",
        "Conclusion",
    ]

    article_text_data["section_name"] = article_text_data["text"].apply(
        lambda x: next(
            (
                pattern
                for pattern in patterns
                if pattern.lower() in x.lower().replace("\n", " ")
            ),
            None,
        )
    )

    # roll the section_name forward to the next sentence if it is empty
    article_text_data["section_name"] = article_text_data["section_name"].fillna(
        method="ffill"
    )

    # fix any sentences missing values to be in introduction
    article_text_data["section_name"] = article_text_data["section_name"].fillna(
        "Introduction"
    )

    logger.info(
        f"Done loading articles, found {len(article_text_data.gddid.unique())} articles."
    )

    return article_text_data


def combine_sentence_data(
    article_text_data: pd.DataFrame, max_word_length=256
) -> pd.DataFrame:
    logger.debug(
        f"Combining sentences into batches of {max_word_length} words or less. Started with {len(article_text_data)} sentences."
    )

    if len(article_text_data.gddid.unique()) > 1:
        raise ValueError(
            "article_text_data must only contain one article to avoid batch splitting across articles."
        )
    batch_df = article_text_data.copy(deep=True)

    batch_df["batch"] = (
        article_text_data.loc[:, "word_count"]
        .cumsum()
        .apply(lambda x: int(x / max_word_length))
    )

    batch_df = batch_df.groupby("batch", as_index=False).agg(
        gddid=("gddid", "first"),
        sentid_list=("sentid", lambda x: x.tolist()),
        section_name_list=("section_name", lambda x: x.tolist()),
        text_length_list=("text_length", lambda x: x.tolist()),
        word_count_list=("word_count", lambda x: x.tolist()),
        total_word_count=("word_count", "sum"),
        # split all words by space then make into single_list
        text=("text", lambda x: " ".join(x)),
    )

    logger.debug(f"Done combining sentences, created {len(batch_df)} batches.")

    return batch_df


def recreate_original_sentences_with_labels(row):
    """
    Recreates the original sentence with the labels added to the correct sentences.

    Parameters
    ----------
    row : pd.Series
        The row of the extracted entities results with the
        columns "text", "text_length_list", "word_count_list", "sentid_list",
        "gddid", "raw_labels".

    Returns
    -------
    pd.DataFrame
        The recreated sentences with the labels added and start/end indices adjusted.
    """

    # get the original sentence
    original_sentence = row["text"]

    split_df = pd.DataFrame()

    for i in range(0, len(row["text_length_list"])):
        # initialize empty df with columns for each label
        sent_df = pd.DataFrame(columns=ALL_LABELS)

        sent_df["sentid"] = [row["sentid_list"][i]]

        sent_start = sum(row["text_length_list"][0:i]) + i
        # add additional i for the space between sentences
        sent_end = sum(row["text_length_list"][0 : i + 1]) + i + 1

        sent_df["text"] = original_sentence[
            sent_start:sent_end
        ].strip()  # remove leading/trailing whitespace

        sent_df["word_count"] = [row["word_count_list"][i]]
        sent_df["text_length"] = [row["text_length_list"][i]]
        sent_df["gddid"] = [row["gddid"]]
        sent_df["section_name"] = [row["section_name_list"][i]]
        sent_df["model_name"] = [row["model_name"]]

        for label in ALL_LABELS:
            lab_ents = []
            for ent in row[label]:
                # prevent overwriting the original dict
                updated_ent = ent.copy()
                # if the label start is less than the next sentence start then add it to the labels_df
                if (ent["start"] <= sent_end) & (ent["end"] >= sent_start):
                    updated_ent["start"] = ent["start"] - sent_start
                    updated_ent["end"] = ent["end"] - sent_start
                    updated_ent["section_name"] = row["section_name_list"][i]
                    lab_ents.append(updated_ent)

            sent_df[label] = [lab_ents]

        if len(sent_df["text"].iloc[0]) != sent_df["text_length"].iloc[0]:
            logger.warning(
                f"Sentence length does not match text length, sentid: {sent_df['sentid'].iloc[0]}"
            )

        if len(sent_df["text"].iloc[0].split()) != sent_df["word_count"].iloc[0]:
            logger.warning(
                f"Word count does not match number of words, sentid: {sent_df['sentid'].iloc[0]}"
            )

        split_df = pd.concat([split_df, sent_df])

    return split_df


def extract_entities(
    article_text_data: pd.DataFrame,
    model_type: str = "huggingface",
    model_path: str = os.path.join("models", "ner", "roberta-finetuned-v3"),
) -> pd.DataFrame:
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

    model_name = model_path.split(os.sep)[-1]

    logger.info(
        f"Extracting entities from {len(article_text_data)} sentences. Using {model_name} model"
    )

    # turn the article text into batches of 256 words or less
    article_batch = combine_sentence_data(article_text_data)

    if model_type == "huggingface":
        # load the model
        logger.debug(f"Loading model from {model_path}")
        ner_pipe = load_ner_model_pipeline(model_path=model_path)

        start_time = pd.Timestamp.now()
        logger.info("Starting entity extraction. This may take a while...")

        raw_labels = ner_pipe(article_batch["text"].tolist())
        logger.info(
            f"Finished entity extraction in {pd.Timestamp.now() - start_time} to process {len(article_batch)} batches."
        )

        # update "word" attribute to be called "text" to match spacy
        # update "entitiy_group" to a list of the entity groups called labels
        for label in raw_labels:
            for entity in label:
                entity["text"] = entity.pop("word")
                entity["labels"] = [entity.pop("entity_group")]

        # get the predicted labels
        # article_batch["raw_labels"] = ner_pipe(article_batch["text"].tolist())
        article_batch["raw_labels"] = raw_labels

        # # create empty column to be filled with predicted labels
        # article_batch["raw_labels"] = len(article_batch) * [None]

        # try:
        #     # use tqdm to showprogress in batches, use base 4 or if less samples use single batch
        #     batch_size = min(2, len(article_batch))
        #     for i in tqdm(range(0, len(article_batch), batch_size)):
        #         raw_labels = ner_pipe(
        #             article_batch.text.iloc[i : i + batch_size]
        #             .apply(lambda x: " ".join(x))
        #             .tolist()
        #         )
        #         logger.debug(f"Found {len(raw_labels)} entities in batch {i}")
        #         # update "word" attribute to be called "text" to match spacy
        #         # update "entitiy_group" to a list of the entity groups called labels
        #         for label in raw_labels:
        #             for entity in label:
        #                 entity["text"] = entity.pop("word")
        #                 entity["labels"] = [entity.pop("entity_group")]
        #         article_batch.raw_labels.iloc[i : i + batch_size] = raw_labels
        # except Exception as e:
        #     logger.error(
        #         f"Error extracting entities for GDD ID: {article_batch['gddid'].iloc[0]}, skipping rest of article and returning results to this point. Error: {e}"
        #     )
        #     pass

        logger.info(
            f"Finished entity extraction in {pd.Timestamp.now() - start_time} to process {len(article_batch)} batches."
        )

    elif model_type == "spacy":
        spacy.require_cpu()
        logger.info(f"Loading model from {model_path}")
        spacy_model = spacy.load(model_path)

        start_time = pd.Timestamp.now()
        logger.info("Starting entity extraction. This may take a while...")

        article_batch["raw_labels"] = article_batch["text"].apply(
            lambda x: spacy_extract_all(x, spacy_model)
        )

    article_batch["model_name"] = model_name

    # TODO: deal with multiple labels for words in this grouping
    for label in ALL_LABELS:
        article_batch[label] = article_batch["raw_labels"].apply(
            lambda x: [entity for entity in x if entity["labels"][0] == label]
        )

    return article_batch


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

    logger.info(
        f"Post-processing extracted entities from {len(extracted_entities)} batches."
    )

    # TODO: optimize this to use apply or map instead of iterating over rows
    # issue is that function returns expanded dataframe so it can't be applied to a series
    recreated_sentences = pd.DataFrame()
    for i, row in extracted_entities.iterrows():
        recreated_sentences = pd.concat(
            [
                recreated_sentences,
                recreate_original_sentences_with_labels(row),
            ]
        )

    logger.debug(
        f"Post processed and re-assembled {len(recreated_sentences)} sentences."
    )

    # add in the sentence text before/after non-empty sentences to recreate the original text
    recreated_sentences["sentid_before"] = recreated_sentences["sentid"] - 1
    recreated_sentences["sentid_after"] = recreated_sentences["sentid"] + 1
    # keep sentences with at least one entity and one sentence before/after
    recreated_sentences = recreated_sentences[
        (recreated_sentences[ALL_LABELS].applymap(len).sum(axis=1) > 0)
        # or keep senteences with at least one entity and one sentence before/after
        | (
            recreated_sentences["sentid"].isin(
                recreated_sentences.loc[
                    recreated_sentences[ALL_LABELS].applymap(len).sum(axis=1) > 0,
                    "sentid_after",
                ].to_list()
            )
        )
        | (
            recreated_sentences["sentid"].isin(
                recreated_sentences.loc[
                    recreated_sentences[ALL_LABELS].applymap(len).sum(axis=1) > 0,
                    "sentid_before",
                ].to_list()
            )
        )
    ]

    logger.info("Done post-processing extracted entities.")

    return recreated_sentences


def export_extracted_entities(
    extracted_entities: pd.DataFrame,
    output_path: str,
) -> None:
    """
    Exports the extracted entities to json.

    Parameters
    ----------
    extracted_entities : pd.DataFrame
        The extracted entities.
    output_path : str
        The path to export the extracted entities to.
    """

    logger.info(
        f"Exporting extracted entities to {output_path} for gddid {extracted_entities['gddid'].iloc[0]}"
    )

    results_dict = {
        "gddid": extracted_entities["gddid"].iloc[0],
        "date_processed": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_name": extracted_entities["model_name"].iloc[0],
        "entities": {
            "TAXA": {},
            "GEOG": {},
            "ALTI": {},
            "EMAIL": {},
            "SITE": {},
            "REGION": {},
            "AGE": {},
        },
        "relevant_sentences": [],
    }

    for i, row in extracted_entities.iterrows():
        # add the text and sentid to relevant_sentences
        results_dict["relevant_sentences"].append(
            {
                "text": row["text"],
                "sentid": row["sentid"],
            }
        )
        for label in ALL_LABELS:
            for entity in row[label]:
                # remove leading/trailing whitespace from extracted text name
                # also remove any leading/trailing punctuation
                stripped_name = entity["text"].strip().strip(".,!?;:'\"")

                # check if the entity has already been added
                if stripped_name not in results_dict["entities"][label]:
                    results_dict["entities"][label][stripped_name] = {
                        "corrected_name": None,
                        "deleted": False,
                        "sentence": [
                            {
                                "text": row["text"],  # this is the full sentence
                                "section_name": row["section_name"],
                                "sentid": row["sentid"],
                                "char_index": {
                                    "start": entity["start"],
                                    "end": entity["end"],
                                },
                            }
                        ],
                    }
                else:
                    # if the entity has already been added then add the sentence
                    results_dict["entities"][label][stripped_name]["sentence"].append(
                        {
                            "text": row["text"],  # this is the full sentence
                            "section_name": row["section_name"],
                            "sentid": row["sentid"],
                            "char_index": {
                                "start": entity["start"],
                                "end": entity["end"],
                            },
                        }
                    )

    # export file name is gddid_timestamp.json without : in timestamp
    file_name = f"{results_dict['gddid']}.json"
    # export the results to json
    with open(os.path.join(output_path, file_name), "w") as f:
        json.dump(results_dict, f, indent=4)

    return results_dict


def main():
    opt = docopt(__doc__)

    logger.debug(f"Running entity extraction pipeline with options:\n{opt}")

    article_text_data = load_article_text_data(opt["--article_text_path"])

    if opt["--max_articles"] is not None and int(opt["--max_articles"]) != -1:
        article_text_data = article_text_data[
            article_text_data["gddid"].isin(
                article_text_data["gddid"].unique()[7 : 7 + int(opt["--max_articles"])]
            )
        ]

    # if max_sentences is not -1 then only use the first max_sentences sentences
    if opt["--max_sentences"] is not None and int(opt["--max_sentences"]) != -1:
        article_text_data = article_text_data.head(int(opt["--max_sentences"]))

    for article_gdd in article_text_data["gddid"].unique():
        logger.info(f"Processing GDD ID: {article_gdd}")

        article_text = article_text_data[article_text_data["gddid"] == article_gdd]

        # try:
        extracted_entities = extract_entities(
            article_text,
            model_type="spacy",
            model_path=os.path.join("models", "ner", "spacy-transformer-v3"),
        )

        # except Exception as e:
        #     logger.error(
        #         f"Error extracting entities for GDD ID: {article_gdd}, skipping article. Error: {e}"
        #     )
        #     continue

        try:
            pprocessed_entities = post_process_extracted_entities(extracted_entities)

            if len(pprocessed_entities) == 0:
                logger.warning(
                    f"No entities extracted for GDD ID: {article_gdd}, skipping article."
                )
                continue
        except Exception as e:
            logger.error(
                f"Error post processing entities for GDD ID: {article_gdd}, no results output. Error: {e}"
            )
            continue

        export_extracted_entities(
            extracted_entities=pprocessed_entities,
            output_path=opt["--output_path"],
        )


if __name__ == "__main__":
    main()
