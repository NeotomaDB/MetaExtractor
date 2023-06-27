import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import os
import zipfile

from pages.navbar import create_navbar


app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "src/data_review_tool/assets/styles.css",
    ],
    title="Finding Fossils",
    suppress_callback_exceptions=True,
)

server = app.server

navbar = create_navbar()


app.layout = html.Div(
    children=[navbar, dash.page_container],
    style={
        "width": "100%",
        "height": "100%",
        "overflow": "hidden",
    },
)
app._favicon = "finding-fossils.ico"

# Has the file been unzipped
unzipped = False

if __name__ == "__main__":
    
    if not unzipped:
        # Create folder to unzip the entity extraction compressed output from xDD servers
        if not os.path.exists("/entity_extraction"):
            os.mkdir("/entity_extraction")
        
        with zipfile.ZipFile(f"/MetaExtractor/inputs/{os.environ['ENTITY_EXTRACTION_BATCH']}", 
                             mode = 'r', 
                             allowZip64 = True) as file:    
            file.extractall("/entity_extraction")
            
        unzipped = True
        
    app.run_server("0.0.0.0", debug=True, port=8050)
