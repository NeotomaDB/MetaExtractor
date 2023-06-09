import os
import json
import pandas as pd
import copy
import numpy as np
from collections import defaultdict
from datetime import datetime
import plotly.express as px

import dash
from dash import Dash, dcc, html, Input, Output, callback, State
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from pages.navbar import df_denormalize
from dash_iconify import DashIconify
from pages.config import *

dash.register_page(__name__,  path_template="/article/<gddid>")

original = None
results = None


def layout(gddid=None):
    try:
        global original
        global results
        # get the metadata of the article
        article = open(os.path.join("data",
                                    "data-review-tool",
                                    "raw",
                                    f"{gddid}.json"), "r")

        original = pd.json_normalize(json.loads(article.read()))
        results = copy.deepcopy(original)

    except FileNotFoundError:
        return html.Div([
            html.H1("Error - gddid Not Found"),
            html.P("The requested gddid does not exist in the files."),
            html.P("Please check the article's gddid and try again."),
            dcc.Link("Go back to Home", href="/"),
        ])

    sidebar = html.Div(
        [
            dmc.Accordion(
                id="accordion",
                disableChevronRotation=True,
                children=get_accordion_items(True, original),
            ),
            html.Br(),
            dmc.Switch(
                id="toggle-switch",
                size="lg",
                radius="md",
                onLabel=" Extracted entities",
                offLabel="Deleted entities",
                checked=True,
                color="teal",
                style={"position": "relative", "left": "35%"},
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
                    dmc.Button("Submit",
                               id="submit-button",
                               color="teal"),
                    dmc.Button("Save Progress",
                               id="save-button",
                               color="lime",
                               variant="outline")
                ],
                style={"justify": "center"},
            ),
            dmc.Text(id="clicked-output", mt=10),
        ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col([
                        dmc.Group(
                            [
                                "Enitity Text: ",
                                html.Label(id="entity-text",
                                           style={"font-weight": "bold"}),
                                dmc.TextInput(
                                    id="corrected-text",
                                    placeholder="Add corrected text here",
                                    style={"width": 200},),
                                dmc.Button("Correct",
                                           id="correct-button"),
                            ],
                            style={"anchor": "middle", "justify": "center"}
                        )
                    ], lg=6),
                    dbc.Col([], lg=4),
                    dbc.Col([
                        dmc.Group([
                            dmc.Button(id="delete-restore-button",),
                        ], id="button-group")
                    ], lg=2)
                ],
            ),
            dmc.Tabs(
                id="section-tabs",
                color="red",
                orientation="horizontal",
            )
        ], style=CONTENT_STYLE)

    layout = html.Div(
        [
            dbc.Row(
                html.H2(original["title"][0],
                        style=h2_style)),
            dbc.Row(
                html.H4(original["journal_name"][0],
                        style=h4_style)),
            dbc.Row(
                [
                    dmc.Group([
                        dbc.Col(
                            [
                                dmc.Button(
                                    "Home",
                                    id="home-button",
                                    color="blue",
                                    leftIcon=DashIconify(
                                        icon="dashicons-arrow-left-alt", height=16),
                                ),
                                dcc.Location(id='location_home', refresh=True)
                            ],
                            align="left",
                            lg=1,
                            md=1,
                            sm=1,
                            style={"margin-left": "10px"},
                        ),
                        dbc.Col(
                            [
                                dmc.Group(
                                    [
                                        html.Label(
                                            "If this article is not relevant to NeotomaDB, click here:",),
                                        dmc.Button("Remove", color="green",
                                                   variant="outline", id="yes-button"),
                                        dmc.Text(id="relevant-output", mt=10),
                                    ],
                                    position="center",
                                ),
                            ],
                            align="center",
                            lg=9,
                            md=9,
                            sm=9
                        ),
                        dbc.Col(
                            [
                                # External link to the article
                                dmc.NavLink(
                                    label="Go to Article",
                                    rightSection=DashIconify(
                                        icon="dashicons-admin-links", height=16),
                                    variant="filled",
                                    active=True,
                                    href="http://doi.org/" + \
                                    original["doi"][0],
                                    target="_blank"
                                )
                            ],
                            align="right",
                            lg=1,
                            md=1,
                            sm=1,
                            style={"margin-right": "10px"},
                        ),
                    ])
                ],
            ),
            html.Br(),
            dcc.Store(id="results", data=[
                      original.reset_index().to_json(orient="split")]),
            dbc.Row(
                [

                    dbc.Col(sidebar, width=12, lg=3, className="g-0"),
                    dbc.Col(content, width=12, lg=9, className="g-0"),
                ],
            ),
        ],
    )

    return layout

# Collapse the accordian when toggling between deleted and extracted entities
@callback(
    Output("accordion", "value"),
    Input("toggle-switch", "checked"),
)
def collapse(checked):
    return None

# Populate accordian
@callback(
    Output("accordion", "children"),
    Input("toggle-switch", "checked"),
    Input("results", "data"),
)
def get_accordion_items(checked, data):

    if not isinstance(data, pd.DataFrame):
        data = pd.read_json(data[0], orient="split")

    children = []

    for label, name in entity_name_mapping.items():
        children.append(
            dmc.AccordionItem([
                dmc.AccordionControl(
                    dmc.Group([
                        dmc.Text(name),
                        dmc.Badge(
                            f"{len([ent for ent in data[f'entities.{label}'][0] if ent['deleted'] != checked])}",
                            size="xs",
                            p=0,
                            variant="filled",
                            sx={"width": 16, "height": 16,
                                "pointerEvents": "none"}
                        )])),
                dmc.AccordionPanel([
                    html.Div(
                        [
                            dmc.ChipGroup(
                                id=entity_id_mapping[label],
                                value=None,
                                multiple=False
                            )
                        ],
                        style=chip_style
                    ),

                ]),
            ],
                value=label,
            ))

    return children

# Button group callback
@callback(
    Output("button-group", "children"),
    Input("toggle-switch", "checked"),
)
def update_button(checked):
    if checked:
        return [
            dmc.Button(
                "Delete Entity",
                id="delete-restore-button",
                color="red",
                leftIcon=DashIconify(icon="dashicons-trash", height=16),
                disabled=True,
            ),
        ]
    else:
        return [
            dmc.Button(
                "Restore Entity",
                id="delete-restore-button",
                color="teal",
                leftIcon=DashIconify(icon="dashicons-undo", height=16),
                disabled=True,
            ),
        ]

# Add home button callback
@callback(
    Output("location_home", "href"),
    Input("home-button", "n_clicks"),
    prevent_initial_call=True,
)
def cell_clicked(n_clicks):
    if n_clicks:
        return f"http://127.0.0.1:8050/"
    else:
        return dash.no_update

# update chip values on screen load
@callback(
    Output("chips_site", "children"),
    Output("chips_region", "children"),
    Output("chips_taxa", "children"),
    Output("chips_geog", "children"),
    Output("chips_alti", "children"),
    Output("chips_age", "children"),
    Output("chips_email", "children"),
    Input("toggle-switch", "checked"),
    Input('results', 'data'),
)
def update_chips(checked, data):

    chips = {"SITE": [], "REGION": [], "TAXA": [],
             "GEOG": [], "ALTI": [], "AGE": [], "EMAIL": []}

    if checked:
        deleted = False
    else:
        deleted = True

    # Get all the sentences and corresponding section names
    for entity in chips.keys():
        for ent in results[f"entities.{entity}"][0]:
            if ent["deleted"] == deleted:
                chips[f"{entity}"].append(
                    dmc.Chip(
                        dmc.Group([
                            ent['name'],
                            dmc.Badge(
                                f"{len(ent['sentence'])}",
                                size="xs",
                                p=0,
                                variant="filled",
                                sx={"width": 16, "height": 16,
                                    "pointerEvents": "none"}
                            )
                        ]),
                        value=ent['name'],
                        variant="outline",
                        styles={"label": {"display": "inline-flex",
                                          "justifyContent": "space-between"}},
                    ))

    return chips["SITE"], chips["REGION"], chips["TAXA"], chips["GEOG"], chips["ALTI"], chips["AGE"], chips["EMAIL"]

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
    prevent_initial_call=True,
)
def unselect_chips(accordian):
    return None, None, None, None, None, None, None

# Populate entity text with the selected chip
@callback(
    Output("entity-text", "children"),
    Output("corrected-text", "disabled"),
    # Output("correct-button", "disabled"),
    Output("delete-restore-button", "disabled"),
    Input("chips_site", "value"),
    Input("chips_region", "value"),
    Input("chips_taxa", "value"),
    Input("chips_geog", "value"),
    Input("chips_alti", "value"),
    Input("chips_age", "value"),
    Input("chips_email", "value"),
    State("accordion", "value"),
)
def chips_values(site, region, taxa, geog, alti, age, email, accordian):
    if accordian == "SITE":
        if site == None:
            return "No entity selected", True, True  # , True
        else:
            return site,  False, False  # , False
    elif accordian == "REGION":
        if region == None:
            return "No entity selected", True, True  # , True
        else:
            return region, False, False  # , False
    elif accordian == "TAXA":
        if taxa == None:
            return "No entity selected", True, True  # , True
        else:
            return taxa, False, False  # , False
    elif accordian == "GEOG":
        if geog == None:
            return "No entity selected", True, True  # , True
        else:
            return geog, False, False  # , False
    elif accordian == "ALTI":
        if alti == None:
            return "No entity selected", True, True  # , True
        else:
            return alti, False, False  # , False
    elif accordian == "AGE":
        if age == None:
            return "No entity selected", True, True  # , True
        else:
            return age, False, False  # , False
    elif accordian == "EMAIL":
        if email == None:
            return "No entity selected", True, True  # , True
        else:
            return email, False, False  # , False
    else:
        return "No entity selected", True, True  # , True

# Update the results store when entity text is changed or it needs to be deleted
@callback(
    Output('results', 'data'),
    Input("correct-button", "n_clicks"),
    Input("delete-restore-button", "n_clicks"),
    State("corrected-text", "value"),
    State("chips_site", "value"),
    State("chips_region", "value"),
    State("chips_taxa", "value"),
    State("chips_geog", "value"),
    State("chips_alti", "value"),
    State("chips_age", "value"),
    State("chips_email", "value"),
    State("accordion", "value"),
    prevent_initial_call=True,
)
def update_entity(correct, delete, entity, site, region, taxa, geog, alti, age, email, accordian):
    original_text, _, _ = chips_values(
        site, region, taxa, geog, alti, age, email, accordian)

    if correct:
        if accordian != None:
            for ent in results[f"entities.{accordian}"][0]:
                if ent["name"] == original_text:
                    ent["name"] = entity
                    break

    if delete:
        for ent in results[f"entities.{accordian}"][0]:
            if ent["name"] == original_text:
                ent["deleted"] = not ent["deleted"]
                break

    return [results.reset_index().to_json(orient="split")]

# Save the results to the appropriate folder
@callback(
    Output("clicked-output", "children"),
    Input("submit-button", "n_clicks"),
    Input("save-button", "n_clicks"),
    Input("relevant-output", "children"),
    State('results', 'data'),
    prevent_initial_call=True,
)
def save_submit(submit, save, relevant, data):
    if not os.path.exists("data/data-review-tool/completed/"):
        os.makedirs("data/data-review-tool/completed/")
    if not os.path.exists("data/data-review-tool/nonrelevant/"):
        os.makedirs("data/data-review-tool/nonrelevant/")
    if submit:
        if relevant == None:
            metadata = pd.read_json(data[0], orient="split")
            metadata["status"] = "Completed"
            metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            gddid = metadata["gddid"][0]
            metadata = df_denormalize(metadata)
            metadata = metadata.to_dict(orient='records')[0]
            metadata = json.dumps(metadata)
            with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
                f.write(metadata)
            return "Submitted"
        elif relevant:
            metadata = pd.read_json(data[0], orient="split")
            metadata["status"] = "Non-relevant"
            metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            gddid = metadata["gddid"][0]
            metadata = df_denormalize(metadata)
            metadata = metadata.to_dict(orient='records')[0]
            metadata = json.dumps(metadata)
            with open(f"data/data-review-tool/nonrelevant/{gddid}.json", "w") as f:
                f.write(metadata)
            return "Submitted"
        else:
            return None
    elif save:
        metadata = pd.read_json(data[0], orient="split")
        metadata["status"] = "In Progress"
        gddid = metadata["gddid"][0]
        metadata = df_denormalize(metadata)
        metadata = metadata.to_dict(orient='records')[0]
        metadata = json.dumps(metadata)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
            f.write(metadata)
        return "Saved"
    else:
        return None

# Remove article from queue if it is not relevant
@callback(
    Output("relevant-output", "children"),
    Input("yes-button", "n_clicks"),
    prevent_initial_call=True,
)
def relevant(yes):
    if yes:
        if (yes % 2) == 0:
            return None
        else:
            return "Article Removed, please click Submit to remove from the queue"
    else:
        return None

# Populate tabs with sentences under corresponding sections
@callback(
    Output("section-tabs", "children"),
    Input("delete-restore-button", "n_clicks"),
    Input("chips_site", "value"),
    Input("chips_region", "value"),
    Input("chips_taxa", "value"),
    Input("chips_geog", "value"),
    Input("chips_alti", "value"),
    Input("chips_age", "value"),
    Input("chips_email", "value"),
    State("accordion", "value"),
    prevent_initial_call=True,
)
def tabs_control(n_clicks, site, region, taxa, geog, alti, age, email, accordian):
    callback_context = [p["prop_id"]
                        for p in dash.callback_context.triggered][0]

    if callback_context == "delete-restore-button.n_clicks" and n_clicks:
        return []

    if accordian == None or (site == None and region == None and taxa == None and geog == None and alti == None and age == None and email == None):
        return []

    # Key is the tab name, value is a list of texts
    tabs = defaultdict(list)

    # Get all the sentences and corresponding section names
    for entity in results[f"entities.{accordian}"][0]:
        if entity["name"] in [site, region, taxa, geog, alti, age, email]:
            sentences = entity["sentence"]
            highlight = entity["name"]
            for sentence in sentences:
                section_name = sentence["section_name"]
                text = sentence["text"]
                tabs[section_name].append(text)

    # Convert all the sentences in tabs to paper dmc components
    dmc_tabs_content = []
    for tab_name, tab_content in tabs.items():
        dmc_tabs_content.append(
            dmc.TabsPanel(
                html.Div([
                    dmc.Paper(
                        children=[
                            dmc.Text(dmc.Highlight(text, highlight=highlight))
                        ],
                        withBorder=True,
                        shadow="xs",
                        style={"padding": "1rem", "margin": "1rem"},
                    ) for text in tab_content],
                    style=tab_body_style,
                ),
                value=tab_name
            ),
        )

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

# Enable correct button when corrected text is entered
@callback(
    Output("correct-button", "disabled"),
    Input("corrected-text", "value"),
)
def enable_correct_button(corrected_text):
    if corrected_text:
        return False
    else:
        return True
