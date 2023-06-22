import os
import sys
from dash import html
import dash_bootstrap_components as dbc

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data_review_tool.pages.config import *

def create_navbar():

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.Div([
                   html.Img(src= os.path.join("/assets",
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
