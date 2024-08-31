import logging
import os
import subprocess
from urllib.parse import urlparse

# Set up logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def save_url_to_file(url: str, dir_path: str):
    try:
        # Log the start of the process
        logging.info("Starting to process the URL: %s", url)

        # Parse the URL to extract the file name from the last part of the path
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)

        if not file_name:
            logging.error(
                "Failed to parse the URL properly. The file name extracted was empty."
            )
            return

        # Append .html to the filename
        file_name += ".html"
        logging.info("Generated file name: %s", file_name)

        # Construct the full file path
        file_path = os.path.join(dir_path, file_name)
        logging.info("Full file path: %s", file_path)

        # Ensure the directory exists
        if not os.path.exists(dir_path):
            logging.info("Directory does not exist, creating directory: %s", dir_path)
            os.makedirs(dir_path)

        # # Docker command to run SingleFile with the given URL and save it to the generated file path
        # command = f'docker run singlefile "{url}" > "{file_path}"'
        # logging.info("Running command: %s", command)
        # Docker command to run SingleFile with the given URL
        command = ["docker", "run", "singlefile", url]
        logging.debug("Running command: %s", " ".join(command))

        # Open the file in binary write mode and redirect stdout directly to the file
        with open(file_path, "wb") as file:
            process = subprocess.Popen(command, stdout=file, stderr=subprocess.PIPE)
            _, stderr = process.communicate()

            # Log stderr for debugging
            if stderr:
                logging.error("Command error: %s", stderr.decode("utf-8"))

            if process.returncode != 0:
                logging.error("Command failed with return code: %d", process.returncode)
            else:
                logging.info("File saved successfully at: %s", file_path)

        # # Run the command using subprocess
        # process = subprocess.Popen(
        #     command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        # )
        # stdout, stderr = process.communicate()

        # # Log stdout and stderr for debugging
        # if stdout:
        #     logging.debug("Command output: %s", stdout.decode("utf-8"))

        # if stderr:
        #     logging.error("Command error: %s", stderr.decode("utf-8"))

        # if process.returncode != 0:
        #     logging.error("Command failed with return code: %d", process.returncode)
        # else:
        #     logging.info("File saved successfully at: %s", file_path)

    except Exception as e:
        logging.exception("An error occurred while trying to save the URL to the file.")


# Example usage
# url = "https://cloud.google.com/compute/docs/disks/about-regional-persistent-disk"
# dir_path = "/home/franco/Documents/files"  # Directory where the file will be saved
# # save_url_to_file(url, dir_path)
