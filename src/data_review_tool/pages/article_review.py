from pages.navbar import segment_control
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback, State
import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
<<<<<<< HEAD
import os
=======
from collections import defaultdict
>>>>>>> data-review-tool-jenit
import json
from datetime import datetime

dash.register_page(__name__,  path_template="/article/<gddid>")

<<<<<<< HEAD
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd
from pages.navbar import df_denormalize


def layout(gddid = None):
    try:
        # get the metadata of the article
        file = open(f"data/data-review-tool/raw/{gddid}.json", "r")
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
            
        

=======

np.random.seed(2023)

results = None


def layout(gddid=None):
    global results
    results = pd.read_json(f"data/data-review-tool/raw/{gddid}.json")
    # metadata = pd.DataFrame(metadata.loc[0, "data"], index=metadata.index).reset_index(drop=True)
    # file = open(f"data/data-review-tool/raw/{gddid}.json", "r")
    # results = pd.json_normalize(json.loads(file.read()))
>>>>>>> data-review-tool-jenit
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
                id="accordion",
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl("Site Name"),
                            dmc.AccordionPanel(
                                [
                                    dmc.ChipGroup(
                                        [
                                            dmc.Chip(
                                                site['name'],
                                                value=site['name'],
                                                variant="outline",
                                            )
                                            for site in results["entities"]["SITE"]
                                        ],
                                        id="chips_site",
                                        value=None,
                                        multiple=False,
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
                                                region['name'],
                                                value=region['name'],
                                                variant="outline",
                                            )
                                            for region in results["entities"]["REGION"]
                                        ],
                                        id="chips_region",
                                        value=None,
                                        multiple=False,
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
                                                taxa['name'],
                                                value=taxa['name'],
                                                variant="outline",
                                            )
                                            for taxa in results["entities"]["TAXA"]
                                        ],
                                        id="chips_taxa",
                                        value=None,
                                        multiple=False,
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
                                                geog['name'],
                                                value=geog['name'],
                                                variant="outline",
                                            )
                                            for geog in results["entities"]["GEOG"]
                                        ],
                                        id="chips_geog",
                                        value=None,
                                        multiple=False,
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
                                                alti['name'],
                                                value=alti['name'],
                                                variant="outline",
                                            )
                                            for alti in results["entities"]["ALTI"]
                                        ],
                                        id="chips_alti",
                                        value=None,
                                        multiple=False,
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
                                                age['name'],
                                                value=age['name'],
                                                variant="outline",
                                            )
                                            for age in results["entities"]["AGE"]
                                        ],
                                        id="chips_age",
                                        value=None,
                                        multiple=False,
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
                                                email['name'],
                                                value=email['name'],
                                                variant="outline",
                                            )
                                            for email in results["entities"]["EMAIL"]
                                        ],
                                        id="chips_email",
                                        value=None,
                                        multiple=False,
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
                placeholder="Add Comments",
                autosize=True,
            ),
            html.Br(),
            dmc.Group(
                [
<<<<<<< HEAD
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
=======
                    dmc.Button("Submit", color="green"),
                    dmc.Button("Save Progress", color="green",
                               variant="outline")
                ],
            )
>>>>>>> data-review-tool-jenit
        ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(
        [
            dbc.Row(
                [
                    dmc.Group(
                        [
<<<<<<< HEAD
                            html.P("Entity text:"),
                            dmc.Text(id="entity-text", style={"width": 200}),
                            dmc.TextInput(label="Corrected Entity:", style={"width": 200}, id="corrected-entity"),
=======
                            dmc.TextInput(
                                id="entity-text",
                                label="Entity text:",
                                style={"width": 200},)
>>>>>>> data-review-tool-jenit
                        ],
                    ),
                ],
            ),
            dmc.Tabs(
                id="section-tabs",
                color="red",
                orientation="horizontal",
            )

            # dmc.Paper(
            #     children=[
            #         dmc.Text(id="segmented-value"),
            #     ],
            # )
        ], style=CONTENT_STYLE)

    layout = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P("Article: " + results["title"][0]),
                            html.A(
                                "DOI: doi.org/" + results["doi"][0], href="http://doi.org/" + results["doi"][0], target="_blank"),
                            html.P("Journal: " + results["journal_name"][0]),
                        ],
                    ),
                    dbc.Col(
                        [
                            html.P("Is this article relevant to NeotomaDB?"),
                            dmc.Group(
                                [
<<<<<<< HEAD
                                    dmc.Button("Yes", color="green", variant="outline", id="yes-button"),
                                    dmc.Button("No", color="red", variant="outline", id="no-button"),
                                    dmc.Text(id="relevant-output", mt=10),
=======
                                    dmc.Button("Yes", color="green",
                                               variant="outline"),
                                    dmc.Button("No", color="red",
                                               variant="outline"),
>>>>>>> data-review-tool-jenit
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Br(),
<<<<<<< HEAD
            dcc.Store(id="metadata", data=[metadata.to_json(orient="split")]),
=======
            dcc.Store(id="results", data=[
                      results.reset_index().to_json(orient="split")]),
>>>>>>> data-review-tool-jenit
            dbc.Row(
                [

                    dbc.Col(sidebar, width=12, lg=3, className="g-0"),
                    dbc.Col(content, width=12, lg=9, className="g-0"),
                ],
            ),
        ],
    )
    return layout

# Update the chip selection when accordian value changes


@callback(
    Output("chips_site", "value"),
    Output("chips_region", "value"),
    Output("chips_taxa", "value"),
    Output("chips_geog", "value"),
    Output("chips_alti", "value"),
    Output("chips_age", "value"),
    Output("chips_email", "value"),
    Input("accordion", "value"),
)
def unselect_chips(accordian_state):
    return None, None, None, None, None, None, None

# Update entity value


@callback(
    Output("entity-text", "value"),
    Input("chips_site", "value"),
    Input("chips_region", "value"),
    Input("chips_taxa", "value"),
    Input("chips_geog", "value"),
    Input("chips_alti", "value"),
    Input("chips_age", "value"),
    Input("chips_email", "value"),
    State("accordion", "value")
)
def chips_values(site, region, taxa, geog, alti, age, email, accordian):
    if accordian == "SITE":
        return site
    elif accordian == "REGION":
        return region
    elif accordian == "TAXA":
        return taxa
    elif accordian == "GEOG":
        return geog
    elif accordian == "ALTI":
        return alti
    elif accordian == "AGE":
        return age
    elif accordian == "EMAIL":
        return email
    else:
        return "No entity selected"

# TODO: When the entity text changes, update the output json


@callback(
    Output("section-tabs", "children"),
    Input("chips_site", "value"),
    Input("chips_region", "value"),
    Input("chips_taxa", "value"),
    Input("chips_geog", "value"),
    Input("chips_alti", "value"),
    Input("chips_age", "value"),
    Input("chips_email", "value"),
    State("accordion", "value")
)
def tabs_control(site, region, taxa, geog, alti, age, email, accordian_state):

<<<<<<< HEAD
@callback(
    Output("clicked-output", "children"),
    Input("submit-button", "n_clicks"),
    Input("save-button", "n_clicks"),
    Input("relevant-output", "children"),
    Input('metadata', 'data'),
    prevent_initial_call=True,
)
def save_submit(submit, save, relevant, data):
    if not os.path.exists("data/data-review-tool/completed/"):
            os.makedirs("data/data-review-tool/completed/")
    if not os.path.exists("data/data-review-tool/nonrelevant/"):
            os.makedirs("data/data-review-tool/nonrelevant/")
    if submit:
        if relevant == "Relevant":
            metadata = pd.read_json(data[0], orient="split")
            metadata["status"] = "Completed"
            metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            print(metadata["last_updated"])
            gddid = metadata["gddid"][0]
            metadata = df_denormalize(metadata)
            metadata= metadata.to_dict(orient='records')
            metadata = json.dumps(metadata)
            with open(f"data/data-review-tool/raw/{gddid}.json", "w") as f:
                f.write(metadata)
            with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
                f.write(metadata)
            return "Submitted"
        elif relevant == "Non-Relevant, hit Submit to remove from the queue":
            metadata = pd.read_json(data[0], orient="split")
            metadata["status"] = "Non-relevant"
            metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            gddid = metadata["gddid"][0]
            metadata = df_denormalize(metadata)
            metadata= metadata.to_dict(orient='records')
            metadata = json.dumps(metadata)
            with open(f"data/data-review-tool/raw/{gddid}.json", "w") as f:
                f.write(metadata)
            with open(f"data/data-review-tool/nonrelevant/{gddid}.json", "w") as f:
                f.write(metadata)
            return "Submitted"
        else:
            return "Please select relevant or non-relevant"
    elif save:
        metadata = pd.read_json(data[0], orient="split")
        metadata["status"] = "In Progress"
        gddid = metadata["gddid"][0]
        metadata = df_denormalize(metadata)
        metadata= metadata.to_dict(orient='records')
        metadata = json.dumps(metadata)
        with open(f"data/data-review-tool/raw/{gddid}.json", "w") as f:
            f.write(metadata)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
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
    
    
=======
    if accordian_state == None or (site == None and region == None and taxa == None and geog == None and alti == None and age == None and email == None):
        return []
    
    # Key is the tab name, value is a list of texts
    tabs = defaultdict(list)

    # Get all the sentences and corresponding section names
    for entity in results["entities"][accordian_state]:
        if entity["name"] in [site, region, taxa, geog, alti, age, email]:
            sentences = entity["sentence"]
            for sentence in sentences:
                section_name = sentence["section_name"]
                text = sentence["text"]
                tabs[section_name].append(text)

    # Convert all the sentences in tabs to paper dmc components
    dmc_tabs_content = []
    for tab_name, tab_content in tabs.items():
        dmc_tabs_content.append(dmc.TabsPanel(
            dmc.Paper(
                children=[
                    dmc.Text(text)
                    for text in tab_content
                ],
                withBorder=True,
                shadow="xs"
            ),
            value=tab_name
        ))
        
    # Convert to list of tabs
    dmc_tabs = [dmc.Tab(tab_name, 
                        value=tab_name,
                        rightSection=dmc.Badge(
                            f"{len(tabs[tab_name])}",
                            size="xs",
                            p=0,
                            variant="filled",
                            sx={"width": 16, "height": 16, "pointerEvents": "none"})) 
                for tab_name in tabs.keys()]
    
    tab_component = dmc.Tabs(
        children=[
            dmc.TabsList(
                dmc_tabs,
                position="center"
            ),
        ],
        color="red",
        orientation="horizontal",
        value=list(tabs.keys())[0]
    )
    tab_component.children.extend(dmc_tabs_content)
    
    return tab_component
>>>>>>> data-review-tool-jenit
