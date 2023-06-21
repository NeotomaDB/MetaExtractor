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
ENV MAX_ARTICLES=-1
ENV MAX_SENTENCES=-1

# Copy in the model defined by the env variable NER_MODEL_NAME from models folder
COPY models/ner/${HF_NER_MODEL_NAME} ./models/ner/${HF_NER_MODEL_NAME} 
COPY models/ner/${SPACY_NER_MODEL_NAME} ./models/ner/${SPACY_NER_MODEL_NAME}

# non-root user control inspired from here: https://stackoverflow.com/questions/66349101/docker-non-root-user-does-not-have-writing-permissions-when-using-volumes
# Create a non-root user that owns the input/outputs directory by default
RUN useradd -r extraction-user          # no specific user ID
RUN mkdir /inputs && chown extraction-user /inputs
RUN mkdir /outputs && chown extraction-user /outputs
# Mount the "inputs" and "outputs" folders as volumes
VOLUME ["/inputs", "/outputs"]

# Set the entry point and command to run the script
USER extraction-user  
RUN ls -alp /app
ENTRYPOINT python src/pipeline/entity_extraction_pipeline.py \
    --article_text_path /inputs/ \
    --output_path /outputs/ \
    --max_articles ${MAX_ARTICLES} \
    --max_sentences ${MAX_SENTENCES}