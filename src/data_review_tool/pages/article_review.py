import os
import json
import pandas as pd
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

dash.register_page(__name__,  path_template="/article/<gddid>")

original = None
results = None

def layout(gddid = None):
    try:
        global original
        global results
        # get the metadata of the article
        article = open(f"data/data-review-tool/raw/{gddid}.json", "r")
        original = pd.json_normalize(json.loads(article.read()))
        article = open(f"data/data-review-tool/raw/{gddid}.json", "r")
        results = pd.json_normalize(json.loads(article.read()))

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
                                            for site in original["entities.SITE"][0]
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
                                            for region in original["entities.REGION"][0]
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
                                            for taxa in original["entities.TAXA"][0]
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
                                            for geog in original["entities.GEOG"][0]
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
                                            for alti in original["entities.ALTI"][0]
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
                                            for age in original["entities.AGE"][0]
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
                                            for email in original["entities.EMAIL"][0]
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
                            "Enitity Text: ",
                            html.Label(id="entity-text", style={"font-weight": "bold"}),
                            dmc.TextInput(
                                id="corrected-text",
                                placeholder="Add corrected text here",
                                style={"width": 200},),
                            dmc.Button("Correct",
                                       id = "correct-button"),
                            dmc.Button(
                                "Delete Entity",
                                id="delete-button",
                                color="red",
                                leftIcon=DashIconify(icon="dashicons-trash", height=16),
                                disabled=True,
                            ),
                            
                        ],
                        style={"anchor": "middle", "justify": "center"}
                    ),
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
                        style={"textAlign": "center",
                                "font-weight": "bold",
                                "font-size": "30px",
                                "font-family": "Arial, Helvetica, sans-serif",
                                "color": "#000000",
                                "margin-top": "10px",
                                "margin-bottom": "10px",
                                "padding-top": "10px",
                                "padding-bottom": "10px",
                                "padding-left": "20px",
                                "padding-right": "20px",
                                "text-overflow": "inherit"})),
            dbc.Row(
                html.H4(original["journal_name"][0],
                        style={"textAlign": "center",
                                "font-weight": "semi-bold",
                                "font-size": "20px",
                                "font-family": "Arial, Helvetica, sans-serif",
                                "color": "#000000",
                                "padding-bottom": "10px",
                                "border-bottom": "1px solid #000000",
                                "text-overflow": "inherit"})),
            dbc.Row(
                [   
                    dmc.Group([
                        dbc.Col(
                            [   
                            # home button
                            dmc.Button(
                                "Home",
                                id="home-button",
                                color="blue",
                                leftIcon=DashIconify(icon="dashicons-arrow-left-alt", height=16),
                            ),
                            dcc.Location(id='location_home', refresh=True),],
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
                                        html.Label("If this article is not relevant to NeotomaDB, click here:",),
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
                                rightSection=DashIconify(icon="dashicons-admin-links", height=16),
                                variant="filled",
                                active=True,
                                href="http://doi.org/" + original["doi"][0],
                                target="_blank",
                            )],
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
    Output("delete-button", "disabled"),
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
        if site == None:
            return site, True, True#, True
        else:
            return site,  False, False#, False
    elif accordian == "REGION":
        if region == None:
            return region, True, True#, True
        else:
            return region, False, False#, False
    elif accordian == "TAXA":
        if taxa == None:
            return taxa, True, True#, True
        else:
            return taxa, False, False#, False
    elif accordian == "GEOG":
        if geog == None:
            return geog, True, True#, True
        else:
            return geog, False, False#, False
    elif accordian == "ALTI":
        if alti == None:
            return alti, True, True#, True
        else:
            return alti, False, False#, False
    elif accordian == "AGE":
        if age == None:
            return age, True, True#, True
        else:
            return age, False, False#, False
    elif accordian == "EMAIL":
        if email == None:
            return email, True, True#, True
        else:
            return email, False, False#, False
    else:
        return "No entity selected", True, True#, True

# Update the results store when entity text is changed or it needs to be deleted
@callback(
    Output('results', 'data'),
    Input("correct-button", "n_clicks"),
    Input("delete-button", "n_clicks"),
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
    original_text, _, _ = chips_values(site, region, taxa, geog, alti, age, email, accordian)
    # callback_context = [p["prop_id"] for p in dash.callback_context.triggered][0]
    print(original_text)
    # if callback_context == "entity-text.n_clicks":
    if correct:
        if accordian != None:
            for ent in results[f"entities.{accordian}"][0]:
                if ent["name"] == original_text:
                    ent["name"] = entity
                    break
    # elif callback_context == "delete-button.n_clicks":
    if delete:
            for ent in results[f"entities.{accordian}"][0]:
                if ent["name"] == original_text:
                    results[f"entities.{accordian}"][0].remove(ent)
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
            metadata= metadata.to_dict(orient='records')[0]
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
            metadata= metadata.to_dict(orient='records')[0]
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
        metadata= metadata.to_dict(orient='records')[0]
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
)
def relevant(yes):
    if yes:
        if (yes%2) == 0:
            return None
        else:
            return "Article Removed, please click Submit to remove from the queue"
    else:
        return None
    
# Populate tabs with sentences under corresponding sections
@callback(
    Output("section-tabs", "children"),
    Input("delete-button", "n_clicks"),
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
    callback_context = [p["prop_id"] for p in dash.callback_context.triggered][0]
    
    if callback_context == "delete-button.n_clicks" and n_clicks:
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
        dmc_tabs_content.append(dmc.TabsPanel(
            dmc.Paper(
                children=[
                    dmc.Text(dmc.Highlight(text, highlight=highlight))
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

# Delete the chip when the entity is deleted
@callback(
    Output("chips_site", "children"),
    Output("chips_region", "children"),
    Output("chips_taxa", "children"),
    Output("chips_geog", "children"),
    Output("chips_alti", "children"),
    Output("chips_age", "children"),
    Output("chips_email", "children"),
    Input("delete-button", "n_clicks"),
    State("entity-text", "children"),
    State("chips_site", "children"),
    State("chips_region", "children"),
    State("chips_taxa", "children"),
    State("chips_geog", "children"),
    State("chips_alti", "children"),
    State("chips_age", "children"),
    State("chips_email", "children"),
    State("accordion", "value"),
    prevent_initial_call=True,
)    
def delete_entity(n_clicks, entity, site, region, taxa, geog, alti, age, email, accordian):
    chips = {"SITE": site, "REGION": region, "TAXA": taxa, "GEOG": geog, "ALTI": alti, "AGE": age, "EMAIL": email}
    updated_chips = []
    if n_clicks:
        for ent in results[f"entities.{accordian}"][0]:
            if ent['name'] != entity:
                new_chip = dmc.Chip(
                    ent['name'],
                    value=ent['name'],
                    variant="outline",
                )
                updated_chips.append(new_chip)
        
        chips[accordian] = updated_chips
    
    return chips['SITE'], chips['REGION'], chips['TAXA'], chips['GEOG'], chips['ALTI'], chips['AGE'], chips['EMAIL']

@callback(
    Output("correct-button", "disabled"),
    Input("corrected-text", "value"),
)
def enable_correct_button(corrected_text):
    if corrected_text:
        return False
    else:
        return True