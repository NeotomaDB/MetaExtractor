from dash import html, dcc
import dash

dash.register_page(__name__, path="/404")


layout = html.Div(
    [
        html.H1("404 - Page Not Found"),
        html.P("The requested page does not exist."),
        html.P("Please check the URL and try again."),
        dcc.Link("Go back to Home", href="/"),
    ]
)

