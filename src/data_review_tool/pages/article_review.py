from pages.navbar import segment_control
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback, State
import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from collections import defaultdict
import json

dash.register_page(__name__,  path_template="/article/<gddid>")


np.random.seed(2023)

results = None


def layout(gddid=None):
    global results
    results = pd.read_json(f"data/data-review-tool/raw/{gddid}.json")
    # metadata = pd.DataFrame(metadata.loc[0, "data"], index=metadata.index).reset_index(drop=True)
    # file = open(f"data/data-review-tool/raw/{gddid}.json", "r")
    # results = pd.json_normalize(json.loads(file.read()))
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
                    dmc.Button("Submit", color="green"),
                    dmc.Button("Save Progress", color="green",
                               variant="outline")
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
                            dmc.TextInput(
                                id="entity-text",
                                label="Entity text:",
                                style={"width": 200},)
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
                                    dmc.Button("Yes", color="green",
                                               variant="outline"),
                                    dmc.Button("No", color="red",
                                               variant="outline"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Br(),
            dcc.Store(id="results", data=[
                      results.reset_index().to_json(orient="split")]),
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
