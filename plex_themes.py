import requests
import xml.etree.ElementTree as ET
import sched
import time
import logging
import threading
import json
import os
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Get Plex server details, token, and update interval from environment variables
PLEX_SERVER_URL = os.getenv('PLEX_SERVER_URL', 'http://localhost:32400')
TOKEN = os.getenv('PLEX_TOKEN', '')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '300'))  # default to 300 seconds

# Define a global variable to store results and a lock for thread safety
results = {}
results_lock = threading.Lock()

# Function to fetch library sections
def get_libraries():
    try:
        headers = {'X-Plex-Token': TOKEN}
        response = requests.get(f"{PLEX_SERVER_URL}/library/sections", headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses
        logging.info("Fetched library sections")
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching library sections: {e}")
        return None

# Function to fetch media items from a library
def get_media_items(library_key):
    try:
        headers = {'X-Plex-Token': TOKEN}
        response = requests.get(f"{PLEX_SERVER_URL}/library/sections/{library_key}/all", headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses
        logging.info(f"Fetched media items for library key: {library_key}")
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching media items for library key {library_key}: {e}")
        return None

# Parse XML response and count items with themes
def count_items_with_themes(media_items_xml):
    try:
        media_items_tree = ET.fromstring(media_items_xml)
        total_items = 0
        theme_count = 0

        for video_node in media_items_tree.findall(".//Video"):
            total_items += 1
            if 'theme' in video_node.attrib:
                theme_count += 1

        for episode_node in media_items_tree.findall(".//Directory"):  # Assuming episodes are under 'Directory' tag
            total_items += 1
            if 'theme' in episode_node.attrib:
                theme_count += 1

        logging.info(f"Counted items with themes: {theme_count}/{total_items}")
        return total_items, theme_count
    except ET.ParseError as e:
        logging.error(f"Error parsing media items XML: {e}")
        return 0, 0

# Function to update data periodically
def update_data(sc):
    global results  # Access the global variable 'results'
    logging.info("Updating data...")

    try:
        libraries_xml = get_libraries()
        
        if libraries_xml is None:
            raise Exception("Failed to fetch libraries XML")

        libraries_tree = ET.fromstring(libraries_xml)

        updated_results = {}

        for library_node in libraries_tree.findall(".//Directory"):
            library_key = library_node.attrib['key']
            library_title = library_node.attrib['title']
            media_items_xml = get_media_items(library_key)

            if media_items_xml is None:
                logging.warning(f"Skipping library key {library_key} due to fetch failure")
                continue

            total_items, theme_count = count_items_with_themes(media_items_xml)

            combined_value = f"{theme_count}/{total_items}"

            updated_results[f'combined_value_{library_title.lower()}'] = combined_value

        with results_lock:
            results = updated_results  # Update the global 'results' variable
            logging.info("Data updated successfully.")
    except Exception as e:
        logging.error(f"Error during update: {e}")

    # Schedule the next update
    sc.enter(UPDATE_INTERVAL, 1, update_data, (sc,))
    logging.info(f"Scheduled next update in {UPDATE_INTERVAL} seconds.")

# Initialize Flask app
app = Flask(__name__)

# Endpoint to serve results
@app.route('/', methods=['GET'])
def get_results():
    logging.info("Received GET request for /")
    with results_lock:
        return jsonify(results)

# Function to run the scheduler in a separate thread
def run_scheduler():
    while True:
        scheduler.run(blocking=False)
        time.sleep(1)  # sleep to prevent high CPU usage

if __name__ == '__main__':
    # Start the scheduler thread
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 1, update_data, (scheduler,))
    logging.info("Scheduled first update immediately.")
    
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    logging.info("Started the scheduler thread.")

    # Start Flask app with custom settings to avoid development server warnings
    app.run(host='0.0.0.0', port=80, debug=False, use_reloader=False)

