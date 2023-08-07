# Meta Extractor Article Relevance Prediction Pipeline Docker Image

This docker image contains the models and code required to run article relevance prediction for research articles on the xDD system. It queries the xDD API article repository based on user-specified parameters, returns the list of articles' DOI as per specified, and predict if the article is relevant to paleoecology/paleoenvironment.

Running this docker image will:

1. Create a JSON file containing a list of xDD articles's gddid and DOI information.
2. Load the article id information from the JSON file, and query CrossRef API to retrieve article metadata.
3. Using metadata and the model to predict the relevance of each article.
4. A parquet file containing the article metadata and the prediction results is created.
5. (Placeholder) Articles that are deemed relevant will be passed to xDD API on the xDD server. The resulting parquet file contains if the API call was success or not for each article.

To run the article relevance prediction pipeline, the docker image needs to be built first

```bash
docker build -t metaextractor-article-relevance-prediction:v0.0.1 -f docker/article-relevance/Dockerfile .
```

## Additional Options Enabled by Environment Variables

Specifying the search criteria of article list and file paths is done through environment variables.

The following environment variables can be set to change the behavior of the pipeline:

Arguments for controlling the xDD API Query:

- `DOI_PATH`: Mandatory. The JSON file containing the queried article list will be saved here.
- `PARQUET_PATH`: Mandatory. This is the folder where processed parquet files are stored.
- `N_RECENT`: This variable can be set to a number to retrieve the n most recently added articles. When this variable is set, no MIN_DATE or MAX_DATE should be set.
- `MIN_DATE`: This variable can be set to establish a earliest date for the range of articles to be included. The date should follow format yyyy-mm-dd.
- `MAX_DATE`: This variable can be set to establish a latest date for the range of articles to be included. The date should follow format yyyy-mm-dd.
- `TERM`: This variable can be set to a word to search for in the article.
- `AUTO_MIN_DATE`: This variable can be set to True or False. If set to True, the pipeline will screen through the date of existing processed parquet files and use the latest date as the earliest date for this run.
- `AUTO_CHECK_DUP`:  This variable can be set to True or False. If set to True, the pipeline will screen through the date of existing processed parquet files and exclude the already-processed articles from the list.

Arguments for controlling the relevance prediction:

- `DOI_FILE_PATH`: This is the path to the JSON ile containing the article list.
- `MODEL_PATH`: This is the path to the classification model.
- `OUTPUT_PATH`: This is the path to save the parquet files (contain article metadata and prediction results)
- `SEND_XDD`: This variable can be set to True or False. If set to True, the articles that predicted to be relevant will be sent to xDD API and go through the name entity extraction (NER) process.

## Sample Docker Compose Setup

Below is a sample docker compose configuration for running the image。

Sample 1: Query by number of most recently added articles

```yaml
version: "0.0.1"
services:
  article-relevance-prediction:
    image: metaextractor-article-relevance-prediction:v0.0.1
    environment:
      # Arguments for xDD API Query
      - DOI_PATH=data/article-relevance/raw
      - PARQUET_PATH=data/article-relevance/processed/prediction_parquet
      - N_RECENT=10
      - MIN_DATE=
      - MAX_DATE=
      - TERM=
      - AUTO_MIN_DATE=False
      - AUTO_CHECK_DUP=False

      # Arguments for relevance prediction script
      - DOI_FILE_PATH=data/article-relevance/raw/gdd_api_return.json
      - MODEL_PATH=models/article-relevance/logistic_regression_model.joblib
      - OUTPUT_PATH=/outputs/
      - SEND_XDD=False

    volumes:
      - ./data/article-relevance/outputs:/outputs/
```

Sample 2: Query by date range

```yaml
version: "0.0.1"
services:
  article-relevance-prediction:
    image: metaextractor-article-relevance-prediction:v0.0.1
    environment:
      # Arguments for xDD API Query
      - DOI_PATH=data/article-relevance/raw
      - PARQUET_PATH=data/article-relevance/processed/prediction_parquet
      - N_RECENT=
      - MIN_DATE=2023-06-04
      - MAX_DATE=2023-06-05
      - TERM=
      - AUTO_MIN_DATE=False
      - AUTO_CHECK_DUP=False

      # Arguments for relevance prediction script
      - DOI_FILE_PATH=data/article-relevance/raw/gdd_api_return.json
      - MODEL_PATH=models/article-relevance/logistic_regression_model.joblib
      - OUTPUT_PATH=/outputs/
      - SEND_XDD=False

    volumes:
      - ./data/article-relevance/outputs:/outputs/
```