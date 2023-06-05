import dash
from dash import dash_table
import json
import os
import pandas as pd
from dash.dependencies import Input, Output, State
import webbrowser
dash.register_page(__name__, path="/")

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc

suppress_callback_exceptions = True

# Set the directory path
directory_path = "data/labelled/"
# Get a list of all files and directories in the directory
files_and_directories = os.listdir(directory_path)
# Filter out the directories to get only the files
files = [file for file in files_and_directories if os.path.isfile(os.path.join(directory_path, file))]
if '.gitkeep' in files:
    files.remove('.gitkeep')
if '.DS_Store' in files:
    files.remove('.DS_Store')
    

# initialize empty dataframe
df = pd.DataFrame()

# Populate the cross ref df
for f in files:
    file = open(f"data/labelled/{f}", "r")
    onefile = pd.json_normalize(json.loads(file.read()))
    
    # merge
    df = pd.concat([df, onefile])
df = df[["title", "doi", "status", "date_processed", "last_updated", "gddid"]].rename(
        columns={"title": "Article", "doi": "DOI", "status": "Status", "date_uploaded": "Date Added", "last_updated": "Date Updated"}
    )
df["Review"] = "Review"

current = df[df["Status"] == "False"]
completed = df[df["Status"] == "True"]

# columns = ["title", "doi", "status", "date_uploaded", "date_modified"]       

layout = html.Div(
    [
        html.H2("Current Articles",
                style={'textAlign': 'center'}),
        html.Br(),
        dash_table.DataTable(
            id="current_table",
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },
            # fixed_rows={'headers': True},
            columns=[{"name": i, "id": i} for i in current.columns],
            data=current.to_dict("records"),
            # is_focused=True,
            style_data_conditional=[
                {'if': {'column_id': 'Review'}, 'backgroundColor': 'blue', 'text_align':'center','color': 'white'},
                {'if': {'column_id': 'Status'},'fontWeight': 'bold'},
                                   ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
        ),
        dcc.Location(id='location_current'),
        html.Br(),
        html.Br(),
        html.H2("Current Articles",
                style={'textAlign': 'center'}),
        html.Br(),
        dash_table.DataTable(
            id="completed_table",
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            },
            # fixed_rows={'headers': True},
            columns=[{"name": i, "id": i} for i in completed.columns],
            data=completed.to_dict("records"),
            # is_focused=True,
            style_data_conditional=[
                {'if': {'column_id': 'Review'}, 'backgroundColor': 'blue', 'text_align':'center','color': 'white'},
                {'if': {'column_id': 'Status'},'fontWeight': 'bold'},
                                   ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
        ),
        html.Div(id='dummy-div', style={'display': 'none'}),
        dcc.Location(id='location_completed'),
    
    ]
)

@callback(
    Output("location_current", "href"),
    Input("current_table", "active_cell"),  
    State("current_table", "derived_viewport_data"),
)

# @callback(Output('dummy-div', 'children'), [Input('current_table', 'active_cell'), Input('completed_table', 'active_cell')])

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