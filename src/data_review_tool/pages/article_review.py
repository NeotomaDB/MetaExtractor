import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import json
from datetime import datetime

dash.register_page(__name__,  path_template="/article/<gddid>")

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd
from pages.navbar import df_denormalize

np.random.seed(2020)

def layout(gddid = None):
    try:
        # get the metadata of the article
        file = open(f"data/labelled/{gddid}.json", "r")
        metadata = pd.json_normalize(json.loads(file.read()))
    except FileNotFoundError:
        return html.Div(
    [
        html.H1("Error - gddid Not Found"),
        html.P("The requested gddid does not exist in the files."),
        html.P("Please check the article's gddid and try again."),
        dcc.Link("Go back to Home", href="/"),
    ]
)
            
        

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
                id = "accordion",
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
                                        value = [None],
                                        multiple = True,
                                    ),                              
                                ],                                                       
                            ),
                        ],
                        value="SITE",
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
                                        value = [None],
                                        multiple = True,
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="REGION",
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
                                        value = [None],
                                        multiple = True,
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="TAXA",
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
                                        value = [None],
                                        multiple = True,
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="GEOG",
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
                                        value = [None],
                                        multiple = True,
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="ALTI",
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
                                        value = [None],  
                                        multiple = True,
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="AGE",
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
                                        value = [None],
                                        multiple = True,
                                    ),
                                    
                                ],                                                       
                            ),
                        ],
                        value="EMAIL",
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
                    dmc.Button("Submit",
                               id="submit-button",
                               color="green"),
                    dmc.Button("Save Progress", 
                               id = "save-button",
                               color="green", 
                               variant="outline")
                ],
            ),
            dmc.Text(id="clicked-output", mt=10),    
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
                            dmc.Text(id="entity-text", style={"width": 200}),
                            dmc.TextInput(label="Corrected Entity:", style={"width": 200}, id="corrected-entity"),
                        ],
                    ),
                ],
            ),
            dmc.SegmentedControl(
                id="segmented",
                value = [None],
                # data=segment_control(metadata, "ca. 12 001 BP"),
                data = [{"label":None, "value":None}],
                fullWidth=True,
                
                
            ),
            dmc.Paper(
                children = 
                    [
                        dmc.Text(id="segmented-value"),
                    ],
                            
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
                                    dmc.Button("Yes", color="green", variant="outline", id="yes-button"),
                                    dmc.Button("No", color="red", variant="outline", id="no-button"),
                                    dmc.Text(id="relevant-output", mt=10),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Br(),
            dcc.Store(id="metadata", data=[metadata.to_json(orient="split")]),
            dbc.Row(
                [
                    
                    dbc.Col(sidebar, width=12, lg=3, className="g-0"),
                    dbc.Col(content, width=12, lg=9, className="g-0"),
                ],
            ),
        ],
    )
    return layout

@callback(Output("segmented-value", "children"), Input("segmented", "value"))
def select_value(value):
    return value

@callback(
    Output("entity-text", "children"),
    Input("chips_site", "value"),
    Input("chips_region", "value"),
    Input("chips_taxa", "value"),
    Input("chips_geog", "value"),
    Input("chips_alti", "value"),
    Input("chips_age", "value"),
    Input("chips_email", "value"),
    
)
def chips_values(site, region, taxa, geog, alti, age, email):
    for x in [site, region, taxa, geog, alti, age, email]:
        if x != [None]:
            return x
    return "No entity selected"

@callback(
    Output("segmented", "data"),
    Input("metadata", "data"),
    Input("entity-text", "children"),
    Input("accordion", "value"),
)
def segment_control(data, selected_entity, selected_entity_type):
    data = pd.read_json(data[0], orient="split")
    tab_data = {}
    if selected_entity[1] == "No entity selected":
        return [{"label":None, "value":None}]
    elif selected_entity_type == None:
        return [{"label":None, "value":None}]
    else:
        for entity in data[f"entities.{selected_entity_type}"][0]:
            if entity["name"] == selected_entity[1]:
                section_name = entity["sentence"][0]["section_name"]
                text_value = entity["sentence"][0]["text"]

                if section_name in tab_data:
                    tab_data[section_name].append(text_value)
                else:
                    tab_data[section_name] = [text_value]
        return [{"label": label, "value": values} for label, values in tab_data.items()]

@callback(
    Output("histograms-graph", "figure"),
    Input("histograms-mean", "value"),
    Input("histograms-std", "value"),
)
def display_color(mean, std):
    data = np.random.normal(mean, std, size=500)
    fig = px.histogram(data, nbins=30, range_x=[-10, 10])
    return fig

@callback(
    Output("clicked-output", "children"),
    Input("submit-button", "n_clicks"),
    Input("save-button", "n_clicks"),
    Input('metadata', 'data'),
    prevent_initial_call=True,
)
def save_submit(submit, save, data):
    if submit:
        metadata = pd.read_json(data[0], orient="split")
        metadata["status"] = "Completed"
        metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        print(metadata["last_updated"])
        gddid = metadata["gddid"][0]
        metadata = df_denormalize(metadata)
        metadata= metadata.to_dict(orient='records')
        metadata = json.dumps(metadata)
        with open(f"data/labelled/{gddid}.json", "w") as f:
            f.write(metadata)
        with open(f"data/labelled/completed/{gddid}.json", "w") as f:
            f.write(metadata)
        return "Submitted"
    
    elif save:
        metadata = pd.read_json(data[0], orient="split")
        metadata["status"] = "In Progress"
        gddid = metadata["gddid"][0]
        metadata = df_denormalize(metadata)
        metadata= metadata.to_dict(orient='records')
        metadata = json.dumps(metadata)
        with open(f"data/labelled/{gddid}.json", "w") as f:
            f.write(metadata)
        with open(f"data/labelled/completed/{gddid}.json", "w") as f:
            f.write(metadata)
        return "Saved"
    else:
        return None

@callback(
    Output("relevant-output", "children"),
    Input("yes-button", "n_clicks"),
    Input("no-button", "n_clicks"),
)

def relevant(yes, no):
    if yes:
        return "Relevant"
    elif no:
        return "Non-Relevant, hit Submit to remove from the queue"
    else:
        return None
    
    