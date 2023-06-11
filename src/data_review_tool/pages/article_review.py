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
from pages.navbar import df_denormalize, find_start_end_char
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
        if os.path.exists(os.path.join("data",
                                       "data-review-tool",
                                       "completed",
                                       f"{gddid}.json")):
            article = open(os.path.join("data",
                                        "data-review-tool",
                                        "completed",
                                        f"{gddid}.json"), "r")
        else:
            article = open(os.path.join("data",
                                        "data-review-tool",
                                        "raw",
                                        f"{gddid}.json"), "r")

        original = json.loads(article.read())
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
                color="green",
                style={"position": "relative", "left": "35%"},
            ),
            html.Br(),
            dmc.Textarea(
                label="Reviewer's Comments",
                placeholder="Add Comments",
                autosize=True,
                style={"padding-left": "15px"}
            ),
            html.Br(),
            dmc.Modal(
                id="modal-submit",
                title="Are you sure you want to submit?",
                children=[
                    dmc.Group(
                        [
                            dmc.Button(
                                "Yes", 
                                color="green",
                                variant="light",
                                id="confirm-submit-button"),
                            dmc.Button(
                                "Cancel",
                                color="red",
                                variant="light",
                                id="confirm-submit-close-button"),
                        ],
                        position="center",
                        style={"margin-top": "10px",},
                    )],
            ),
            dmc.Group(
                [
                    dmc.Button("Submit",
                               id="submit-button",
                               color="green"),
                    dmc.Button("Save Progress",
                               id="save-button",
                               color="lime",
                               variant="outline")
                ],
                style={"justify": "center",
                       "padding-left": "15px"},
            ),
            html.Div(id="clicked-output"),
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
                    ], lg=8),
                    dbc.Col([], lg=2),
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

    layout = dmc.NotificationsProvider(
        html.Div(
        [
            dbc.Row(
                html.H2(original["title"],
                        style=h2_style)),
            dbc.Row(
                html.H4(original["journal_name"],
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
                                dcc.Location(id='location_home', refresh=True),
                                dcc.Location(id='location-irrelevant', refresh=True),
                                dcc.Location(id='location-submit', refresh=True),
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
                                        html.Label("Relevance Score: {}".format(round(original["relevance_score"], 2))),
                                        dmc.Modal(
                                            id="modal-irrelevant",
                                            title="Are you sure you want to mark this item as irrelevant?",
                                            children=[
                                                dmc.Group(
                                                    [
                                                        dmc.Button(
                                                            "Yes", 
                                                            color="green",
                                                            variant="light",
                                                            id="confirm-irrelevant-button"),
                                                        dmc.Button(
                                                            "Cancel",
                                                            color="red",
                                                            variant="light",
                                                            id="confirm-irrelevant-close-button"),
                                                    ],
                                                    position="center",
                                                    style={"margin-top": "10px"},
                                            )],
                                        ),
                                        dmc.Button("Mark as irrelevant",
                                                   color="red",
                                                   variant="filled", id="irrelevant-button"),
                                        html.Div(id="relevant-output"),
                                    ],
                                    position="center",
                                ),
                            ],
                            align="center",
                            lg=9,
                            md=8,
                            sm=7
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
                                    original["doi"],
                                    target="_blank",
                                    style={"font-weight": "bold",
                                           "border-radius": "3px"},
                                )
                            ],
                            align="right",
                            lg=1,
                            md=2,
                            sm=3,
                            style={"margin-right": "10px"},
                        ),
                    ])
                ],
            ),
            html.Br(),
            dcc.Store(id="results", data=[
                      original]),
            dbc.Row(
                [

                    dbc.Col(sidebar, width=12, lg=3, className="g-0"),
                    dbc.Col(content, width=12, lg=9, className="g-0"),
                ],
            ),
        ],
    ))

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
    prevent_initial_call=True,
)
def get_accordion_items(checked, data):

    children = []

    for label, name in entity_name_mapping.items():
        children.append(
            dmc.AccordionItem([
                dmc.AccordionControl(
                    dmc.Group([
                        dmc.Text(name),
                        dmc.Badge(
                            f"{len([ent for ent in data['entities'][label].values() if ent['deleted'] != checked])}",
                            size="xxs",
                            p=0,
                            style={"background-color": "#F4C430",
                                   "font-size": "10px",
                                   "font-weight": "exta-bold",},
                            variant="filled",
                            sx={"width": 16, "height": 16,
                                "pointerEvents": "none"}
                        )
                        ])),
                dmc.AccordionPanel([
                    html.Div(
                        [
                            dmc.ChipGroup(
                                id=entity_id_mapping[label],
                                value=None,
                                multiple=False
                            ),
                        ],
                        style=chip_style
                    ),
                    html.Div([
                        dmc.Button(
                            "Add New Entity",
                            id="new-entity-button",
                            color="green",
                            variant="outline",
                            leftIcon=DashIconify(icon="dashicons-plus", height=16),
                            style={"margin-top": "10px"},
                        ),
                        dmc.Modal(
                            id="new-entity-modal",
                            zIndex=10000,
                            centered=True,
                            children=[
                                html.Div([
                                    dmc.Textarea(
                                        label="Entity Name:",
                                        placeholder="Enter the name of the new entity here", 
                                        value="",
                                        id="new-entity-text"),
                                    html.Br(),
                                    dmc.Textarea(
                                        label="Sentence:",
                                        placeholder="Enter sentence containing new entity here", 
                                        value="",
                                        id="new-entity-sentence"),
                                    html.Br(),
                                    dmc.Textarea(
                                        label="Section Name:",
                                        placeholder="Enter sentence containing new entity here", 
                                        value="",
                                        id="new-entity-section"),
                                    html.Br(),
                                ]),
                                dmc.Group(
                                    [
                                        dmc.Button(
                                            "Add", 
                                            color="green",
                                            variant="light",
                                            id="new-entity-submit"),
                                        dmc.Button(
                                            "Close",
                                            color="red",
                                            variant="light",
                                            id="new-entity-close",
                                        ),
                                    ],
                                    position="right",
                                    style={"margin-top": "10px"},
                                ),
                            ],
                        ),

                    ])
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
                color="green",
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
    Input('results', 'data')
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
        for ent, values in results["entities"][entity].items():
            if values["deleted"] == deleted:
                chips[f"{entity}"].append(
                    dmc.Chip(
                        dmc.Group([
                            ent,
                            dmc.Badge(
                                f"{len(values['sentence'])}",
                                size="xs",
                                p=0,
                                variant="filled",
                                style={"background-color": "#F4C430",
                                   "font-size": "10px",
                                   "font-weight": "exta-bold",},
                                sx={"width": 16, "height": 16,
                                    "pointerEvents": "none"}
                            )
                        ]),
                        value=ent,
                        variant="outline",
                        styles={"label": {"display": "inline-flex",
                                          "justifyContent": "space-between",}},
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
    Output("delete-restore-button", "disabled"),
    Output("corrected-text", "value"),
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
            return "No entity selected", True, True, ""
        else:
            return site, False, False, site
    elif accordian == "REGION":
        if region == None:
            return "No entity selected", True, True, ""
        else:
            return region, False, False, region
            
    elif accordian == "TAXA":
        if taxa == None:
            return "No entity selected", True, True, ""
        else:
            return taxa, False, False, taxa
    elif accordian == "GEOG":
        if geog == None:
            return "No entity selected", True, True, ""
        else:
            return geog, False, False, geog
    elif accordian == "ALTI":
        if alti == None:
            return "No entity selected", True, True, ""
        else:
            return alti, False, False, alti
    elif accordian == "AGE":
        if age == None:
            return "No entity selected", True, True, ""
        else:
            return age, False, False, age
    elif accordian == "EMAIL":
        if email == None:
            return "No entity selected", True, True, ""
        else:
            return email, False, False, email
    else:
        return "No entity selected", True, True, ""

# toggle through the modal whenever the add-new-entity / close button is clicked
@callback(
    Output("new-entity-modal", "opened"),
    Output("new-entity-modal", "title"),
    Input("new-entity-button", "n_clicks"),
    Input("new-entity-close", "n_clicks"),
    State("new-entity-modal", "opened"),
    State("accordion", "value"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks, close, opened, accordian):
    return not opened, f"Please add information for a new {accordian} entity below:"

# Update the results store when entity text is changed or it needs to be deleted
@callback(
    Output('results', 'data'),
    Input("correct-button", "n_clicks"),
    Input("delete-restore-button", "n_clicks"),
    Input("new-entity-submit", "n_clicks"),
    State("corrected-text", "value"),
    State("chips_site", "value"),
    State("chips_region", "value"),
    State("chips_taxa", "value"),
    State("chips_geog", "value"),
    State("chips_alti", "value"),
    State("chips_age", "value"),
    State("chips_email", "value"),
    State("accordion", "value"),
    State("new-entity-text", "value"),
    State("new-entity-sentence", "value"),
    State("new-entity-section", "value"),
    prevent_initial_call=True,
)
def update_entity(
    correct, delete, submit, entity, site, region, 
    taxa, geog, alti, age, email, accordian, 
    new_entity_text, new_entity_sentence, new_entity_section):
    
    original_text, _, _, _ = chips_values(site, region, taxa, geog, alti, age, email, accordian)
    
    if submit:
        if new_entity_text != None:
            try:
                start, end = find_start_end_char(new_entity_sentence, new_entity_text)
            except:
                start, end = 0, 0
            
            if not new_entity_section:
                new_entity_section = "Manual Entry"
                
            results["entities"][accordian][new_entity_text] = {
                "sentence": [{
                    "text": new_entity_sentence,
                    "section_name": new_entity_section,
                    "char_index": {
                        "start": start,
                        "end": end
                    },
                }],
                "name": new_entity_text,
                "corrected_name": None,
                "deleted": False,
            }
    elif correct:
        if accordian != None:
            for ent, values in results["entities"][accordian].items():
                if ent == original_text:
                    values["corrected_name"] = entity
                    break

    elif delete:
        for ent, values in results["entities"][accordian].items():
            if ent == original_text:
                values["deleted"] = not values["deleted"]
                break

    return results

# Save the results to the appropriate folder
@callback(
    Output("clicked-output", "children"),
    Output("location-submit", "href"),
    Output("location-irrelevant", "href"),
    Input("confirm-submit-button", "n_clicks"),
    Input("save-button", "n_clicks"),
    Input("relevant-output", "children"),
    State('results', 'data'),
    prevent_initial_call=True,
)
def save_submit(submit, save, relevant, data):
    if submit:
        data["status"] = "Completed"
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        gddid = data["gddid"]
        data = json.dumps(data)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
            f.write(data)
        return  dmc.Notification(
                    title="Review Complete!",
                    id="submit-notification",
                    action="show",
                    color="green",
                    message="Proceed to home page",
                    icon=DashIconify(icon="ic:round-celebration"),
                ), "/", None
    elif relevant:
        data["status"] = "Non-relevant"
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        gddid = data["gddid"]
        data = json.dumps(data)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
            f.write(data)
        return  None, None, "/"
    elif save:
        data["status"] = "In Progress"
        gddid = data["gddid"]
        data = json.dumps(data)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
            f.write(data)
        return  dmc.Notification(
                    title="Progress Saved!",
                    id="save-notification",
                    action="show",
                    color="yellow",
                    message="Don't forget to comeback and finish the review",
                    icon=DashIconify(icon="dashicons-saved"), 
                ), None, None
    else:
        return None, None, None

# Remove article from queue if it is not relevant
@callback(
    Output("relevant-output", "children"),
    Input("confirm-irrelevant-button", "n_clicks"),
    prevent_initial_call=True,
)
def relevant(n_clicks):
    return dmc.Notification(
            title="Article Removed!",
            id="remove-notification",
            action="show",
            color="red",
            message="Proceed to home page",
            icon=DashIconify(icon="dashicons-remove"),
        )

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
    for entity, values in results["entities"][accordian].items():
        if entity in [site, region, taxa, geog, alti, age, email]:
            sentences = values["sentence"]
            highlight = entity
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
                            style={"background-color": "#F4C430",
                                   "font-size": "10px",
                                   "font-weight": "exta-bold",},
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

@callback(
    Output("location-article", "href"),
    Input("article-button", "n_clicks"),
)
def open_article(n_clicks):
    if n_clicks:
        return "http://doi.org/" + original["doi"][0]
    else:
        return None
    
def toggle_modal(n_clicks, opened):
    return not opened


for overflow in ["submit", "irrelevant"]:
    callback(
        Output(f"modal-{overflow}", "opened"),
        Input(f"{overflow}-button", "n_clicks"),
        State(f"modal-{overflow}", "opened"),
        prevent_initial_call=True,
    )(toggle_modal)