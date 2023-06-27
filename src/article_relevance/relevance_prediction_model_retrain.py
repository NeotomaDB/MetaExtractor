# Author: Kelly Wu
# 2023-06-22

# Using corrected article relevance data to retrain the logistic regressio model
# Input: directory with the JSON files of new relevant articles & the parquet file with article info of the batch
# Output: Model object to be used for running the prediction pipeline

# Process Overview:
# - Gather the list of new data for training
# - Retried these article's feature from parquet file, convert to format that's suitable for model training
# - Spilt the new data into training split and test split. Default is 80%/20%, but user could modify the parameter in the train_test_split function.
# - Merge the new training split with old training split. Merge the test split with old test split.
# - Model retraining
# - Model evaluation

# Assumption:
# - All parquet files generated by the article relevance pipeline is stored in one folder
# - All new articles's reviewed data outputted from data review tool are stored in one folder, with subfolders for each batch.
# - Each parquet file contains doi, metadata, sentence embeddings, i.e. all info required for retraining

import os
import sys
import joblib

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import datetime

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import (
    cross_validate,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.linear_model import LogisticRegression 
from sklearn.compose import make_column_transformer, ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder, FunctionTransformer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


# Locate src module
current_dir = os.path.dirname(os.path.abspath('__file__'))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from logs import get_logger
logger = get_logger(__name__) # this gets the object with the current modules name

def train_data_load_split(train_raw_csv_path):
    '''
    Load the old sample used in the original model training.
    Return the train, validation, and test split as three dataframes.

    Args:
        train_raw_csv_path (str)    The path to the original training data file metadata_processed.csv.

    Return:
        Three pandas Data frames: train_df, valid_df, test_df

    Example:
        train_data_load_split(train_raw_csv_path = "../../data/article-relevance/processed/metadata_processed_embedded.csv")
    '''

    # load original training sample
    metadata_df = pd.read_csv(train_raw_csv_path, index_col=0)
    
    metadata_df['text_with_abstract'].fillna("", inplace=True)
    metadata_df['subject_clean'].fillna("", inplace=True)
    
    if metadata_df['has_abstract'].isna().any():
        raise ValueError(f"Column 'has_abstract' contains NaN values.")
    if metadata_df['is-referenced-by-count'].isna().any():
        raise ValueError(f"Column 'is-referenced-by-count' contains NaN values.")
    if metadata_df['text_with_abstract'].isna().any():
        raise ValueError(f"Column 'text_with_abstract' contains NaN values.")
    if metadata_df['target'].isna().any():
        raise ValueError(f"Column 'target' contains NaN values.")


    # Split into train/valid/test sets
    train_df, val_test_df = train_test_split(metadata_df, test_size=0.3, random_state=123)
    valid_df, test_df = train_test_split(val_test_df, test_size=0.5, random_state=123)
    logger.info(f'Data Loading - Original sample has {train_df.shape[0]}/{valid_df.shape[0]}/{test_df.shape[0]} in train/valid/test splits.')
    logger.info(f'Data Loading - Each original sample has {train_df.shape[1]} features.')

    return train_df, valid_df, test_df


def retrain_data_load_split(reviewed_parquet_folder_path):
    '''
    Get a DOI list of reviewed articles (i.e. status is completed/irrelevant).
    Retrieve their metadata and split into train/valid/test sets.
    Return the train, validation, and test splits as three dataframes.

    Args:
        reviewed_parquet_folder_path (str)  The path to the folder storing reviewed articles parquet files.

    Return:
        Three pandas Data frames: train_df, valid_df, test_df
    '''
    result_df = []

    # Get a list of parquet files in the folder
    parquet_list = os.listdir(reviewed_parquet_folder_path)

    # Loop thorugh all parquet files and extract the rows with status "Non-relevant" or "Completed"
    for file_name in parquet_list:
        if file_name.endswith('.parquet'):
            # Construct the file path
            file_path = os.path.join(reviewed_parquet_folder_path, file_name)

            # Read the parquet file into a dataframe
            onefile_df = pd.read_parquet(file_path)

            # Filter rows based on the "status" column
            filtered_df = onefile_df[onefile_df['status'].isin(['Non-relevant', 'Completed'])]

            # Append the filtered dataframe to the list
            result_df.append(filtered_df)

    # Concatenate all dataframes into a single dataframe
    return_df = pd.concat(result_df, ignore_index=True)
    return_df = return_df.rename(columns={'subject': 'subject_clean',
                                    'title_with_abstract': 'text_with_abstract'})
    
    # Create reviewed_target column using status column
    return_df['target'] = return_df['status'].apply(lambda x: 1 if x == "Completed" else 0)
    
    # Convert NaN to '' for preprocessing
    return_df['text_with_abstract'].fillna("", inplace=True)
    return_df['subject_clean'].fillna("", inplace=True)

    # Split into train/valid/test sets
    train_df, val_test_df = train_test_split(return_df, test_size=0.3, random_state=123)
    valid_df, test_df = train_test_split(val_test_df, test_size=0.5, random_state=123)
    
    logger.info(f'Data Loading - Reviewed new sample has {train_df.shape[0]}/{valid_df.shape[0]}/{test_df.shape[0]} in train/valid/test splits.')
    logger.info(f'Data Loading - Each new sample has {train_df.shape[1]} features.')

    return train_df, valid_df, test_df


def retrain_data_merge(old_train, new_train, old_valid, new_valid,old_test, new_test):
    '''
    Merge old splits with new splits.
    Return merged train, valid, test splits.

    Args:
        old_train (pd Dataframe)  Original traing split.
        new_train (pd Dataframe)  New traing split.
        old_valid (pd Dataframe)  Original validation split.
        new_valid (pd Dataframe)  New validation split.        
        old_test (pd Dataframe)  Original test split.
        new_test (pd Dataframe)  New test split.

    Return:
        Three pandas Data frames: train_df, valid_df, test_df
    '''

    # Concatenate the old and new training splits
    train_df = pd.concat([old_train, new_train], ignore_index=True)

    # Concatenate the old and new validation splits
    valid_df = pd.concat([old_valid, new_valid], ignore_index=True)

    # Concatenate the old and new test splits
    test_df = pd.concat([old_test, new_test], ignore_index=True)

    logger.info(f'Data Loading - Final training sample has {train_df.shape[0]}/{valid_df.shape[0]}/{test_df.shape[0]} in train/valid/test splits.')
    logger.info(f'Data Loading - Each merged sample has {train_df.shape[1]} features.')

    return train_df, valid_df, test_df


def model_train(train_df, model_dir, model_c = 0.01563028103558011):
    '''
    Train logistic regression with specified C hyperparameter value.
    Return and save the trained model.

    Args:
        train_df (pd Dataframe)  Training data.
        model_c (float)  Hyperparamter C value.
        model_dir (str) Path to where the trained model will be saved.

    Return:
        Scikit learn logistic regression model.
    '''

    # ======== Ensure feature values are valid ===========
    if train_df['has_abstract'].isna().any():
        raise ValueError(f"Column 'has_abstract' contains NaN values.")
    if train_df['is-referenced-by-count'].isna().any():
        raise ValueError(f"Column 'is-referenced-by-count' contains NaN values.")
    if train_df['text_with_abstract'].isna().any():
        raise ValueError(f"Column 'text_with_abstract' contains NaN values.")
    if train_df['target'].isna().any():
        raise ValueError(f"Column 'target' contains NaN values.")
    
    # ======= only keep feature columns ==========
    keep_col = ['target', 'has_abstract', 'subject_clean', 'is-referenced-by-count'] + [str(i) for i in range(0,768)]
    columns_to_drop = set(train_df.columns) - set(keep_col)
    train_df = train_df.drop(columns=columns_to_drop)

    # ======== Train start ==========
    # split x and y
    X_train, y_train = train_df.drop(columns = ["target"]), train_df["target"]

    # Dividing the feature types
    text_features = "subject_clean"
    text_transformer = CountVectorizer(stop_words="english", max_features= 1000)

    binary_feature = ['has_abstract']
    binary_transformer = OneHotEncoder(drop='if_binary', dtype = int)

    numeric_features = ["is-referenced-by-count"]
    numeric_transformer = StandardScaler()

    # Create the column transformer
    preprocessor = ColumnTransformer(
        transformers = [
        ("num_preprocessor", numeric_transformer, numeric_features),
        ("binary_preprocessor", binary_transformer, binary_feature),
        ("text_preprocessor", text_transformer, text_features)
        ],
        remainder = "passthrough"
    )

    # train model with tuned hyperparameter
    logreg_model = make_pipeline(preprocessor, 
                                 LogisticRegression(class_weight = 'balanced', 
                                                    max_iter=10000, 
                                                    random_state=123, 
                                                    C=model_c))
    
    logreg_model.fit(X_train, y_train)

    # save the model with current data time
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%dT%H-%M-%S")

    model_file_name = os.path.join(model_dir, f"retrained_model_{formatted_datetime}.joblib")
    joblib.dump(logreg_model, model_file_name)

    return logreg_model


def model_eval(model, valid_df, test_df, report_dir):
    '''
    Generate ROC plot to show effect of threshold on recall and precision,
    and generate a short json file with: 
    - recall, precision, confusion matrix on validation set using various threshold
    - recall and precision on test set using default 0.5 threshold
    '''

    # ======= Only keep feature columns ==========
    keep_col = ['target', 'has_abstract', 'subject_clean', 'is-referenced-by-count'] + [str(i) for i in range(0,768)]
    columns_to_drop = set(valid_df.columns) - set(keep_col)
    valid_df = valid_df.drop(columns=columns_to_drop)
    test_df = test_df.drop(columns=columns_to_drop)

    # ======== Split ==========
    # split x and y
    X_valid, y_valid = valid_df.drop(columns = ["target"]), valid_df["target"]
    X_test, y_test = test_df.drop(columns = ["target"]), test_df["target"]

    # === ROC plot ====
    fpr, tpr, thresholds = roc_curve(y_valid, model.predict_proba(X_valid)[:, 1])
    plt.plot(fpr, tpr, label="ROC Curve")
    plt.xlabel("FPR")
    plt.ylabel("TPR (recall)")

    default_threshold = np.argmin(np.abs(thresholds - 0.5))

    plt.plot(
        fpr[default_threshold],
        tpr[default_threshold],
        "or",
        markersize=10,
        label="threshold 0.5",
    )
    plt.legend(loc="best")

    # save the model with current datetime
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%dT%H-%M-%S")

    plot_file_name = os.path.join(report_dir, f"retrained_model_{formatted_datetime}_ROC-curve.png")
    plt.savefig(plot_file_name)


    # json for validation and test set performance
    results = {}

    def threshold_adj(thld = 0.5):
        proba = model.predict_proba(X_valid)[:, 1]
        predictions = np.array([1 if prob > thld else 0 for prob in proba])
        TN, FP, FN, TP = confusion_matrix(y_valid, predictions).ravel()
        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
        f1_score = (2 * precision * recall) / (precision + recall)
        print(f"(threshold = {thld}) validation set's precision = {round(precision, 3)}, recall = {round(recall, 3)} & f1 = {round(f1_score, 3)}")
        print(f"False negative = {FN}, False positive = {FP}")
        print(f"True negative = {TN}, True positive = {TP}")

    threshold_adj(thld = 0.6)
    threshold_adj(thld = 0.5)
    threshold_adj(thld = 0.4)
    threshold_adj(thld = 0.3)


def main():
    pass

