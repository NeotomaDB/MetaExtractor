import dash
import sys
import os
from pages.config import *

dash.register_page(__name__)

from dash import dash, dcc, html, Input, Output, callback
import os

with open(os.path.join("src",
                        "data_review_tool",
                        "assets",
                        'about.md'), 'r') as file:
    markdown_text = file.read()

layout = html.Div(
    [
        html.Div(
            [
                html.H2("Finding Fossils Demo",
                        style=h2_style),
                html.Video(
                    controls=True,
                    src= os.path.join("assets",
                                      "data_review_tool_demo.mp4"),
                    style={"width": "50%", "height": "auto"},
                ),
                dcc.Markdown(
                    children=[
                        markdown_text,
                    ],
                ),
            ],
            style={'text-align': 'center',
                   "width": '75%',
                   },
        ),
    ],
    style={'display': 'flex', 'justify-content': 'center'}    
)