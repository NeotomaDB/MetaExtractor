# Finding Fossils - Data Review Tool Docker Image

This docker image contains `Finding Fossils`, a data review tool built using Dash, Python. It is used to visualize the outputs of the models and verify the extracted entities for inclusion in the Neotoma Database. 

The expected inputs are mounted onto the newly created container as volumes and can be dumped in any folder. An environment variable is setup to provide the path to this folder. It assumes the following:
1. A parquet file containing the outputs from the article relevance prediction component.
2. A zipped file containing the outputs from the named entity extraction component.
3. Once the articles have been verified we update the same parquet file referenced using the environment variable `ARTICLE_RELEVANCE_BATCH` with the entities verified by the steward and the status of review for the article.

## Additional Options Enabled by Environment Variables

The following environment variables can be set to change the behavior of the pipeline:
- `ARTICLE_RELEVANCE_BATCH`: This variable gives the name of the article relevance output parquet file.
- `ENTITY_EXTRACTION_BATCH`: This variable gives the name of the entity extraction compressed output file.

## Sample Docker Compose Setup

Update the environment variables and the volume paths defined under the `data-review-tool` service in the `docker-compose.yml` file under the root directory. The volume paths are:

`INPUT_PATH`: The path to the directory where the data is dumped. eg. `./data/data-review-tool` (recommended)

```yaml
version: "3.9"
services:
  data-review-tool:
    build: 
      ...
    ports:
      - "8050:8050"
    volumes:
    - {INPUT_PATH}:/MetaExtractor/inputs
    environment:
    - ARTICLE_RELEVANCE_BATCH=sample_parquet_output.parquet
    - ENTITY_EXTRACTION_BATCH=sample_ner_output.zip
```
Then build and run the docker image to install the required dependencies using `docker-compose` as follows:
```bash
docker-compose build
docker-compose up data-review-tool
```
