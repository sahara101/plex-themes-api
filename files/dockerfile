# Dockerfile

# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir requests Flask

# Make port 80 available to the world outside this container
EXPOSE 80

# Set environment variables (default values can be overridden by user)
ENV PLEX_SERVER_URL=http://localhost:32400
ENV PLEX_TOKEN=
ENV UPDATE_INTERVAL=300

# Run the application
CMD ["python", "plex_themes.py"]
