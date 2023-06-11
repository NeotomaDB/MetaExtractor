import dash
from dash import dash_table
import json
import os
import pandas as pd
from dash.dependencies import Input, Output, State
dash.register_page(__name__, path="/")

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pages.config import *
suppress_callback_exceptions = True

def layout():


    directories = [os.path.join("data", "data-review-tool", dir) for dir in ["completed", "raw"]]

    # Initialize an empty dictionary to store the dataframes
    dfs = {}

    # Iterate through the directories
    for directory in directories:
        # List all files in the directory
        files = os.listdir(directory)
        # Filter JSON files
        json_files = [file for file in files if file.endswith('.json')]
        # Read each JSON file into a dataframe and store it in the dictionary
        for file in json_files:
            file_path = os.path.join(directory, file)
            article = open(file_path, "r")
            df = pd.json_normalize(json.loads(article.read()))
            # Only keep the dataframe if the file is not already in the dictionary
            if file not in dfs:
                dfs[file] = df
    # Combine all dataframes into a single dataframe
    combined_df = pd.concat(list(dfs.values()), ignore_index=True)

    combined_df = combined_df[["title", "doi", "gddid", "status", "date_processed", "last_updated"]].rename(
            columns={"title": "Article", 
                    "doi": "DOI", 
                    "status": "Status", 
                    "date_processed": "Date Added",
                    "last_updated": "Date Updated"}
        )
    combined_df["Review"] = "Review"

    current = combined_df.query("Status == 'False' | Status =='In Progress'")
    completed = combined_df[combined_df["Status"] == "Completed"]
    nonrelevant = combined_df[combined_df["Status"] == "Non-relevant"]
    

    layout = html.Div(
        dbc.Col([
            dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            get_article_tab("Current Articles", current),
                            get_article_tab("Completed Articles", completed),
                            get_article_tab("Irrelevant Articles", nonrelevant),
                        ],
                        position="apart"
                    ),
                    get_article_table("current_table", "location_current", "Current Articles", current),
                    get_article_table("completed_table", "location_completed", "Completed Articles", completed),
                    get_article_table("irrelevant_table", "location_irrelevant", "Irrelevant Articles", nonrelevant),
                ],
                id="article-tabs",
                color="blue",
                orientation="horizontal",
                value="Current Articles",
            ),
        ],
        width=10,
        style = {'margin-left': 'auto', 'margin-right': 'auto'}
        )
    )
    return layout

@callback(
    Output("location_current", "href"),
    Input("current_table", "active_cell"),  
    State("current_table", "derived_viewport_data"),
)

def current_article_clicked(active_cell_current, data):
    if active_cell_current:
        row = active_cell_current["row"]
        col = active_cell_current["column_id"]
        if col == "Review":  # or whatever column you want
            selected = data[row]["gddid"]
            return f"http://127.0.0.1:8050/article/{selected}"
        else:
            return dash.no_update

@callback(
    Output("location_completed", "href"),
    Input("completed_table", "active_cell"),
    State("completed_table", "derived_viewport_data"),
)
def completed_article_clicked(active_cell_completed, data):
    if active_cell_completed:
        row = active_cell_completed["row"]
        col = active_cell_completed["column_id"]
        if col == "Review":  # or whatever column you want
            selected = data[row]["gddid"]
            return f"http://127.0.0.1:8050/article/{selected}"
        else:
            return dash.no_update
    
@callback(
    Output("location_irrelevant", "href"),
    Input("irrelevant_table", "active_cell"),
    State("irrelevant_table", "derived_viewport_data"),
)
def irrelevant_article_clicked(active_cell_nonrelevant, data):        
    if active_cell_nonrelevant:
        row = active_cell_nonrelevant["row"]
        col = active_cell_nonrelevant["column_id"]
        if col == "Review":  # or whatever column you want
            selected = data[row]["gddid"]
            return f"http://127.0.0.1:8050/article/{selected}"
        else:
            return dash.no_update
        
def get_article_tab(tab_header, data):
    return dmc.Tab(
            children=dmc.Text(tab_header,
                                style=tab_header_style),
            value=tab_header,
            rightSection=dmc.Badge(
                f"{data.shape[0]}",
                p=0,
                variant="filled",
                style=badge_style,
                sx={"width": 20, "height": 20, "pointerEvents": "none"}),
    )
    
def get_article_table(table_id, location_id, tab_header, data):
    return dmc.TabsPanel(
            html.Div([
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
                    style_table={'overflowX': 'auto',
                                    "padding-top": "20px",},
                    style_cell=table_cell_style,
                    style_header=table_header_style,
                ),
                dcc.Location(id=location_id, refresh=True),
            ],
                style=tab_body_style),
            value=tab_header
        )