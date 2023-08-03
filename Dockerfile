# Use an official Python runtime as the base image
FROM python:3.11-slim-buster

# Set the working directory inside the container
# WORKDIR /usr/src/app

# Copy the local files to the container
#COPY main.py .
#COPY StrawHouseAnalysis.py .
#COPY assets/ ./assets/

COPY [".", "./"]
# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8080
ENV PORT 8080

# Define the command to run the app
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app.server
