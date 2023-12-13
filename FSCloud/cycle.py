import os
import requests
import schedule
import time

# Set to keep track of processed filenames
processed_files = set()


def upload_file_to_api(file_path, api_url):
    # Prepare the file data`
    files = {'file': open(file_path, 'rb')}

    # Make a POST request to the API endpoint
    response = requests.post(api_url, files=files)

    # Print the API response
    print(response.json())


def job():
    global processed_files  # Use the global set of processed files

    # Specify the local folder path
    local_folder = 'C:/Users/nibra/Downloads/FScloud/'

    # Specify the API endpoint
    api_url = 'http://127.0.0.1:8000/app/api/upload/'

    # Iterate over files in the local folder
    for filename in os.listdir(local_folder):
        file_path = os.path.join(local_folder, filename)

        # Check if the file has already been processed
        if filename not in processed_files:
            # Upload the file to the API
            upload_file_to_api(file_path, api_url)

            # Add the filename to the set of processed files
            processed_files.add(filename)


# Schedule the job to run every 10 seconds
schedule.every(10).seconds.do(job)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
