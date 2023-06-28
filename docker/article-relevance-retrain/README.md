# Meta Extractor Article Relevance Retrain Pipeline Docker Image

This docker image contains the data and code required to run article relevance retraining.It adds articles that are marked as "Non-relevant" or "Completed" into the model training process with the aim to improve the model using larger sample. It outputs the new model and the model can be specified for use in the Article Relevance Prediction Pipeline.

To run the article relevance retrain pipeline, the docker image needs to be built first

```bash
docker build -t metaextractor-article-relevance-retrain:v0.0.1 -f docker/article-relevance-retrain/Dockerfile .
```

Running this docker image will:

1. Retrieve the training data used in the original model
2. Retrieve the newly reviewed articles' metadata features and add them as new examples.
3. Train a new logistic regression model using the expanded data.
4. Key model evaluation are outputted in the specified results directory.

## Additional Options Enabled by Environment Variables

The following environment variables can be set to change the behavior of the pipeline:

- `USE_REVIEWED_DATA`: By default is true and use newly reviewed articles to train the model. If set to False, the pipeline will reproduce the original model.
- `TRAIN_DATA_PATH`: The csv file where the processed original sample's metadata were saved. (This should be `data/article-relevance/processed/metadata_processed_embedded.csv`)
- `MODEL_FOLDER`: The folder where newly trained model .joblib file will be saved.
- `RESULT_DIR`: The folder where newly trained model's evaluation results will be saved.
- `REVIEWED_FOLDER_PATH`: The folder where newly reviewed articles' parquet files are saved.

## Sample Docker Compose Setup

Below is a sample docker compose configuration for running the image.

```yaml
version: "0.0.1"
services:
  article-relevance-prediction:
    image: metaextractor-article-relevance-retrain:v0.0.1
    environment:
      - USE_REVIEWED_DATA=True
      - TRAIN_DATA_PATH=data/article-relevance/processed/metadata_processed_embedded.csv
      - MODEL_FOLDER=/outputs/model/
      - RESULT_DIR=/outputs/model_eval/
      - REVIEWED_FOLDER_PATH=data/data-review-tool/

    volumes:
      - ./data/article-relevance/retrain-outputs:/outputs/
```
