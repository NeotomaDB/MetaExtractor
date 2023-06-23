# Author: Shaun Hutchinson,
# Date: 2023-06-22
from dash._callback_context import context_value
from dash._utils import AttributeDict
from dash import html, dash_table
import dash_mantine_components as dmc
from dash.testing.browser import Browser
import pytest
import sys
import os

# ensure that the parent directory is on the path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data_review_tool.app import *
from src.data_review_tool.pages.article_review import *


def test_collapse():
    """Test that the collapse function returns None when the no accordion is clicked."""
    assert collapse(True) == None


def test_cell_clicked():
    "Test that the cell_clicked function returns the correct value when a cell is clicked."
    assert cell_clicked(1) == "/"
    assert cell_clicked(0) == dash.no_update


def test_directory_structure():
    "Test that the directory structure is as expected."
    dir = "data/data-review-tool"
    expected = ["processed", "raw"]
    assert sorted(os.listdir(dir)) == expected


def test_find_start_end_char():
    "Test that the find_start_end_char function returns the correct values."
    text = "This is a test"
    entity = "test"
    assert find_start_end_char(text, entity) == (10, 14)


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


def test_update_chips():
    "Test that the update_chips function returns the correct values."
    deleted = False
    data = {"entities": {"SITE": {"test": {"corrected_name": "test"}}}}

    assert update_chips(deleted, data)[0] == "test"
