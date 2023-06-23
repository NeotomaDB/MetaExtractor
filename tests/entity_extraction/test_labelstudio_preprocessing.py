# Author: Ty Andrews
# Date: 2023-06-02

import os, sys

import json
import pytest

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.entity_extraction.training.hf_token_classification.huggingface_preprocess import (
    convert_labelled_data_to_hf_format,
)


# test that a nonexistant folder raises an error
def test_nonexistant_folder_raises_error():
    with pytest.raises(FileNotFoundError):
        convert_labelled_data_to_hf_format("data/labelled/nonexistant_folder")


# test that a folder without train/test/val raises an error
# create temporary folders for just train/val
def test_folder_without_train_test_val_raises_error(tmp_path):
    # create a folder with just train/val
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "train").mkdir()
    (folder / "val").mkdir()

    with pytest.raises(FileNotFoundError):
        convert_labelled_data_to_hf_format(folder)


# test that the function processes the data correctly
def test_process_labelled_data(tmp_path):
    folder_path = str(tmp_path)

    train_folder = os.path.join(folder_path, "train")
    test_folder = os.path.join(folder_path, "test")
    val_folder = os.path.join(folder_path, "val")

    os.makedirs(train_folder)
    os.makedirs(test_folder)
    os.makedirs(val_folder)

    sample_data = {
        "task": {"data": {"text": "Sample text", "gdd_id": "sample_id"}},
        "result": [
            {
                "id": "OXpADMYGB3",
                "type": "labels",
                "value": {
                    "end": 63,
                    "text": "Neogene Mediterranean",
                    "start": 42,
                    "labels": ["REGION"],
                },
                "origin": "prediction",
                "to_name": "text",
                "from_name": "label",
            }
        ],
    }

    with open(os.path.join(train_folder, "123.txt"), "w") as f:
        json.dump(sample_data, f)

    with open(os.path.join(test_folder, "456.txt"), "w") as f:
        json.dump(sample_data, f)

    with open(os.path.join(val_folder, "789.txt"), "w") as f:
        json.dump(sample_data, f)

    convert_labelled_data_to_hf_format(folder_path)

    assert os.path.exists(os.path.join(folder_path, "train.json"))
    assert os.path.exists(os.path.join(folder_path, "test.json"))
    assert os.path.exists(os.path.join(folder_path, "val.json"))
