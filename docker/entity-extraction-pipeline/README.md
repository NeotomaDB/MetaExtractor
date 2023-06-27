# Meta Extractor Entity Extraction Pipeline Docker Image

This docker image contains the models and code required to run entity extraction from research articles on the xDD system. It assumes the following:
1. The raw text is input in the `nlp352` TSV format with either a single article per file or multiple articles denoted by GDD ID
   -  like this sample data from xDD [Link to Sample Data](https://github.com/UW-xDD/xdd-docker-recipe/tree/master/sample_data/nlp352)
2. The raw input data is mounted as a volume to the docker folder `/app/inputs/`
3. The expected output location is mounted as a volume to the docker folder `/app/outputs/`
4. A single JSON file per article is exported into the output folder along with a `.log` file for the processing run.

## Additional Options Enabled by Environment Variables

The following environment variables can be set to change the behavior of the pipeline:
- `USE_NER_MODEL_TYPE`: This variable can be set to `spacy` or `huggingface` to change the NER model used. The default is `huggingface`. This will be used to run batches with each model to evaluate final performance.
- `HF_NER_MODEL_NAME`: The name of the `huggingface-hub` repository hosting the huggingface model artifacts.
- `SPACY_NER_MODEL_NAME`: The name of the `huggingface-hub` repository hosting the spacy model artifacts.
- `MAX_SENTENCES`: This variable can be set to a number to limit the number of sentences processed per article. This is useful for testing and debugging. The default is `-1` which means no limit.
- `MAX_ARTICLES`: This variable can be set to a number to limit the number of articles processed. This is useful for testing and debugging. The default is `-1` which means no limit.
- `LOG_OUTPUT_DIR`: This variable is set to the path of the output folder to write the log file. Default is the directory from which the docker container is run.

## Sample Docker Compose Setup

Update the environment variables defined under the `entity-extraction-pipeline` service in the `docker-compose.yml` file under the root directory. The volume paths are:

- `INPUT_PATH`: The folder containing the raw text `nlp352` TSV file, eg. `./data/entity-extraction/raw/original_files/` (recommended)
- `OUTPUT_PATH`: The folder to dump the final JSON files, eg. `./data/entity-extraction/processed/processed_articles/` (recommended)

Below is a sample docker compose configuration for running the image:
```yaml
version: "0.0.1"
services:
  entity-extraction-pipeline:
    image: metaextractor-entity-extraction-pipeline:v0.0.1
    build: 
        ...
    ports:
      - "5000:5000"
    volumes:
    - {INPUT_PATH}:/app/inputs/
    - {OUTPUT_PATH}:/app/outputs/
    environment:
      - HF_NER_MODEL_NAME=finding-fossils/metaextractor
      - SPACY_NER_MODEL_NAME=en_metaextractor_spacy
      - USE_NER_MODEL_TYPE=huggingface
      - LOG_OUTPUT_DIR=/app/outputs/
      - MAX_SENTENCES=20
      - MAX_ARTICLES=1
```
Then build and run the docker image to install the required dependencies using `docker-compose` as follows:
```bash
docker-compose build
docker-compose up entity-extraction-pipeline
```

