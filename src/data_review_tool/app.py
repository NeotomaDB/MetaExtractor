
import dash
import dash_bootstrap_components as dbc
import os
import time
import sys

# src_path = os.path.abspath(os.path.join(".."))
# if src_path not in sys.path:
#     sys.path.append(src_path)

from pages.navbar import create_navbar

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], title="MetaExtractor")

server = app.server

# navbar = dbc.NavbarSimple(
#     dbc.DropdownMenu(
#         [
#             dbc.DropdownMenuItem(page["name"], href=page["path"])
#             for page in dash.page_registry.values()
#             if page["module"] != "pages.not_found_404"
#         ],
#         nav=True,
#         label="More Pages",
#     ),
#     brand="Multi Page App Plugin Demo",
#     color="primary",
#     dark=True,
#     className="mb-2",
# )

navbar = create_navbar()

app.layout = dbc.Container(
    [navbar, dash.page_container],
    fluid=True,
)

if __name__ == "__main__":
    app.run_server(debug=True)
