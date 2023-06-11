import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import json
import dash_mantine_components as dmc

def create_navbar():

    navbar = dbc.Navbar(
        dbc.Container(
            [
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="/assets/finding-fossils-logo-symbol_highres.png", height="30px")),
                            dbc.Col(
                                dmc.Text(
                                    "Finding Fossils",
                                    style={"color": "#FFFFF0",
                                           "font-size": "2.3rem",
                                           "font-weight": "bold",
                                           "font-family": "Futura"
                                    }
                                ),
                                className="navbar-brand"),
                        ],
                    ),
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink("Article Review", href="/", style={"color": "#FFFFF0"})),
                        dbc.NavItem(
                            dbc.NavLink("About", href="/about", style={"color": "#FFFFF0"})),
                    ],
                    className="ml-auto",
                    navbar=True,
                    pills=True,
                ),
            ],
        ),
        color="tan",
        dark=True,
    )
    return navbar

# The following two functions were taken from https://stackoverflow.com/questions/54776916/inverse-of-pandas-json-normalize
def _get_nested_fields(df: pd.DataFrame):
    """Return a list of nested fields, sorted by the deepest level of nesting first."""
    nested_fields = [*{field.rsplit(".", 1)[0] for field in df.columns if "." in field}]
    nested_fields.sort(key=lambda record: len(record.split(".")), reverse=True)
    return nested_fields

def df_denormalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a normalised DataFrame into a nested structure.

    Fields separated by '.' are considered part of a nested structure.
    """
    nested_fields = _get_nested_fields(df)
    for field in nested_fields:
        list_of_children = [column for column in df.columns if field in column]
        rename = {
            field_name: field_name.rsplit(".", 1)[1] for field_name in list_of_children
        }
        renamed_fields = df[list_of_children].rename(columns=rename)
        df[field] = json.loads(renamed_fields.to_json(orient="records"))
        df.drop(list_of_children, axis=1, inplace=True)
    return df

def find_start_end_char(text, entity):
    start = text.find(entity)
    if start == -1:
        end = -1
    else:
        end = start + len(entity)
    return start, end