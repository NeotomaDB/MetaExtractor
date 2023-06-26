# Author: Shaun Hutchinson,
# Date: 2023-06-22
from dash._utils import AttributeDict
from dash import html, dash_table
import dash_mantine_components as dmc
import pandas as pd
import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Import the names of callback functions you want to test
from src.data_review_tool.app import *
from src.data_review_tool.pages.home import *
from src.data_review_tool.pages.config import *


def test_directory_structure():
    "test that the data directory structure is correct"
    dir = "data/data-review-tool"
    expected = ["processed", "raw"]

    assert sorted(os.listdir(dir)) == expected


def test_current_article_clicked():
    "test that clicking 'Review' button redirects to the correct article"
    active_cell_current = AttributeDict({"row": 0, "column_id": "Review"})
    current_data = [{"gddid": "1234", "Review": "Review"}]
    active_cell_completed = None
    completed_data = None
    active_cell_nonrelevant = None
    nonrelevant_data = None

    # Create the expected output
    expected = "/article/1234"
    assert (
        current_article_clicked(
            active_cell_current,
            current_data,
            active_cell_completed,
            completed_data,
            active_cell_nonrelevant,
            nonrelevant_data,
        )
        == expected
    )


def test_get_article_tab():
    """Test that the tab is created correctly"""
    tab_header = "Current"
    data = pd.DataFrame({"gddid": ["1234", "5678"]})

    # Create the expected output
    expected = dmc.Tab(
        children=dmc.Text(tab_header, style=tab_header_style),
        value=tab_header,
        rightSection=dmc.Badge(
            f"{data.shape[0]}",
            p=0,
            variant="filled",
            style=badge_style,
            sx={"width": 20, "height": 20, "pointerEvents": "none"},
        ),
    )

    assert (
        get_article_tab(tab_header, data).rightSection.children
        == expected.rightSection.children
    )
    assert get_article_tab(tab_header, data).value == expected.value


def test_get_article_table():
    """Test that the table is created correctly"""
    table_id = "current-table"
    location_id = "current-table-location"
    tab_header = "Current Articles"
    data = pd.DataFrame({"gddid": ["1234", "5678"]})

    expected = dmc.TabsPanel(
        html.Div(
            [
                dash_table.DataTable(
                    id=table_id,
                    filter_action="native",
                    sort_action="native",
                    page_action="native",
                    page_size=10,
                    style_data=table_data_style,
                    filter_options={"placeholder_text": ""},
                    columns=[{"name": i, "id": i} for i in data.columns],
                    data=data.to_dict("records"),
                    style_data_conditional=table_conditional_style,
                    style_table={
                        "overflowX": "auto",
                        "padding-top": "20px",
                    },
                    style_cell=table_cell_style,
                    style_header=table_header_style,
                ),
                dcc.Location(id=location_id, refresh=True),
            ],
            style=tab_body_style,
        ),
        value=tab_header,
    )
    assert (
        get_article_table(table_id, location_id, tab_header, data).value
        == expected.value
    )
