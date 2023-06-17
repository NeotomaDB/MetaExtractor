# Use the official Python 3.10 image as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app/

# Copy the requirements file to the container
COPY docker/entity-extraction-pipeline/requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader stopwords

# Copy the entire repository folder into the container
COPY src ./src

# Build args
ARG HF_NER_MODEL_NAME
ARG SPACY_NER_MODEL_NAME

# Set env variables for when running the container
ENV HF_NER_MODEL_NAME=${HF_NER_MODEL_NAME}
ENV SPACY_NER_MODEL_NAME=${SPACY_NER_MODEL_NAME}
ENV USE_NER_MODEL_TYPE=huggingface

# Copy in the model defined by the env variable NER_MODEL_NAME from models folder
COPY models/ner/${HF_NER_MODEL_NAME} ./models/ner/${HF_NER_MODEL_NAME} 

COPY models/ner/${SPACY_NER_MODEL_NAME} ./models/ner/${SPACY_NER_MODEL_NAME}

# Set the entry point and command to run the script
ENTRYPOINT ["python", "src/pipeline/entity_extraction_pipeline.py", \
    "--article_text_path", "/app/inputs/sentences_nlp352", \
    "--output_path", "/app/outputs/", "--max_articles", "1", "--max_sentences", "1"]

# Mount the "inputs" and "outputs" folders as volumes
VOLUME ["/app/inputs", "/app/outputs"]