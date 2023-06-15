import os
import json
import pandas as pd
import copy
import numpy as np
from collections import defaultdict
from datetime import datetime

import dash
from dash import dcc, html, Input, Output, callback, State
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from pages.navbar import find_start_end_char
from dash_iconify import DashIconify
from pages.config import *
import seaborn as sns

dash.register_page(__name__,  path_template="/article/<gddid>")

original = None
results = None
color_palette = sns.color_palette("RdYlGn", 100).as_hex()


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
    
    relevance_score = round(original["relevance_score"], 2) * 100
    
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
                    "labelWrapper":{
                        "font-color": "white",
                    },
                    "track": {
                        "background-color": "green",
                        "color": "white"
                }},
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
                style={"padding-left": "1rem"}
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
                       "padding-left": "1rem"},
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
                                "Original Text: ",
                                html.Label(id="entity-text",
                                           style={"font-weight": "bold"}),
                                dmc.TextInput(
                                    id="corrected-text",
                                    placeholder="Add corrected text here",
                                    style={"width": 200},),
                                dmc.Button(
                                    "Correct",
                                    id="correct-button",
                                    color="lime",
                                    variant="outline",
                                ),
                            ],
                            style={"anchor": "middle", "justify": "center"}
                        )
                    ], lg=8),
                    dbc.Col([], lg=2),
                    dbc.Col([
                        dmc.Group([
                            dmc.Button(
                                "Delete Entity",
                                id="delete-restore-button",
                                color="red",
                                leftIcon=DashIconify(icon="dashicons-trash", height=16),
                                disabled=True,
                            )
                        ], id="button-group")
                    ], lg=2)
                ],
            ),
            dmc.Tabs(
                id="section-tabs",
                color="red",
                orientation="horizontal",
                style={"padding-top": "1rem"}
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
                                    dmc.Text(
                                        "Home",
                                        style=nav_text_style),
                                    id="home-button",
                                    leftIcon=DashIconify(
                                        icon="dashicons-arrow-left-alt", height=16),
                                    style=nav_button_style,
                                ),
                                dcc.Location(id='location_home', refresh=True),
                                # dcc.Location(id='location-irrelevant', refresh=True),
                                # dcc.Location(id='location-submit', refresh=True),
                            ],
                            align="left",
                            lg=1,
                            md=2,
                            sm=3,
                            width=12,
                            style={"margin-left": "10px"},
                        ),
                        dbc.Col([
                            html.Div([
                                dmc.Text("Relevance Score: ",
                                        style=relevance_score_style),
                                dmc.RingProgress(
                                    id="ring-progress",
                                    sections=[{
                                        "value": relevance_score,
                                        "color": color_palette[int(relevance_score)],
                                    }],
                                    label=dmc.Center(dmc.Text(f"{int(relevance_score)}%",
                                                            style={"font-size": "1rem",
                                                                    "font-weight": "bold"})),
                                    size=80,
                                    thickness=10,
                                    roundCaps=True,
                                    style=progress_ring_style,
                                ),
                            ])
                        ],  align="center",
                            lg=2,
                            md=3,
                            sm=4,
                            style={
                                "position": "relative",
                                "left": "2%"
                        }),
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
                                    ],
                                    position="center",
                                ),
                            ],
                            align="center",
                            lg=7,
                            md=5,
                            sm=2,
                            width=12,
                            style={
                                "position": "relative",
                                "right": "6%"
                            },
                        ),
                        dbc.Col(
                            [
                                # External link to the article
                                dmc.NavLink(
                                    label=dmc.Text(
                                        "Go to Article",
                                        style=nav_text_style),
                                    rightSection=DashIconify(
                                        icon="dashicons-admin-links", height=16),
                                    variant="filled",
                                    active=True,
                                    href="http://doi.org/" + \
                                    original["doi"],
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
                                "left": "2.5%"},
                        ),
                    ])
                ],
            ),
            html.Br(),
            dcc.Store(id="results", data=[results]),
            dbc.Row(
                [
                    dbc.Col(sidebar, width=12, lg=3, className="g-0"),
                    dbc.Col(content, width=12, lg=9, className="g-0"),
                ],
            ),
        ],
    ),
        position="top-right",
        autoClose=3000)

    return layout

# Collapse the accordian when toggling between deleted and extracted entities
@callback(
    Output("accordion", "value"),
    Input("toggle-switch", "checked"),
)
def collapse(checked):
    """Return the value of the accordion to collapse it when toggling between deleted and extracted entities

    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False

    Returns:
        bool: Whether the accordion is collapsed (True) or not (False)
    """
    return None

# Populate accordian
@callback(
    Output("accordion", "children"),
    Input("toggle-switch", "checked"),
    Input("results", "data"),
    prevent_initial_call=True,
)
def get_accordion_items(checked, data):
    """Return the children of the accordion to populate it with the extracted entities
    
    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False)
        data (dict): The data from the previous page
    
    Returns:
        list: The children of the accordion
    """
    children = []

    for label, name in entity_name_mapping.items():
        children.append(
            dmc.AccordionItem([
                dmc.AccordionControl(
                    dmc.Group([
                        dmc.Text(name),
                        dmc.Badge(
                            dmc.Text(
                                f"{len([ent for ent in results['entities'][label].values() if ent['deleted'] != checked])}",
                                style=review_badge_style
                            ),
                            p=0,
                            style={"background-color": "#b8864b"},
                            variant="filled",
                            sx={"width": 17, "height": 17,
                                "pointerEvents": "none"}
                        )
                        ])),
                dmc.AccordionPanel([
                    html.Div(
                        [
                            dmc.ChipGroup(
                                id=entity_id_mapping[label],
                                value=None,
                                multiple=False,
                                
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
    prevent_initial_call=True,
)
def update_button(checked):
    """Return the children of the button group to update the button to either delete or restore entities
    
    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False)
    
    Returns:
        list: The children of the button group
    """
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
    """Return the href of the home button to redirect to the home page
    
    Args:
        n_clicks (int): The number of times the home button has been clicked
    
    Returns:
        str: The href of the home button
    """
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
    """Return the children of the chips to update the chips on screen load
    
    Args:
        checked (bool): Whether the toggle switch is checked (True) or not (False)
        data (dict): The data from the previous page
    Returns:
        list: The children of the chips
    """
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
                # Use the updated name for the chip
                if values["corrected_name"] != None:
                    name = values["corrected_name"]
                else:
                    name = ent
                    
                chips[f"{entity}"].append(
                    dmc.Chip(
                        dmc.Group([
                            name,
                            dmc.Badge(
                                dmc.Text(f"{len(values['sentence'])}",
                                         style=review_badge_style),
                                p=0,
                                variant="filled",
                                style={"background-color": "#b8864b"},
                                sx={"width": 17, "height": 17,
                                    "pointerEvents": "none"}
                            )
                        ]),
                        value=ent,
                        variant="outline",
                        styles=toggle_style,
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
    """Return the values of the chips to unselect all chips when the accordian value changes
    
    Args:
        accordian (str): The value of the accordian
    
    Returns:
        list: The values of the chips
    """
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
def chips_values(site,
                 region,
                 taxa,
                 geog,
                 alti,
                 age,
                 email,
                 accordian):
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
    
    Returns:
        list: The children of the entity text
    """

    if accordian == None:
        return "No entity selected", True, True, ""
    
    for entity, value in results["entities"][accordian].items():
        if entity in [site, region, taxa, geog, alti, age, email]:
            if value["corrected_name"] != None:
                corrected_name = value["corrected_name"]
            else:
                corrected_name = entity

    if accordian == "SITE":
        if site == None:
            return "No entity selected", True, True, ""
        else:
            return site, False, False, corrected_name
    elif accordian == "REGION":
        if region == None:
            return "No entity selected", True, True, ""
        else:
            return region, False, False, corrected_name
            
    elif accordian == "TAXA":
        if taxa == None:
            return "No entity selected", True, True, ""
        else:
            return taxa, False, False, corrected_name
    elif accordian == "GEOG":
        if geog == None:
            return "No entity selected", True, True, ""
        else:
            return geog, False, False, corrected_name
    elif accordian == "ALTI":
        if alti == None:
            return "No entity selected", True, True, ""
        else:
            return alti, False, False, corrected_name
    elif accordian == "AGE":
        if age == None:
            return "No entity selected", True, True, ""
        else:
            return age, False, False, corrected_name
    elif accordian == "EMAIL":
        if email == None:
            return "No entity selected", True, True, ""
        else:
            return email, False, False, corrected_name

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
    
    Returns:
        dict: The updated results store
    """
    
    callback_context = [p["prop_id"] for p in dash.callback_context.triggered][0]
    original_text, _, _, _ = chips_values(site, region, taxa, geog, alti, age, email, accordian)
    
    if callback_context == "new-entity-submit.n_clicks" and submit:
        if new_entity_text != None:
            
            try:
                start, end = find_start_end_char(new_entity_sentence, new_entity_text)
            except:
                start, end = 0, 0
            
            try:
                sentences = pd.DataFrame(results["relevant_sentences"])
                sentid = int(sentences['sentid'].min() - 1)
            except:
                sentences = pd.DataFrame()
                sentid = -1
            
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
                    "sentid": sentid
                }],
                "name": new_entity_text,
                "corrected_name": None,
                "deleted": False,
            }
            results["relevant_sentences"].append({
                "sentid": sentid,
                "text": new_entity_sentence,
            })
            
    elif callback_context == "correct-button.n_clicks" and correct:
        # for ent, values in results["entities"][accordian].items():
        #     if ent == original_text:
        #         values["corrected_name"] = entity
        #         break
        if entity in results["entities"][accordian]:
            for sentence in results["entities"][accordian][original_text]["sentence"]:
                try:
                    start, end = find_start_end_char(sentence['text'], entity)
                except:
                    start, end = 0, 0
                    
                sentence["char_index"]["start"] = start
                sentence["char_index"]["end"] = end
                
                # Add to sentences if not already present
                if sentence not in results["entities"][accordian][entity]["sentence"]:
                    results["entities"][accordian][entity]["sentence"].append(sentence)
            # Delete the old entity
            del results['entities'][accordian][original_text]
            
        else:
            for ent, values in results["entities"][accordian].items():
                if ent == original_text:
                    values["corrected_name"] = entity
                    break

    elif callback_context == "delete-restore-button.n_clicks" and delete:
        for ent, values in results["entities"][accordian].items():
            if ent == original_text:
                values["deleted"] = not values["deleted"]
                break

    return results

# Save the results to the appropriate folder
@callback(
    Output("clicked-output", "children"),
    Input("confirm-submit-button", "n_clicks"),
    Input("save-button", "n_clicks"),
    Input("confirm-irrelevant-button", "n_clicks"),
    State('results', 'data'),
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
        results["status"] = "Completed"
        results["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        gddid = results["gddid"]
        data = json.dumps(results)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
            f.write(data)
        return  dmc.Notification(
                    title="Review Complete!",
                    id="submit-notification",
                    action="show",
                    color="green",
                    message="Proceed to home page",
                    icon=DashIconify(icon="ic:round-celebration"),
                )
    elif callback_context == "confirm-irrelevant-button.n_clicks" and relevant:
        results["status"] = "Non-relevant"
        results["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        gddid = results["gddid"]
        data = json.dumps(results)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
            f.write(data)
        return  dmc.Notification(
                    title="Article Removed!",
                    id="remove-notification",
                    action="show",
                    color="red",
                    message="Proceed to home page",
                    icon=DashIconify(icon="dashicons-remove"),
                )
    elif callback_context == "save-button.n_clicks" and save:
        results["status"] = "In Progress"
        gddid = results["gddid"]
        data = json.dumps(results)
        with open(f"data/data-review-tool/completed/{gddid}.json", "w") as f:
            f.write(data)
        return  dmc.Notification(
                    title="Progress Saved!",
                    id="save-notification",
                    action="show",
                    color="yellow",
                    message="Don't forget to comeback and finish the review",
                    icon=DashIconify(icon="dashicons-saved"), 
                )
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
    Returns:
        list: The list of tabs
    """
    callback_context = [p["prop_id"]
                        for p in dash.callback_context.triggered][0]

    if callback_context == "delete-restore-button.n_clicks":
        return []

    if accordian == None or (site == None and region == None and taxa == None and geog == None and alti == None and age == None and email == None):
        return []
    
    # Key is the tab name, value is a list of texts
    tabs = defaultdict(list)

    # Get all the sentences and corresponding section names
    for entity, values in results["entities"][accordian].items():
        if entity in [site, region, taxa, geog, alti, age, email]:
            sentences = values["sentence"]
            if values['corrected_name'] != None:
                highlight = values['corrected_name']
            else:
                highlight = entity
            for sentence in sentences:
                section_name = sentence["section_name"]
                #TODO: get text using `sentid` attribute
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
                            dmc.Text(dmc.Highlight(text,
                                                   highlight=highlight,
                                                   highlightColor="blue",
                                                   ))
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
                            dmc.Text(
                                f"{len(tabs[tab_name])}",
                                style=review_badge_style),
                            p=0,
                            variant="filled",
                            style={"background-color": "#b8864b"},
                            sx={"width": 17, "height": 17, "pointerEvents": "none"}))
                for tab_name in tabs.keys()]

    # Get the first tab component
    try:
        first_tab = list(tabs.keys())[0]
    except IndexError:
        # Error if the corrected spelling doesn't occur in any sentence
        first_tab = None
    tab_component = dmc.Tabs(
        children=[
            dmc.TabsList(
                dmc_tabs,
                position="center"
            ),
        ],
        variant='outline',
        orientation="horizontal",
        value=first_tab
    )
    tab_component.children.extend(dmc_tabs_content)

    return tab_component

# Enable correct button when corrected text is entered
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