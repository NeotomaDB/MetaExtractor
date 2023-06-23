# Author: Shaun Hutchinson,
# Date: 2023-06-22
import dash
import sys
import os
from dash import html
import os
import dash_player as dp

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data_review_tool.pages.config import *

dash.register_page(__name__)


layout = html.Div(
    [
        html.H1("About Finding Fossils"),
        html.P(
            "Finding Fossils is a data review tool as part of the project between Neotoma DB (Simon Goring and Soccoro Dominguez) and UBC MDS (Kelly Wu, Jenit Jain, Ty Andrews, and Shaun Hutchinson)."
        ),
        html.H2("Finding Fossils Demo"),
        dp.DashPlayer(
            id="player",
            url="https://youtu.be/CSXBJ0fr0sM",
            controls=True,
            width="100%",
            height="250px",
        ),
        html.H2("How the app works"),
        html.H3("Home Page"),
        html.P(
            "From the home page, users can access three main tabs of data articles that have been extracted for review."
        ),
        html.Ol(
            [
                html.Li(
                    "Current Articles are articles that are ready for review. Those with a status False have not been reviewed yet. Those with a status In Progress are articles that have reviews started and changes saved, but the review is not yet complete."
                ),
                html.Li(
                    "Completed Articles are those articles that have been reviewed and submitted. Changes can still be made if you open these files and click Submit, or Save which changes the status of the file to In Progress again."
                ),
                html.Li(
                    "Irrelevant Articles are not relevant to the Neotoma Database and have been extracted accidentally (false positives). These articles can be used to retrain the article relevance model for improved accuracy."
                ),
            ]
        ),
        html.Center(
            html.Img(
                src="../assets/about_assets/home.png",
                alt="Home Page",
                style={"width": "100%", "height": "auto"},
            )
        ),
        html.H3("Article Review"),
        html.P(
            "Once an article has been selected from the Home Page, the user is directed to the article relevance page. Several functionalities have been implemented to ensure a quick traversal and verification of an article."
        ),
        html.Ul(
            [
                html.Li([html.Strong("Home:"), " button to return to the Home Page."]),
                html.Li(
                    [
                        html.Strong("Relevance Score:"),
                        " indicator showing the prediction results from the article relevance model.",
                    ]
                ),
                html.Li(
                    [
                        html.Strong("Mark as irrelevant:"),
                        " button to move the article to the Irrelevant Articles tab on the Home Page. This will remove the article from the queue of articles to be reviewed and can be used to retrain the article relevance model.",
                    ]
                ),
                html.Li(
                    [
                        html.Strong("Go to Article:"),
                        " button to open the article in a new tab.",
                    ]
                ),
                html.Li(
                    [
                        html.Strong("Save:"),
                        " button to save your changes but not submit the article. This will save your changes and will keep the article in the Current Articles tab on the Home Page with a status of In Progress.",
                    ]
                ),
                html.Li(
                    [
                        html.Strong("Submit:"),
                        " button to submit the article once the review of the article is complete. This will save all of the changes that you have made to the article and will move the article to the Completed Articles tab on the Home Page.",
                    ]
                ),
            ]
        ),
        html.H4("Reviewing the Article"),
        html.P(
            "On the left hand side of the page, there are accordions for each entity type found in the article. The number displayed beside the entity type indicates how many different entities are found in the article. Clicking on the accordion will open the list of entities. Clicking on the entity will open the entity review page that lists the section tabs under which the entities occur along with the corresponding sentences."
        ),
        html.Center(
            html.Img(
                src="../assets/about_assets/accordions.png",
                alt="Accordions",
                width="400",
            )
        ),
        html.H4("Entity Review"),
        html.P(
            "On the entity review page, you will see the Original Text which will display the label that the Entity Extraction model has extracted. Below this will be tabs of each of the sections of the journal article that this entity has been found in. Under each tab will be the sentences in which the entity has been found. The entity has been highlighted in blue. As a result of the scanning of articles from PDFs through Optical Character Recognition there could be issues with the text. If you see any issues with the text, you can edit the text in the text box below the sentence. Once you have made your changes, you can click the Correct button to save your changes. If you would like to delete the entity, you can click the Delete button. This will remove the entity from the accordion and will be reflected in the entity count on the left hand side of the article review page. If the entity is correct, simply move on to the next entity."
        ),
        html.Center(
            html.Img(
                src="../assets/about_assets/entity_review.png",
                alt="Entity Review",
                style={"width": "100%", "height": "auto"},
            )
        ),
        html.H4("Adding a new entity"),
        html.P(
            "If through the process of reviewing the article you come across an entity that was not extracted by the Entity Extraction model, you can add a new entity. To do this, click the Add New Entity button. This will open a popup in which you can add the entity you have found. The information that you need to include here is the Entity Name, the Sentence that you found this entity in, as well as the Section Name of the article it was found in. Once you have added the necessary information, click the Add button. This will add the entity to the entity list on the left hand side of the article review page. You can then click on the entity to open the entity review page and make any changes to the entity that you would like."
        ),
        html.Center(
            html.Img(src="../assets/about_assets/new_entity.png", alt="Add New Entity")
        ),
        html.H4("Restoring an entity"),
        html.P(
            "If you have deleted an entity by accident, you can restore the entity. To do this, select the Show deleted entity button on the below the accordions."
        ),
        html.Center(
            html.Img(
                src="../assets/about_assets/deleted_toggle.png",
                alt="Show Deleted Entity",
            )
        ),
        html.P(
            "From there, select the entity and click the Restore button on the entity review page. This will restore the entity to the entity list on the left hand side of the article review page."
        ),
        html.Center(
            html.Img(
                src="../assets/about_assets/restore.png",
                alt="Restore Entity",
                style={"width": "100%", "height": "auto"},
            )
        ),
    ],
    style={
        "padding-left": "10%",
        "padding-right": "10%",
        "font-family": "Arial, Helvetica, sans-serif",
    },
)
