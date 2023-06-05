
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import os

from pages.navbar import create_navbar


app = dash.Dash(__name__, 
                use_pages=True, 
                external_stylesheets=[dbc.themes.BOOTSTRAP], 
                title="MetaExtractor",
                suppress_callback_exceptions=True,)

server = app.server

navbar = create_navbar()

app.layout = html.Div(
    children=
    [
        navbar,
        dash.page_container
        ],
    )


if __name__ == "__main__":
    app.run_server(debug=True)
