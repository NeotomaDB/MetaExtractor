import dash
from dash import dcc, html
import dash_bootstrap_components as dbc


def create_navbar():  
    search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="ms-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
    )
    
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="assets/finding-fossils-logo-symbol_highres.png", height="30px")),
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
                    dbc.Collapse(
                    search_bar,
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
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