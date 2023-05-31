import dash

dash.register_page(__name__,  path_template="/article/<gddid>")

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd

np.random.seed(2020)

def layout(gddid = None):
    metadata = pd.read_json(f"data/labelled/{gddid}.json")
    metadata = pd.DataFrame(metadata.loc[0, "data"], index=metadata.index).reset_index(drop=True)
    layout = html.Div(
        [   
            html.P("Article: " + metadata["title"][0]),
            html.P("DOI: "+ metadata["doi"][0]),
            html.A("URL: doi.org/" + metadata["doi"][0], href="http://doi.org/" + metadata["doi"][0], target="_blank"),
            dcc.Graph(id="histograms-graph"),
            html.P("Mean:"),
            dcc.Slider(
                id="histograms-mean", min=-3, max=3, value=0, marks={-3: "-3", 3: "3"}
            ),
            html.P("Standard Deviation:"),
            dcc.Slider(id="histograms-std", min=1, max=3, value=1, marks={1: "1", 3: "3"}),
        ]
    )
    return layout

@callback(
    Output("histograms-graph", "figure"),
    Input("histograms-mean", "value"),
    Input("histograms-std", "value"),
)
def display_color(mean, std):
    data = np.random.normal(mean, std, size=500)
    fig = px.histogram(data, nbins=30, range_x=[-10, 10])
    return fig


