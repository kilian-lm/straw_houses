# Use an official Python runtime as the base image
FROM python:3.11-slim-buster

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the local files to the container
COPY main.py .
COPY StrawHouseAnalysis.py .
COPY assets/ ./assets/
# Install required packages
RUN pip install --no-cache-dir pandas numpy matplotlib dash

# Expose the port the app runs on
EXPOSE 50001

# Define the command to run the app
CMD ["python", "main.py"]
