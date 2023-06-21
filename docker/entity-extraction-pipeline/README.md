# Meta Extractor Entity Extraction Pipeline Docker Image

This docker image contains the models and code required to run entity extraction from research articles on the xDD system. It assumes the following:
1. The raw text is input in the `nlp352` TSV format with either a single article per file or multiple articles denoted by GDD ID
   -  like this sample data from xDD [Link to Sample Data](https://github.com/UW-xDD/xdd-docker-recipe/tree/master/sample_data/nlp352)
2. The raw input data is mounted as a volume to the docker folder `/app/inputs/`
3. The expected output location is mounted as a volume to the docker folder `/app/outputs/`
4. A single JSON file per article is exported into the output folder along with a `.log` file for the processing run.
5. An environment variable `LOG_OUTPUT_DIR` is set to the path of the output folder. This is used to write the log file. Default is the directory from which the docker container is run.

## Additional Options Enabled by Environment Variables

The following environment variables can be set to change the behavior of the pipeline:
- `USE_NER_MODEL_TYPE`: This variable can be set to `spacy` or `huggingface` to change the NER model used. The default is `huggingface`. This will be used to run batches with each model to evaluate final performance.
- `MAX_SENTENCES`: This variable can be set to a number to limit the number of sentences processed per article. This is useful for testing and debugging. The default is `-1` which means no limit.
- `MAX_ARTICLES`: This variable can be set to a number to limit the number of articles processed. This is useful for testing and debugging. The default is `-1` which means no limit.

## Sample Docker Run & Compose Setup

Below is a sample docker run command for running the image:
- the `$(id -u)` is used to run the docker container as the current user so that the output files are not owned by root
- the `LOG_OUTPUT_DIR="../outputs/"` is different from the docker compose as it is relative to the current directory which from Docker run starts in `app` folder
- for git bash on windows the `/${PWD}` is used to get the current directory and the forward slash is important to get the correct path
```bash
docker run -u $(id -u) -p 5000:5000 -v /${PWD}/data/entity-extraction/raw/original_files/:/inputs/ -v /${PWD}/data/entity-extraction/processed/processed_articles/:/outputs/ --env LOG_OUTPUT_DIR="../outputs/" metaextractor-entity-extraction-pipeline:v0.0.2
```

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
    - ./data/raw/:/app/inputs/
    - ./data/processed/:/app/outputs/
    environment:
      - USE_NER_MODEL_TYPE=huggingface
      - LOG_OUTPUT_DIR=/app/outputs/
      - MAX_SENTENCES=20
      - MAX_ARTICLES=1
```