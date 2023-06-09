# Author: Shaun Hutchinson,
# Date: 2023-06-22
import pytest
import sys
import os

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

os.environ["ARTICLE_RELEVANCE_BATCH"] = "article-relevance-output.parquet"
os.environ["ENTITY_EXTRACTION_BATCH"] = "entity-extraction-output.zip"

from src.data_review_tool.app import *
from src.data_review_tool.pages.article_review import *


def test_collapse():
    """Test that the collapse function returns None when the no accordion is clicked."""
    assert collapse(True) == None


def test_cell_clicked():
    "Test that the cell_clicked function returns the correct value when a cell is clicked."
    assert cell_clicked(1) == "/"
    assert cell_clicked(0) == dash.no_update


def test_update_button():
    "Test that the update_button function returns correct children for Delete or Restore."
    assert update_button(True)[0].children == "Delete Entity"
    assert update_button(False)[0].children == "Restore Entity"


def test_chips_values():
    "Test that the chips_values function returns the correct values."
    site = "test"
    taxa, region, geog, alti, age, email = None, None, None, None, None, None
    accordian = "SITE"
    data = {"entities": {"SITE": {"test": {"corrected_name": "test"}}}}

    assert chips_values(
        site, taxa, region, geog, alti, age, email, accordian, data
    ) == ("test", False, False, "test")


def test_enable_correct_button():
    "Test that the enable_correct_button function returns the correct values."
    assert enable_correct_button("Pinus") == False
