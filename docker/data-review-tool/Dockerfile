# Use the official Python base image with your desired version
FROM python:3.10

# Copy the requirements.txt file to the working directory
COPY ./docker/data-review-tool/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR MetaExtractor/

ENV LOG_LEVEL=DEBUG
# Copy the entire repository folder into the container
COPY src ./src

# Expose the port your Dash app is running on
EXPOSE 8050

RUN pip install pyarrow

RUN mkdir -p ./inputs

VOLUME ["/MetaExtractor/inputs"]

# Set the entrypoint command to run your Dash app
#CMD ["python", "src/data_review_tool/app.py"]

ENTRYPOINT python src/data_review_tool/app.py