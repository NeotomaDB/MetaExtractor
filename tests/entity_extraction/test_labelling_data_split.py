# Author: Ty Andrews,
# Date:2023-05-31
from __future__ import unicode_literals
import os
import sys
from distutils import dir_util
from pytest import fixture
import pytest
import logging

logger = logging.getLogger(__name__)

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.preprocessing.labelling_data_split import separate_labels_to_train_val_test


# testing setup inspiration from: https://stackoverflow.com/questions/29627341/pytest-where-to-store-expected-data
@fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


# test that after running the function, the output folder contains the correct number of files
def test_labelling_data_split(datadir):
    separate_labels_to_train_val_test(
        labelled_file_path=str(datadir),
        output_path=str(datadir) + "/processed",
        train_split=0.34,
        val_split=0.33,
        test_split=0.33,
        seed=42,
    )

    # check the folder exists
    assert os.path.exists(datadir.join("/processed/train"))
    assert os.path.exists(datadir.join("/processed/val"))
    assert os.path.exists(datadir.join("/processed/test"))

    # print the contents of the output folder
    print("Files in train: ", os.listdir(datadir.join("/processed/train")))
    print("Files in val: ", os.listdir(datadir.join("/processed/val")))
    print("Files in test: ", os.listdir(datadir.join("/processed/test")))
    # # check the folder contains one file each
    assert len(os.listdir(datadir.join("/processed/train"))) == 1
    assert len(os.listdir(datadir.join("/processed/val"))) == 1
    assert len(os.listdir(datadir.join("/processed/test"))) == 1


# test that invalid train/test splits raise an error
def test_labelling_data_split_invalid_splits(datadir):
    with pytest.raises(ValueError):
        separate_labels_to_train_val_test(
            labelled_file_path=str(datadir),
            output_path=str(datadir) + "/processed",
            train_split=0.1,
            val_split=0.1,
            test_split=0.1,
            seed=42,
        )


# test that a non-existent folder raises an error
def test_labelling_data_split_non_existent_folder(datadir):
    with pytest.raises(FileNotFoundError):
        separate_labels_to_train_val_test(
            labelled_file_path=str(datadir) + "/non_existent_folder",
            output_path=str(datadir) + "/processed",
            train_split=0.34,
            val_split=0.33,
            test_split=0.33,
            seed=42,
        )
