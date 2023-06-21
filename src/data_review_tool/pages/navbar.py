import os
from dash import html
import dash_bootstrap_components as dbc
from pages.config import *

def create_navbar():

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.Div([
                   html.Img(src= os.path.join("assets",
                                              "finding-fossils-logo-symbol_highres.png"), 
                            height="55px",
                            style={"position": "relative", "left": "-60px"}),
                ], style={"display": "flex"}),
                html.Div([
                    html.H3(
                        "Finding Fossils",
                        style=h3_style,
                    ),
                ], style={"display": "flex"}),
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink("Home", 
                                        href="/", 
                                        style={
                                            "color": "white",
                                            "font-family": "Futura"})),
                        dbc.NavItem(
                            dbc.NavLink("About", 
                                        href="/about",
                                        style={
                                            "color": "white",
                                            "font-family": "Futura"})),
                    ],
                    className="ml-auto",
                    navbar=True,
                    pills=True,
                    style={"position": "relative", "right": "-60px"},
                ),
            ],
        ),
        color="#b8864b",
        dark=True,
    )
    return navbar

def find_start_end_char(text, entity):
    """Find the start and end character of an entity in a text.

    Args:
        text (str): Text to search for entity.
        entity (str): Entity to search for in text.

    Returns:
        start (int): Start character of entity in text.
        end (int): End character of entity in text.
    """
    start = text.find(entity)
    if start == -1:
        end = -1
    else:
        end = start + len(entity)
    return start, end