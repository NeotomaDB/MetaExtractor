# Author: Shaun Hutchinson, Jenit Jain
# Date: 2023-06-22
import os
import sys
import json
import sys
import pandas as pd
import copy
import numpy as np
from collections import defaultdict
from datetime import datetime

import dash
from dash import dcc, html, Input, Output, callback, State
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import seaborn as sns

sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
)

from src.logs import get_logger

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data_review_tool.pages.config import *

dash.register_page(__name__, path_template="/article/<gddid>")

from src.logs import get_logger

logger = get_logger(__name__)

original = None
color_palette = sns.color_palette("RdYlGn", 100).as_hex()

logger = get_logger(__name__)


def layout(gddid=None):
    try:
        logger.info(f"Loading article {gddid}")
        global original
        global results

        original = load_data(f"/entity_extraction/{gddid}.json")
        results = copy.deepcopy(original)

    except FileNotFoundError:
        return html.Div(
            [
                html.H1("Error - gddid Not Found"),
                html.P("The requested gddid does not exist in the files."),
                html.P("Please check the article's gddid and try again."),
                dcc.Link("Go back to Home", href="/"),
            ]
        )

    relevance_score = round(original["predict_proba"], 2) * 100

    logger.info(f"Relevance score for article {gddid} = {relevance_score}")

    sidebar = html.Div(
        [
            dmc.Accordion(
                id="accordion",
                disableChevronRotation=True,
                children=get_accordion_items(True, original),
                style={"background-color": "#f8f9fa"},
            ),
            html.Br(),
            dmc.Switch(
                id="toggle-switch",
                size="xl",
                radius="md",
                onLabel="Show deleted entities",
                offLabel="Hide deleted entities",
                checked=True,
                styles={
                    "labelWrapper": {
                        "font-color": "white",
                    },
                    "track": {"background-color": "green", "color": "white"},
                },
                style={
                    "align-items": "center",
                    "position": "relative",
                    "left": "30%",
                },
                color="red",
            ),
            html.Br(),
            dmc.Textarea(
                label="Reviewer's Comments",
                placeholder="Add Comments",
                autosize=True,
                style={"padding-left": "1rem"},
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
                                id="confirm-submit-button",
                            ),
                            dmc.Button(
                                "Cancel",
                                color="red",
                                variant="light",
                                id="confirm-submit-close-button",
                            ),
                        ],
                        position="center",
                        style={
                            "margin-top": "10px",
                        },
                    )
                ],
            ),
            dmc.Group(
                [
                    dmc.Button("Submit", id="submit-button", color="green"),
                    dmc.Button(
                        "Save Progress",
                        id="save-button",
                        color="lime",
                        variant="outline",
                    ),
                ],
                style={"justify": "center", "padding-left": "1rem"},
            ),
            html.Div(id="clicked-output"),
        ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dmc.Group(
                                [
                                    "Original Text: ",
                                    html.Label(
                                        id="entity-text", style={"font-weight": "bold"}
                                    ),
                                    dmc.TextInput(
                                        id="corrected-text",
                                        placeholder="Add corrected text here",
                                        style={"width": 200},
                                    ),
                                    dmc.Button(
                                        "Correct",
                                        id="correct-button",
                                        color="lime",
                                        variant="outline",
                                    ),
                                ],
                                style={"anchor": "middle", "justify": "center"},
                            )
                        ],
                        lg=8,
                    ),
                    dbc.Col([], lg=2),
                    dbc.Col(
                        [
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Delete Entity",
                                        id="delete-restore-button",
                                        color="red",
                                        leftIcon=DashIconify(
                                            icon="dashicons-trash", height=16
                                        ),
                                        disabled=True,
                                    )
                                ],
                                id="button-group",
                            )
                        ],
                        lg=2,
                    ),
                ],
            ),
            dmc.Tabs(
                id="section-tabs",
                color="red",
                orientation="horizontal",
                style={"padding-top": "1rem"},
            ),
        ],
        style=CONTENT_STYLE,
    )

    layout = dmc.NotificationsProvider(
        html.Div(
            [
                dbc.Row(html.H2(original["title"], style=h2_style)),
                dbc.Row(html.H4(original["journal"], style=h4_style)),
                dbc.Row(
                    [
                        dmc.Group(
                            [
                                dbc.Col(
                                    [
                                        dmc.Button(
                                            dmc.Text("Home", style=nav_text_style),
                                            id="home-button",
                                            leftIcon=DashIconify(
                                                icon="dashicons-arrow-left-alt",
                                                height=16,
                                            ),
                                            style=nav_button_style,
                                        ),
                                        dcc.Location(id="location_home", refresh=True),
                                    ],
                                    align="left",
                                    lg=1,
                                    md=2,
                                    sm=3,
                                    width=12,
                                    style={"margin-left": "10px"},
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                dmc.Text(
                                                    "Relevance Score: ",
                                                    style=relevance_score_style,
                                                ),
                                                dmc.RingProgress(
                                                    id="ring-progress",
                                                    sections=[
                                                        {
                                                            "value": relevance_score,
                                                            "color": color_palette[
                                                                int(relevance_score)
                                                            ],
                                                        }
                                                    ],
                                                    label=dmc.Center(
                                                        dmc.Text(
                                                            f"{int(relevance_score)}%",
                                                            style={
                                                                "font-size": "1rem",
                                                                "font-weight": "bold",
                                                            },
                                                        )
                                                    ),
                                                    size=80,
                                                    thickness=10,
                                                    roundCaps=True,
                                                    style=progress_ring_style,
                                                ),
                                            ]
                                        )
                                    ],
                                    align="center",
                                    lg=2,
                                    md=3,
                                    sm=4,
                                    style={"position": "relative", "left": "2%"},
                                ),
                                dbc.Col(
                                    [
                                        dmc.Group(
                                            [
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
                                                                    id="confirm-irrelevant-button",
                                                                ),
                                                                dmc.Button(
                                                                    "Cancel",
                                                                    color="red",
                                                                    variant="light",
                                                                    id="confirm-irrelevant-close-button",
                                                                ),
                                                            ],
                                                            position="center",
                                                            style={
                                                                "margin-top": "10px"
                                                            },
                                                        )
                                                    ],
                                                ),
                                                dmc.Button(
                                                    "Mark as irrelevant",
                                                    color="red",
                                                    variant="filled",
                                                    id="irrelevant-button",
                                                ),
                                            ],
                                            position="center",
                                        ),
                                    ],
                                    align="center",
                                    lg=7,
                                    md=5,
                                    sm=2,
                                    width=12,
                                    style={"position": "relative", "right": "6%"},
                                ),
                                dbc.Col(
                                    [
                                        # External link to the article
                                        dmc.NavLink(
                                            label=dmc.Text(
                                                "Go to Article", style=nav_text_style
                                            ),
                                            rightSection=DashIconify(
                                                icon="dashicons-admin-links", height=16
                                            ),
                                            variant="filled",
                                            active=True,
                                            href="http://doi.org/" + original["DOI"],
                                            target="_blank",
                                            style=nav_button_style,
                                        )
                                    ],
                                    lg=1,
                                    md=2,
                                    sm=3,
                                    width=12,
                                    style={
                                        "position": "relative",
                                        "width": "auto",
                                        "left": "2.5%",
                                    },
                                ),
                            ]
                        )
                    ],
                ),
                html.Br(),
                dcc.Store(id="results", data=results),
                dbc.Row(
                    [
                        dbc.Col(sidebar, width=12, lg=3, className="g-0"),
                        dbc.Col(content, width=12, lg=9, className="g-0"),
                    ],
                ),
            ],
        ),
        position="top-right",
        autoClose=3000,
    )

    return layout


@callback(
    Output("accordion", "value"),
    Input("toggle-switch", "checked"),
)
def collapse(checked):
    logger.debug(f"checked: {checked}")
    """Return the value of the accordion to collapse it when toggling between deleted and extracted entities

    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False

    Returns:
        bool: Whether the accordion is collapsed (True) or not (False)
    """
    return None


@callback(
    Output("accordion", "children"),
    Input("toggle-switch", "checked"),
    Input("results", "data"),
    prevent_initial_call=True,
)
def get_accordion_items(checked, data):
    logger.debug(f"checked: {checked}")
    """Return the children of the accordion to populate it with the extracted entities
    
    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False)
        data (dict): The data from the article page
    
    Returns:
        list: The children of the accordion
    """
    children = []

    for label, name in entity_name_mapping.items():
        children.append(
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(
                        dmc.Group(
                            [
                                dmc.Text(name),
                                dmc.Badge(
                                    dmc.Text(
                                        f"{len([ent for ent in data['entities'][label].values() if ent['deleted'] != checked])}",
                                        style=review_badge_style,
                                    ),
                                    p=0,
                                    style={"background-color": "#b8864b"},
                                    variant="filled",
                                    sx={
                                        "width": 17,
                                        "height": 17,
                                        "pointerEvents": "none",
                                    },
                                ),
                            ]
                        )
                    ),
                    dmc.AccordionPanel(
                        [
                            html.Div(
                                [
                                    dmc.ChipGroup(
                                        id=entity_id_mapping[label],
                                        value=None,
                                        multiple=False,
                                    ),
                                ],
                                style=chip_style,
                            ),
                            html.Div(
                                [
                                    dmc.Button(
                                        "Add New Entity",
                                        id="new-entity-button",
                                        color="green",
                                        variant="outline",
                                        leftIcon=DashIconify(
                                            icon="dashicons-plus", height=16
                                        ),
                                        style={"margin-top": "10px"},
                                    ),
                                    dmc.Modal(
                                        id="new-entity-modal",
                                        zIndex=10000,
                                        centered=True,
                                        children=[
                                            html.Div(
                                                [
                                                    dmc.Textarea(
                                                        label="Entity Name:",
                                                        placeholder="Enter the name of the new entity here",
                                                        value="",
                                                        id="new-entity-text",
                                                    ),
                                                    html.Br(),
                                                    dmc.Textarea(
                                                        label="Sentence:",
                                                        placeholder="Enter sentence containing new entity here",
                                                        value="",
                                                        id="new-entity-sentence",
                                                    ),
                                                    html.Br(),
                                                    dmc.Textarea(
                                                        label="Section Name:",
                                                        placeholder="Enter sentence containing new entity here",
                                                        value="",
                                                        id="new-entity-section",
                                                    ),
                                                    html.Br(),
                                                ]
                                            ),
                                            dmc.Group(
                                                [
                                                    dmc.Button(
                                                        "Add",
                                                        color="green",
                                                        variant="light",
                                                        id="new-entity-submit",
                                                    ),
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
                                ]
                            ),
                        ]
                    ),
                ],
                value=label,
            )
        )
    return children


@callback(
    Output("button-group", "children"),
    Input("toggle-switch", "checked"),
    prevent_initial_call=True,
)
def update_button(checked):
    """Return the children of the button group to update the button to either delete or restore entities

    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False)

    Returns:
        list: The children of the button group
    """
    logger.info(f"checked: {checked}")
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


@callback(
    Output("location_home", "href"),
    Input("home-button", "n_clicks"),
    prevent_initial_call=True,
)
def cell_clicked(n_clicks):
    """Return the href of the home button to redirect to the home page

    Args:
        n_clicks (int): The number of times the home button has been clicked

    Returns:
        str: The href of the home button
    """
    logger.info(f"n_clicks: {n_clicks}")
    if n_clicks:
        return "/"
    else:
        return dash.no_update


@callback(
    Output("chips_site", "children"),
    Output("chips_region", "children"),
    Output("chips_taxa", "children"),
    Output("chips_geog", "children"),
    Output("chips_alti", "children"),
    Output("chips_age", "children"),
    Output("chips_email", "children"),
    Input("toggle-switch", "checked"),
    State("results", "data"),
)
def update_chips(checked, data):
    """Return the children of the chips to update the chips on screen load

    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False)
        data (dict): The data of the article
    Returns:
        list: The children of the chips
    """
    chips = {
        "SITE": [],
        "REGION": [],
        "TAXA": [],
        "GEOG": [],
        "ALTI": [],
        "AGE": [],
        "EMAIL": [],
    }
    logger.info(f"checked: {checked}")
    if checked:
        deleted = False
    else:
        deleted = True

    # Get all the sentences and corresponding section names
    for entity in chips.keys():
        for ent, values in data["entities"][entity].items():
            if values["deleted"] == deleted:
                # Use the updated name for the chip
                if values["corrected_name"] != None:
                    name = values["corrected_name"]
                else:
                    name = ent

                chips[f"{entity}"].append(
                    dmc.Chip(
                        dmc.Group(
                            [
                                name,
                                dmc.Badge(
                                    dmc.Text(
                                        f"{len(values['sentence'])}",
                                        style=review_badge_style,
                                    ),
                                    p=0,
                                    variant="filled",
                                    style={"background-color": "#b8864b"},
                                    sx={
                                        "width": 17,
                                        "height": 17,
                                        "pointerEvents": "none",
                                    },
                                ),
                            ]
                        ),
                        value=ent,
                        variant="outline",
                        styles=toggle_style,
                    )
                )

    return (
        chips["SITE"],
        chips["REGION"],
        chips["TAXA"],
        chips["GEOG"],
        chips["ALTI"],
        chips["AGE"],
        chips["EMAIL"],
    )


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
    """Return the values of the chips to unselect all chips when the accordian value changes

    Args:
        accordian (str): The value of the accordian

    Returns:
        list: The values of the chips
    """
    return None, None, None, None, None, None, None


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
    Input("results", "data"),
)
def chips_values(site, region, taxa, geog, alti, age, email, accordian, data):
    """Return the children of the entity text to populate the entity text with the selected chip

    Args:
        site (str): The value of the site chip
        region (str): The value of the region chip
        taxa (str): The value of the taxa chip
        geog (str): The value of the geog chip
        alti (str): The value of the alti chip
        age (str): The value of the age chip
        email (str): The value of the email chip
        accordian (str): The value of the accordian
        data (dict): The data of the article

    Returns:
        list: The children of the entity text
    """
    logger.info(f"accordian: {accordian}")
    if accordian == None:
        return "No entity selected", True, True, ""

    for entity, value in data["entities"][accordian].items():
        if entity in [site, region, taxa, geog, alti, age, email]:
            if value["corrected_name"] != None:
                corrected_name = value["corrected_name"]
            else:
                corrected_name = entity

    if accordian == "SITE":
        if site == None:
            return "No entity selected", True, True, ""
        else:
            logger.debug(f"site: {site} corrected: {corrected_name}")
            return site, False, False, corrected_name

    elif accordian == "REGION":
        if region == None:
            return "No entity selected", True, True, ""
        else:
            logger.debug(f"region: {region} corrected: {corrected_name}")
            return region, False, False, corrected_name
    elif accordian == "TAXA":
        if taxa == None:
            return "No entity selected", True, True, ""
        else:
            logger.debug(f"taxa: {taxa} corrected: {corrected_name}")
            return taxa, False, False, corrected_name
    elif accordian == "GEOG":
        if geog == None:
            return "No entity selected", True, True, ""
        else:
            logger.debug(f"geog: {geog} corrected: {corrected_name}")
            return geog, False, False, corrected_name
    elif accordian == "ALTI":
        if alti == None:
            return "No entity selected", True, True, ""
        else:
            logger.debug(f"alti: {alti} corrected: {corrected_name}")
            return alti, False, False, corrected_name
    elif accordian == "AGE":
        if age == None:
            return "No entity selected", True, True, ""
        else:
            logger.debug(f"age: {age} corrected: {corrected_name}")
            return age, False, False, corrected_name
    elif accordian == "EMAIL":
        if email == None:
            return "No entity selected", True, True, ""
        else:
            logger.debug(f"email: {email} corrected: {corrected_name}")
            return email, False, False, corrected_name


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
    """Return the state of the modal and the title of the modal

    Args:
        n_clicks (int): The number of times the add-new-entity button has been clicked
        close (int): The number of times the close button has been clicked
        opened (bool): The state of the modal
        accordian (str): The value of the accordian
    Returns:
        bool: The state of the modal
        str: The title of the modal
    """
    logger.info(
        f"n_clicks: {n_clicks} close: {close} opened: {opened} accordian: {accordian}"
    )
    return not opened, f"Please add information for a new {accordian} entity below:"


@callback(
    Output("results", "data"),
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
    Input("results", "data"),
    prevent_initial_call=True,
)
def update_entity(
    correct,
    delete,
    submit,
    entity,
    site,
    region,
    taxa,
    geog,
    alti,
    age,
    email,
    accordian,
    new_entity_text,
    new_entity_sentence,
    new_entity_section,
    data,
):
    """Update the results store when entity text is changed or it needs to be deleted

    Args:
        correct (int): The number of times the correct button has been clicked
        delete (int): The number of times the delete button has been clicked
        submit (int): The number of times the submit button has been clicked
        entity (str): The corrected entity text
        site (str): The value of the site chip
        region (str): The value of the region chip
        taxa (str): The value of the taxa chip
        geog (str): The value of the geog chip
        alti (str): The value of the alti chip
        age (str): The value of the age chip
        email (str): The value of the email chip
        accordian (str): The value of the accordian
        new_entity_text (str): The value of the new entity text
        new_entity_sentence (str): The value of the new entity sentence
        new_entity_section (str): The value of the new entity section
        data (dict): The data of the article

    Returns:
        dict: The updated results store
    """

    callback_context = [p["prop_id"] for p in dash.callback_context.triggered][0]
    original_text, _, _, _ = chips_values(
        site, region, taxa, geog, alti, age, email, accordian, data
    )

    if callback_context == "new-entity-submit.n_clicks" and submit:
        logger.info(
            f"new_entity_text: {new_entity_text} new_entity_sentence: {new_entity_sentence} new_entity_section: {new_entity_section}"
        )
        if new_entity_text != None:
            try:
                start, end = find_start_end_char(new_entity_sentence, new_entity_text)
            except:
                start, end = 0, 0

            try:
                sentences = pd.DataFrame(data["relevant_sentences"])
                min_sentid = int(sentences["sentid"].min() - 1)
                if min_sentid >= 0:
                    min_sentid = -1
                sentid = min_sentid
            except:
                sentences = pd.DataFrame()
                sentid = -1

            if not new_entity_section:
                new_entity_section = "Manual Entry"

            data["entities"][accordian][new_entity_text] = {
                "sentence": [
                    {
                        "text": new_entity_sentence,
                        "section_name": new_entity_section,
                        "char_index": {"start": start, "end": end},
                        "sentid": sentid,
                    }
                ],
                "name": new_entity_text,
                "corrected_name": None,
                "deleted": False,
            }
            data["relevant_sentences"].append(
                {
                    "sentid": sentid,
                    "text": new_entity_sentence,
                }
            )

    elif callback_context == "correct-button.n_clicks" and correct:
        # return results if entity == original_text so nothing happens
        if entity == original_text:
            logger.info("entity == original_text")
            return data
        if entity in data["entities"][accordian]:
            logger.debug(f"{entity} in data[entities][accordian]")
            for sentence in data["entities"][accordian][original_text]["sentence"]:
                try:
                    start, end = find_start_end_char(sentence["text"], entity)
                except:
                    start, end = 0, 0

                sentence["char_index"]["start"] = start
                sentence["char_index"]["end"] = end

                # Add to sentences if not already present
                if sentence not in data["entities"][accordian][entity]["sentence"]:
                    data["entities"][accordian][entity]["sentence"].append(sentence)
                    logger.info(
                        f"Added {sentence} to data[entities][accordian][entity][sentence]"
                    )
            # Delete the old entity
            data["entities"][accordian][original_text]["deleted"] = True
            logger.info(f"Changed {original_text} to deleted = True")

        else:
            for ent, values in data["entities"][accordian].items():
                if ent == original_text:
                    values["corrected_name"] = entity
                    logger.info(f"Changed {original_text} to {entity}")
                    break

    elif callback_context == "delete-restore-button.n_clicks" and delete:
        for ent, values in data["entities"][accordian].items():
            if ent == original_text:
                values["deleted"] = not values["deleted"]
                logger.info(f"Changed {original_text} to deleted = True")
                break

    return data


@callback(
    Output("clicked-output", "children"),
    Input("confirm-submit-button", "n_clicks"),
    Input("save-button", "n_clicks"),
    Input("confirm-irrelevant-button", "n_clicks"),
    State("results", "data"),
    prevent_initial_call=True,
)
def save_submit(submit, save, relevant, data):
    """Save the results to the appropriate folder

    Args:
        submit (int): The number of times the submit button has been clicked
        save (int): The number of times the save button has been clicked
        relevant (int): The number of times the irrelevant button has been clicked
        data (dict): The results store

    Returns:
        str: The notification to display
    """
    callback_context = [p["prop_id"] for p in dash.callback_context.triggered][0]

    if callback_context == "confirm-submit-button.n_clicks" and submit:
        update_data = {
            "gddid": data["gddid"],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "corrected_entities": json.dumps(data["entities"]),
            "status": "Completed",
        }
        update_output(**update_data)
        logger.info("Entities saved!")
        return dmc.Notification(
            title="Review Complete!",
            id="submit-notification",
            action="show",
            color="green",
            message="Proceed to home page",
            icon=DashIconify(icon="ic:round-celebration"),
        )

    elif callback_context == "confirm-irrelevant-button.n_clicks" and relevant:
        update_data = {
            "gddid": data["gddid"],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "corrected_entities": "None",
            "status": "Non-relevant",
        }
        update_output(**update_data)
        logger.info("Article removed from queue")
        return dmc.Notification(
            title="Article Removed!",
            id="remove-notification",
            action="show",
            color="red",
            message="Proceed to home page",
            icon=DashIconify(icon="dashicons-remove"),
        )

    elif callback_context == "save-button.n_clicks" and save:
        update_data = {
            "gddid": data["gddid"],
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "corrected_entities": json.dumps(data["entities"]),
            "status": "In Progress",
        }
        update_output(**update_data)
        logger.info("Article progress saved!")
        return dmc.Notification(
            title="Progress Saved!",
            id="save-notification",
            action="show",
            color="yellow",
            message="Don't forget to comeback and finish the review",
            icon=DashIconify(icon="dashicons-saved"),
        )

    else:
        return None


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
    Input("results", "data"),
    prevent_initial_call=True,
)
def tabs_control(n_clicks, site, region, taxa, geog, alti, age, email, accordian, data):
    """Populate tabs with sentences under corresponding sections

    Args:
        n_clicks (int): The number of times the delete/restore button has been clicked
        site (str): The site name
        region (str): The region name
        taxa (str): The taxa name
        geog (str): The geography name
        alti (str): The altitude name
        age (str): The age name
        email (str): The email name
        accordian (str): The current accordian
        data (dict): The results store
    Returns:
        list: The list of tabs
    """
    callback_context = [p["prop_id"] for p in dash.callback_context.triggered][0]

    if callback_context == "delete-restore-button.n_clicks":
        return []

    if accordian == None or (
        site == None
        and region == None
        and taxa == None
        and geog == None
        and alti == None
        and age == None
        and email == None
    ):
        return []

    # Key is the tab name, value is a list of texts
    tabs = defaultdict(list)
    logger.debug(f"Accordian: {accordian}")
    relevant_sentences = pd.DataFrame(data["relevant_sentences"])
    logger.debug(relevant_sentences)
    positive_values = relevant_sentences["sentid"][relevant_sentences["sentid"] > 0]
    # Get all the sentences and corresponding section names
    for entity, values in data["entities"][accordian].items():
        if entity in [site, region, taxa, geog, alti, age, email]:
            sentences = values["sentence"]
            if values["corrected_name"] != None:
                highlight = values["corrected_name"]
            else:
                highlight = entity

            for sentence in sentences:
                section_name = sentence["section_name"]
                # New Entity Sentances have Negative sentid
                # So only add that one sentance
                if sentence["sentid"] < 0:
                    text = relevant_sentences.query("sentid == @sentence['sentid']")[
                        "text"
                    ].values[0]
                    tabs[section_name].append(text)

                # If the sentid is the minimum positive value
                # Than add the current and next sentence
                elif sentence["sentid"] == positive_values.min():
                    text = []
                    for i in [sentence["sentid"], sentence["sentid"] + 1]:
                        text.append(
                            relevant_sentences.query("sentid == @i")["text"].values[0]
                        )
                    tabs[section_name].append(" ".join(text))

                # Else we want sentences before and after the current sentence as well
                else:
                    text = []
                    for i in [
                        sentence["sentid"] - 1,
                        sentence["sentid"],
                        sentence["sentid"] + 1,
                    ]:
                        text.append(
                            relevant_sentences.query("sentid == @i")["text"].values[0]
                        )
                    tabs[section_name].append(" ".join(text))
    # Convert all the sentences in tabs to paper dmc components
    dmc_tabs_content = []
    for tab_name, tab_content in tabs.items():
        dmc_tabs_content.append(
            dmc.TabsPanel(
                html.Div(
                    [
                        dmc.Paper(
                            children=[
                                dmc.Text(
                                    dmc.Highlight(
                                        text,
                                        highlight=highlight,
                                        highlightColor="blue",
                                    )
                                )
                            ],
                            withBorder=True,
                            shadow="xs",
                            style={"padding": "1rem", "margin": "1rem"},
                        )
                        for text in tab_content
                    ],
                    style=tab_body_style,
                ),
                value=tab_name,
            ),
        )

    # Convert to list of tabs
    dmc_tabs = [
        dmc.Tab(
            tab_name,
            value=tab_name,
            rightSection=dmc.Badge(
                dmc.Text(f"{len(tabs[tab_name])}", style=review_badge_style),
                p=0,
                variant="filled",
                style={"background-color": "#b8864b"},
                sx={"width": 17, "height": 17, "pointerEvents": "none"},
            ),
        )
        for tab_name in tabs.keys()
    ]

    # Get the first tab component
    try:
        first_tab = list(tabs.keys())[0]
    except IndexError:
        # Error if the corrected spelling doesn't occur in any sentence
        first_tab = None
    tab_component = dmc.Tabs(
        children=[
            dmc.TabsList(dmc_tabs, position="center"),
        ],
        variant="outline",
        orientation="horizontal",
        value=first_tab,
    )
    tab_component.children.extend(dmc_tabs_content)
    return tab_component


@callback(
    Output("correct-button", "disabled"),
    Input("corrected-text", "value"),
)
def enable_correct_button(corrected_text):
    """Enable correct button when corrected text is entered

    Args:
        corrected_text (str): The corrected text
    Returns:
        bool: Whether the correct button is enabled
    """
    if corrected_text:
        return False
    else:
        return True


@callback(
    Output("location-article", "href"),
    Input("article-button", "n_clicks"),
)
def open_article(n_clicks):
    """Open the article in a new tab

    Args:
        n_clicks (int): The number of times the article button has been clicked

    Returns:
        str: The article link
    """

    if n_clicks:
        logger.info(f"Opening article f{original['doi'][0]}")
        return "http://doi.org/" + original["doi"][0]
    else:
        return None


def toggle_confirmation_modal(n_clicks_close, n_clicks, submit, opened):
    """Toggle the confirmation modal

    args:
        n_clicks_close (int): The number of times the close button has been clicked
        n_clicks (int): The number of times the confirm button has been clicked
        submit (int): The number of times the submit button has been clicked
        opened (bool): Whether the modal is opened

    Return:
        bool: Whether the modal is opened
    """
    return not opened


for overflow in ["submit", "irrelevant"]:
    callback(
        Output(f"modal-{overflow}", "opened"),
        Input(f"confirm-{overflow}-close-button", "n_clicks"),
        Input(f"confirm-{overflow}-button", "n_clicks"),
        Input(f"{overflow}-button", "n_clicks"),
        State(f"modal-{overflow}", "opened"),
        prevent_initial_call=True,
    )(toggle_confirmation_modal)


def load_data(file_path):
    """Fetches the extracted entities and metadata for an article

    Parameter
    ---------
    file_path: str
        Path to extracted entities for an article

    Returns
    -------
    dict: entities and metadata for an article

    """
    entities = json.load(open(file_path, "r"))
    logger.info(f"Entities extracted from file: {file_path}")

    metadata, corrected_entities = get_article_metadata(entities["gddid"])
    logger.info(f"Metadata extracted for the article")

    if corrected_entities != "None":
        entities["entities"] = json.loads(corrected_entities)
        logger.info("Fetched verified entities from stored output")

    return {**entities, **metadata[entities["gddid"]]}


def get_article_metadata(gddid):
    """Fetch the article metadata

    Parameter
    ---------
    gddid: str
        xDD ID of the current selected article

    Returns
    -------
    dict: dictionary containing the current article's metadata
    str: dictionary of updated entities in string format
    """
    # Read the Parquet file with pushdown predicate
    article_metadata = pd.read_parquet(
        os.path.join("/MetaExtractor", "inputs", os.environ["ARTICLE_RELEVANCE_BATCH"])
    )
    filtered_metadata = (
        article_metadata[article_metadata["gddid"] == gddid][
            [
                "DOI",
                "gddid",
                "predict_proba",
                "title",
                "subtitle",
                "journal",
                "status",
                "last_updated",
                "corrected_entities",
            ]
        ]
        .set_index("gddid")
        .to_dict(orient="index")
    )

    if gddid in filtered_metadata:
        corrected_entities = filtered_metadata[gddid].get("corrected_entities", "None")
    else:
        corrected_entities = "None"

    return filtered_metadata, corrected_entities


def update_output(**args):
    """
    Updates the article relevance parquet file
    with extracted and verified entities

    Parameter
    ---------
    args: dict
        Various keys to update in the file

        gddid: str
            xDD ID of the article to update
        last_updated: datetime
            Datetime stamp when the user updated the article review
        corrected_entities: str
            Dictionary of corrected and updated entities in string format
        status: str
            Status of the reviewing process
    """

    article_metadata = pd.read_parquet(
        os.path.join("/MetaExtractor", "inputs", os.environ["ARTICLE_RELEVANCE_BATCH"])
    )
    article_metadata.loc[article_metadata["gddid"] == args["gddid"], "status"] = args[
        "status"
    ]
    article_metadata.loc[
        article_metadata["gddid"] == args["gddid"], "last_updated"
    ] = args["last_updated"]
    article_metadata.loc[
        article_metadata["gddid"] == args["gddid"], "corrected_entities"
    ] = args["corrected_entities"]

    article_metadata.to_parquet(
        os.path.join("/MetaExtractor", "inputs", os.environ["ARTICLE_RELEVANCE_BATCH"])
    )
