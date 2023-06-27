import dash
from dash import dash_table
import json
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
from dash.dependencies import Input, Output, State

dash.register_page(__name__, path="/")

from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pages.config import *

suppress_callback_exceptions = True

article_relevance_data_path = os.path.join(
    "/MetaExtractor",
    "inputs",
    os.environ["ARTICLE_RELEVANCE_BATCH"]
)

def layout():    
    combined_df = load_data(f"/entity_extraction/")
    combined_df["Review"] = "Review"
    
    current = combined_df.query("Status == 'False' | Status =='In Progress'")
    completed = combined_df[combined_df["Status"] == "Completed"]
    nonrelevant = combined_df[combined_df["Status"] == "Non-relevant"]

    layout = html.Div(
        dbc.Col(
            [
                dmc.Tabs(
                    [
                        dmc.TabsList(
                            [
                                get_article_tab("Current Articles", current),
                                get_article_tab("Completed Articles", completed),
                                get_article_tab("Irrelevant Articles", nonrelevant),
                            ],
                            position="apart",
                        ),
                        get_article_table(
                            "current_table",
                            "location_current",
                            "Current Articles",
                            current,
                        ),
                        get_article_table(
                            "completed_table",
                            "location_completed",
                            "Completed Articles",
                            completed,
                        ),
                        get_article_table(
                            "irrelevant_table",
                            "location_irrelevant",
                            "Irrelevant Articles",
                            nonrelevant,
                        ),
                    ],
                    id="article-tabs",
                    color="blue",
                    orientation="horizontal",
                    value="Current Articles",
                ),
            ],
            width=10,
            style={
                "margin-left": "auto",
                "margin-right": "auto",
                "max-width": "100%",
                "word-wrap": "break-word",
            },
        )
    )
    return layout


@callback(
    Output("location_current", "href"),
    Input("current_table", "active_cell"),
    State("current_table", "derived_viewport_data"),
    Input("completed_table", "active_cell"),
    State("completed_table", "derived_viewport_data"),
    Input("irrelevant_table", "active_cell"),
    State("irrelevant_table", "derived_viewport_data"),
)
def current_article_clicked(
    active_cell_current,
    current_data,
    active_cell_completed,
    completed_data,
    active_cell_nonrelevant,
    nonrelevant_data,
):
    """Get the URL of the article that was clicked on for each data table

    Args:
        active_cell_current (dict): The active cell of the current articles table
        current_data (dict): The data of the current articles table
        active_cell_completed (dict): The active cell of the completed articles table
        completed_data (dict): The data of the completed articles table
        active_cell_nonrelevant (dict): The active cell of the nonrelevant articles table
        nonrelevant_data (dict): The data of the nonrelevant articles table

    Returns:
        str: The URL of the article that was clicked on
    """
    for active_cell, data in [
        (active_cell_current, current_data),
        (active_cell_completed, completed_data),
        (active_cell_nonrelevant, nonrelevant_data),
    ]:
        if active_cell:
            row = active_cell["row"]
            col = active_cell["column_id"]
            if col == "Review":
                selected = data[row]["gddid"]
                return f"/article/{selected}"
            else:
                return dash.no_update


def get_article_tab(tab_header, data):
    """Get the tab for the specified article table

    Args:
        tab_header (str): The header of the tab
        data (pandas.DataFrame): The data for the table

    Returns:
        dash_mantine_components.Tab: The tab for the specified article table
    """
    return dmc.Tab(
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


def get_article_table(table_id, location_id, tab_header, data):
    """Get the table for the specified article table

    Args:
        table_id (str): The ID of the table
        location_id (str): The ID of the location
        tab_header (str): The header of the tab
        data (pandas.DataFrame): The data for the table

    Returns:
        dash_mantine_components.TabsPanel: The table for the specified article table
    """
    return dmc.TabsPanel(
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

def load_data(directory):
    """Read the articles from the entity extraction directory \
       and adds relevant article metadata to it

    Args:
        directory (str): dirtectory to read the articles from

    Returns:
        pandas.DataFrame: The articles in the directory
    """
    
    articles = read_entities(directory)
    filtered_df = add_article_metadata(articles)
    combined_df = pd.merge(articles, filtered_df, on="gddid", how='left')
    combined_df = combined_df[["Article", "DOI", "gddid", "Status", "Date Added", "Date Updated"]]
    
    return combined_df
    
def read_entities(directory):
    """Reads the extracted data from all articles under the specified directory

    Parameter
    ---------
    directory: str 
        dirtectory to read the articles from

    Returns
    -------
    pandas.DataFrame: The articles in the directory
    """
    try:
        # Initialize an empty dictionary to store the 
        # data for all the articles
        dfs = {}

        files = os.listdir(directory)
        # Filter JSON files
        json_files = [file for file in files if file.endswith(".json")]
        # Read each JSON file into a dataframe and store it in the dictionary
        for file in json_files:
            file_path = os.path.join(directory, file)
            article = open(file_path, "r")
            df = pd.json_normalize(json.loads(article.read()))
            # Only keep the data if the file is not already in the dictionary
            if file not in dfs:
                dfs[file.split(".")[0]] = df
        
        # Combine all dataframes into a single dataframe
        df = pd.concat(list(dfs.values()), ignore_index=True)
        df = df[['gddid', 'date_processed',]].rename(
            columns={"date_processed": "Date Added"}
        )
    except ValueError as e:
        print(str(e))
        df = pd.DataFrame(
            columns=[
                "gddid",
                "Date Added",
            ]
        )
    return df

def add_article_metadata(df):
    """Retreive article metadata

    Parameter
    ---------
    df: pd.DataFrame
        Data frame containing gddid and entities from an article

    Returns
    -------
    filtered_df: pd.DataFrame
        metadata for articles relevant for the UI 
    """
    gddid = df['gddid'].tolist()
    
    schema = pq.read_schema(article_relevance_data_path)
    # Read the Parquet file with pushdown predicate
    results = pd.read_parquet(article_relevance_data_path)

    if "status" not in results.columns:
        results["status"] = "False"
        schema = schema.append(pa.field('status', pa.string())) # False, In Progress, Non-relevant, Completed
    # TODO: improve the following 2 datatypes for the future
    if "last_updated" not in results.columns:
        results["last_updated"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        schema = schema.append(pa.field('last_updated', pa.string())) # Date in string format
    if "corrected_entities" not in results.columns:
        results["corrected_entities"] = "None"
        schema = schema.append(pa.field('corrected_entities', pa.string())) # JSON in string format

    results.to_parquet(article_relevance_data_path, schema=schema)
    
    filtered_df = results[results['gddid'].isin(gddid)].rename(
        columns={
            "status": "Status",
            "title": "Article", 
            "doi": "DOI",
            "last_updated": "Date Updated"
        }
    )

    return filtered_df
