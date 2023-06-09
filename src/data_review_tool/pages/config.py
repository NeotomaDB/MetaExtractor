# Describe the configuration and the HTML styles for the review page
chip_style={"scrollbar-width": "none", 
        "overflow": "auto",
        "height": "auto",
        "max-height": "200px"}

tab_body_style = {
    "scrollbar-width": "none", 
    "overflow": "auto",
    "height": "auto",
    "max-height": "500px"
}
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

h2_style = {
    "textAlign": "center",
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
    "text-overflow": "inherit"
}

h4_style = {
    "textAlign": "center",
    "font-weight": "semi-bold",
    "font-size": "20px",
    "font-family": "Arial, Helvetica, sans-serif",
    "color": "#000000",
    "padding-bottom": "10px",
    "border-bottom": "1px solid #000000",
    "text-overflow": "inherit"
}

entity_name_mapping = {
    "SITE": "Site Name", 
    "REGION": "Region Name",
    "TAXA": "Taxa",
    "GEOG": "Geographic Coordinates",
    "ALTI": "Altitude",
    "AGE": "Age", 
    "EMAIL": "Email Address"
}

entity_id_mapping = {
    "SITE": "chips_site",
    "REGION": "chips_region",
    "TAXA": "chips_taxa",
    "GEOG": "chips_geog",
    "ALTI": "chips_alti",
    "AGE": "chips_age", 
    "EMAIL": "chips_email"
}