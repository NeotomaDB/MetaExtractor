import dash

dash.register_page(__name__, path="/")

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc

df = px.data.medals_wide(indexed=True)

table_header = [
            html.Thead(html.Tr([html.Th("Article"), html.Th("DOI"), html.Th("Status"), html.Th("Date Added"), html.Th("Date Updated"), html.Th("Review")]))
        ]
            
row1 = html.Tr([html.Td("Dapibus ac facilisis in "), 
                        html.Td("doi.org.123445"),
                        html.Td("In Progress"),
                        html.Td("2023-05-29"),
                        html.Td("2023-05-29"),
                        html.Td("Review")
                        ])
row2 = html.Tr([html.Td("Dapibus ac facilisis in "), 
                        html.Td("doi.org.123445"),
                        html.Td("Completed"),
                        html.Td("2023-05-29"),
                        html.Td("2023-05-29"),
                        html.Td("Review")
                        ])

current_table = [html.Tbody([row1])]

completed_table = [html.Tbody([row2])]
        

layout = html.Div(
    [
        html.P("Current Articles"),
        dbc.Table(table_header + current_table, bordered=True),
        html.P("Completed Articles"),
        dbc.Table(table_header + completed_table, bordered=True)
    ]
)


