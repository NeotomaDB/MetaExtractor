import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import json

dash.register_page(__name__,  path_template="/article/<gddid>")

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd
from pages.navbar import segment_control

np.random.seed(2020)

def layout(gddid = None):
    # metadata = pd.read_json(f"data/labelled/{gddid}.json")
    # metadata = pd.DataFrame(metadata.loc[0, "data"], index=metadata.index).reset_index(drop=True)
    file = open(f"data/labelled/{gddid}.json", "r")
    metadata = pd.json_normalize(json.loads(file.read()))
    # styling the sidebar
    SIDEBAR_STYLE = {
        # "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        # "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
    }

    # padding for the page content
    CONTENT_STYLE = {
        # "margin-left": "18rem",
        # "margin-right": "2rem",
        "padding": "0.3rem 0.3rem",
    }
    sidebar = html.Div(
        [
            dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Site Name"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                x["name"],
                                                value = x["name"],
                                                variant="outline",
                                            )
                                            for x in metadata["entities.SITE"][0]
                                        ],
                                        id="chips_site",  
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="site_name",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Region Name"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                x["name"],
                                                value = x["name"],
                                                variant="outline",
                                            )
                                            for x in metadata["entities.REGION"][0]
                                        ],
                                        id="chips_region",  
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="region_name",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Taxa"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                x["name"],
                                                value = x["name"],
                                                variant="outline",
                                            )
                                            for x in metadata["entities.TAXA"][0]
                                        ],
                                        id="chips_taxa",  
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="taxa",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Geographic Coordinates"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                x["name"],
                                                value = x["name"],
                                                variant="outline",
                                            )
                                            for x in metadata["entities.GEOG"][0]
                                        ],
                                        id="chips_geog",  
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="geog",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Altitude"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                x["name"],
                                                value = x["name"],
                                                variant="outline",
                                            )
                                            for x in metadata["entities.ALTI"][0]
                                        ],
                                        id="chips_alti",  
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="alti",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Age"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                x["name"],
                                                value = x["name"],
                                                variant="outline",
                                            )
                                            for x in metadata["entities.AGE"][0]
                                        ],
                                        id="chips_age",  
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="age",
                    ),
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Email Address"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                x["name"],
                                                value = x["name"],
                                                variant="outline",
                                            )
                                            for x in metadata["entities.EMAIL"][0]
                                        ],
                                        id="chips_email",  
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="email",
                    ),
                ],
            ),
            html.Br(),
            dmc.Textarea(
                label="Reviewer's Comments",
                placeholder="Reviewer's Comments",
                autosize=True,
            ),
            html.Br(),
            dmc.Group(
                [
                    dmc.Button("Submit", color="green"),
                    dmc.Button("Save Progress", color="green", variant="outline")
                ],
            )    
        ],
        style=SIDEBAR_STYLE,
    )
    
    content = html.Div(
        [
            dbc.Row(
                [
                    dmc.Group(
                        [
                            html.P("Entity text:"),
                            dmc.Button("Homo sampiens", color = "black", variant = "outline"),
                            dmc.TextInput(label="Corrected Entity:", style={"width": 200}, error=True)
                        ],
                    ),
                ],
            ),
            dmc.SegmentedControl(
                id="segmented",
                data=segment_control(metadata, "ca. 12 001 BP"),
                fullWidth=True,
                
                
            ),
            dcc.Graph(id="histograms-graph"),
            html.P("Mean:"),
            dcc.Slider(
                id="histograms-mean", min=-3, max=3, value=0, marks={-3: "-3", 3: "3"}
            ),
            html.P("Standard Deviation:"),
            dcc.Slider(id="histograms-std", min=1, max=3, value=1, marks={1: "1", 3: "3"}),
            ], style=CONTENT_STYLE)
    
    layout = html.Div(
        [   
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P("Article: " + metadata["title"][0]),
                            html.A("DOI: doi.org/" + metadata["doi"][0], href="http://doi.org/" + metadata["doi"][0], target="_blank"),
                            html.P("Journal: " + metadata["journal_name"][0]),
                        ],
                    ),
                    dbc.Col(
                        [
                            html.P("Is this article relevant to NeotomaDB?"),
                            dmc.Group(
                                [
                                    dmc.Button("Yes", color="green", variant="outline"),
                                    dmc.Button("No", color="red", variant="outline"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Br(),
            dbc.Row(
                [
                    
                    dbc.Col(sidebar, width=12, lg=3, className="g-0"),
                    dbc.Col(content, width=12, lg=9, className="g-0"),
                ],
            ),
        ],
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


