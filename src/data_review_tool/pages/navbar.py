import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import json


def create_navbar():

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="/assets/finding-fossils-logo-symbol_highres.png", height="30px")),
                             dbc.Col("MetaExtractor", className="navbar-brand"),
                        ],
                    ),
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink("Article Review", href="/")),
                        dbc.NavItem(
                            dbc.NavLink("About", href="/about")),
                    ],
                    className="ml-auto",
                    navbar=True,
                    pills=True,
                ),
            ],
        ),
        color="tan",
        # dark=True,
    )
    return navbar


def segment_control(data, selected_entity, selected_entity_type):
    tab_data = {}
    tab_data_list = []
    for entity in data[f"entities.{selected_entity_type}"][0]:
        if entity["name"] == selected_entity:
            section_name = entity["sentence"][0]["section_name"]
            text_value = entity["sentence"][0]["text"]

            if section_name in tab_data:
                tab_data[section_name].append(text_value)
            else:
                tab_data[section_name] = [text_value]
    return [{"label": label, "value": values} for label, values in tab_data.items()]

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
    end = start + len(entity)
    return start, end