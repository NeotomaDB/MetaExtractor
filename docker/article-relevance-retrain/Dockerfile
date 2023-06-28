# Use the official Python 3.10 image as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app/

# Copy the requirements file to the container
COPY docker/article-relevance-retrain/requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire repository folder into the container
COPY src ./src

# Copy the model folder into the container
COPY models/article-relevance ./models/article-relevance

# Copy the data folder into the container
COPY data/article-relevance ./data/article-relevance

# Copy the shell script to the container
COPY docker/article-relevance-retrain/run-retrain.sh .

# Make the shell script executable
RUN chmod +x run-retrain.sh

# Mount volumes
RUN mkdir -p /output
VOLUME ["/output"]

# Set the entry point for the Docker container
ENTRYPOINT ["./run-retrain.sh"]
