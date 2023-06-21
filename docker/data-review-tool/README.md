# Finding Fossils - Data Review Tool Docker Image

This docker image contains `Finding Fossils`, a data review tool built using Dash, Python. It is used to visualize the outputs of the models and verify the extracted entities for inclusion in the Neotoma Database. 

## Docker Compose Setup

We first build the docker image to install the required dependencies that can be run using `docker-compose` as follows:
```bash
docker-compose build
docker-compose up data-review-tool
```

This is the basic docker compose configuration for running the image.

```yaml
version: "3.9"
services:
  data-review-tool:
    build: 
      ...
    ports:
      - "8050:8050"
    volumes:
    - ./data/data-review-tool:/MetaExtractor/data/data-review-tool
```

### Input
The expected inputs are mounted onto the newly created container as volumes and can be dumped in the `data/data-review-tool` folder. The artifacts required by the data review tool to verify a batch of processed articles are:
- A parquet file containing the outputs from the article relevance prediction component.
- A zipped file containing the outputs from the named entity extraction component.

### Output
Once the articles have been verified and the container has been destroyed, we update the same parquet file referenced in the `Input` with the extracted (predicted by the model) and verified (correct by data steward) entities.
