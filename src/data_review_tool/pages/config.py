# Tab header on home page
tab_header_style = {
    "font-weight": "bold",
    "font-size": "25px",
    "font-family": "Lato",
    "padding-top": "20px",
    "padding-bottom": "10px"
}

#Home page badge style
badge_style = {
    "background-color": "#b8864b",
    "font-size": "15px",
}

# Data table conditional style
table_conditional_style = [
    {'if': {'column_id': 'Review'}, 
        'backgroundColor': 'blue', 
        'text_align':'center',
        'color': 'white',
        "fontWeight": "1000",
        'font-family': 'montserrat',},
    {'if': {'column_id': 'Article'}, 
        'text_align':'left',
        'font-family': 'montserrat',},
    {'if': {'column_id': 'Status'},
        'fontWeight': 'bold'},
]

# Data table data style
table_data_style = {
    'whiteSpace': 'normal',
    'height': 'auto',
    'lineHeight': '15px',
    'font-family': 'montserrat',
}

# Data table cell style
table_cell_style = {
    'textAlign': 'center',
    'font-family': 'montserrat',
    "background-color": "#fffff0",
}

# Data table header style
table_header_style = {
    "text-align": "center",
    'font-family': 'montserrat',
    "font-weight": "bold"
}
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
    "padding": "0.3rem 1rem",
    "background-color": "#fffff0",
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

h3_style = {
    "color": "white",
    "textAlign": "right",
    "font-size": "45px",
    "font-weight": "bold",
    "font-family": "Futura",
    "margin-bottom": "10px",
    "padding-left": "100px",
    "text-overflow": "inherit",
    "background-color": "#b8864b",
    "text-shadow": "1px 1px #000000"
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

entity_add_mapping = {
    "SITE": "new_site",
    "REGION": "new_region",
    "TAXA": "new_taxa",
    "GEOG": "new_geog",
    "ALTI": "new_alti",
    "AGE": "new_age", 
    "EMAIL": "new_email"
}