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


    directories = ["data/data-review-tool/completed/", "data/data-review-tool/raw/"]

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
            dmc.Tabs([
                dmc.TabsList(
                    [
                        dmc.Tab(
                            dmc.Text("Current Articles",
                                     style={"font-weight": "bold",
                                            "font-size": "25px",
                                            "font-family": "Lato",
                                            "padding-top": "20px",
                                            "padding-bottom": "10px"}),
                            "Current Articles",
                            rightSection=dmc.Badge(
                                f"{current.shape[0]}",
                                p=0,
                                variant="filled",
                                style={
                                    "background-color": "#F4C430",
                                    "font-size": "15px",
                                    "font-weight": "exta-bold",},
                                sx={"width": 20, "height": 20, "pointerEvents": "none"}),
                        ),
                        dmc.Tab(
                            dmc.Text("Completed Articles",
                                     style={"font-weight": "bold",
                                            "font-size": "25px",
                                            "font-family": "Lato",
                                            "padding-top": "20px",
                                            "padding-bottom": "10px"}),
                            "Completed Articles",
                            rightSection=dmc.Badge(
                                f"{completed.shape[0]}",
                                p=0,
                                variant="filled",
                                style={
                                    "background-color": "#F4C430",
                                    "font-size": "15px",
                                    "font-weight": "exta-bold",},
                                sx={"width": 20, "height": 20, "pointerEvents": "none"},
                            ),
                        ),
                        dmc.Tab(
                            dmc.Text("Irrelevant Articles",
                                     style={"font-weight": "bold",
                                            "font-size": "25px",
                                            "font-family": "Lato",
                                            "padding-top": "10px",
                                            "padding-bottom": "10px"}),
                            "Irrelevant Articles",
                            rightSection=dmc.Badge(
                                f"{nonrelevant.shape[0]}",
                                p=0,
                                variant="filled",
                                style={
                                    "background-color": "#F4C430",
                                    "font-size": "15px",
                                    "font-weight": "exta-bold",},
                                sx={"width": 20, "height": 20, "pointerEvents": "none"}),
                        ),
                    ],
                    position="apart"
                ),
                    dmc.TabsPanel(
                        html.Div([
                            dash_table.DataTable(
                                id="current_table",
                                filter_action="native",
                                sort_action="native",
                                page_action="native",
                                page_size=10,
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '15px',
                                    'font-family': 'montserrat',
                                },
                                filter_options={"placeholder_text": ""},
                                columns=[{"name": i, "id": i} for i in current.columns],
                                data=current.to_dict("records"),
                                style_data_conditional=[
                                    {'if': {'column_id': 'Review'}, 
                                     'backgroundColor': 'blue', 
                                     'text_align':'center',
                                     'color': 'white',
                                     "font-weight": "700",
                                     'font-family': 'montserrat',},
                                    {'if': {'column_id': 'Article'}, 
                                     'text_align':'left',
                                     'font-family': 'montserrat',},
                                    {'if': {'column_id': 'Status'},
                                     'fontWeight': 'bold'},
                                ],
                                style_table={'overflowX': 'auto',
                                             "padding-top": "20px",},
                                style_cell={'textAlign': 'center',
                                            'font-family': 'montserrat',},
                                style_header={"text-align": "center",
                                              'font-family': 'montserrat',
                                              "font-weight": "bold"}
                            ),
                            dcc.Location(id='location_current'),
                        ],
                            style=tab_body_style),
                        value="Current Articles"
                    ),
                    dmc.TabsPanel(
                        html.Div([
                            dash_table.DataTable(
                                id="completed_table",
                                filter_action="native",
                                sort_action="native",
                                page_action="native",
                                page_size=10,
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '15px',
                                    'font-family': 'montserrat',
                                },
                                filter_options={"placeholder_text": ""},
                                columns=[{"name": i, "id": i} for i in completed.columns],
                                data=completed.to_dict("records"),
                                style_data_conditional=[
                                    {'if': {'column_id': 'Review'}, 
                                     'backgroundColor': 'blue', 
                                     'text_align':'center',
                                     'color': 'white',
                                     "font-weight": "700",
                                     'font-family': 'montserrat',},
                                    {'if': {'column_id': 'Article'}, 
                                     'text_align':'left',
                                     'font-family': 'montserrat',},
                                    {'if': {'column_id': 'Status'},
                                     'fontWeight': 'bold'},
                                ],
                                style_table={'overflowX': 'auto',
                                             "padding-top": "20px",},
                                style_cell={'textAlign': 'center',
                                            'font-family': 'montserrat',},
                                style_header={"text-align": "center",
                                              'font-family': 'montserrat',
                                              "font-weight": "bold"}
                            ),
                            dcc.Location(id='location_completed'),
                        ],
                            style=tab_body_style),
                        value="Completed Articles"
                    ),
                    dmc.TabsPanel(
                        html.Div([
                            dash_table.DataTable(
                                id="irrelevant_table",
                                filter_action="native",
                                sort_action="native",
                                page_action="native",
                                page_size=10,
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '15px',
                                    'font-family': 'montserrat',
                                },
                                filter_options={"placeholder_text": ""},
                                columns=[{"name": i, "id": i} for i in nonrelevant.columns],
                                data=nonrelevant.to_dict("records"),
                                style_data_conditional=[
                                    {'if': {'column_id': 'Review'}, 
                                     'backgroundColor': 'blue', 
                                     'text_align':'center',
                                     'color': 'white',
                                     "font-weight": "700",
                                     'font-family': 'montserrat',},
                                    {'if': {'column_id': 'Article'}, 
                                     'text_align':'left',
                                     'font-family': 'montserrat',},
                                    {'if': {'column_id': 'Status'},
                                     'fontWeight': 'bold'},
                                ],
                                style_table={'overflowX': 'auto',
                                             "padding-top": "20px",},
                                style_cell={'textAlign': 'center',
                                            'font-family': 'montserrat',},
                                style_header={"text-align": "center",
                                              'font-family': 'montserrat',
                                              "font-weight": "bold"}
                            ),
                            dcc.Location(id='location_irrelevant'),
                        ],
                            style=tab_body_style),
                        value="Irrelevant Articles"
                    ),],
                id="article-tabs",
                color="blue",
                orientation="horizontal",
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

def cell_clicked(active_cell_current, data):
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
def cell_clicked(active_cell_completed, data):        
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
def cell_clicked(active_cell_nonrelevant, data):        
    if active_cell_nonrelevant:
        row = active_cell_nonrelevant["row"]
        col = active_cell_nonrelevant["column_id"]
        if col == "Review":  # or whatever column you want
            selected = data[row]["gddid"]
            return f"http://127.0.0.1:8050/article/{selected}"
        else:
            return dash.no_update