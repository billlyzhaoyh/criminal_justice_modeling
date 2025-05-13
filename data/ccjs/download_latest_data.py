import os
from datetime import datetime

import pandas as pd
import requests

# Define the base URL and output directory
BASE_URL = "https://criminal-justice-delivery-data-dashboards.justice.gov.uk/criminal_justice_delivery_data_q3_2024_v4.csv"
OUTPUT_DIR = "./data/ccjs/raw"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_latest_data():
    """
    Downloads the latest CCJS data from the specified URL and saves it to the raw data folder.
    """
    try:
        # Download the data
        response = requests.get(BASE_URL)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get current date for the filename
        current_date = datetime.now().strftime("%B-%Y")

        # Create the output filename
        output_filename = f"criminal_justice_delivery_data_{current_date}.csv"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Save the data
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"Successfully downloaded CCJS data to {output_path}")

        # Read and display basic information about the downloaded data
        df = pd.read_csv(output_path)
        print("\nData Overview:")
        print(f"Shape: {df.shape}")
        print("\nColumns:")
        for col in df.columns:
            print(f"- {col}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    download_latest_data()
