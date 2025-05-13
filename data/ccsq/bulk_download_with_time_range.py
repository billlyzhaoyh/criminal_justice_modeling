import argparse
import os
import re

import requests
from bs4 import BeautifulSoup


def fetch_links(url):
    """Fetches and returns a dictionary of links with their corresponding text from the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    links_dict = {}
    for link in soup.find_all(
        "a",
        string=lambda text: text
        and text.startswith("Criminal court statistics quarterly"),
    ):
        href = link.get("href")
        if href and not href.startswith("http"):
            href = "https://www.gov.uk" + href
        links_dict[link.text.strip()] = href
    return links_dict


def filter_links_by_year(links_dict, start_year, end_year):
    """Filters the links dictionary to include only entries within the specified year range."""
    filtered_dict = {}
    year_pattern = re.compile(r"(\d{4})$")
    for text, href in links_dict.items():
        match = year_pattern.search(text)
        if match:
            year = int(match.group(1))
            if start_year <= year <= end_year:
                filtered_dict[text] = href
    return filtered_dict


def download_ods_file(page_url, download_dir):
    """Downloads the ODS file linked as 'Tables' from the given page URL."""
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links with text 'tables'
    tables_links = [
        link for link in soup.find_all("a") if link.text and "tables" in link.text
    ]

    # Ensure there's exactly one 'tables' link
    if len(tables_links) != 1:
        raise ValueError(
            f"Expected exactly one 'tables' link on {page_url}, found {len(tables_links)}."
        )

    # Get the href attribute
    ods_url = tables_links[0].get("href")
    if not ods_url.endswith(".ods"):
        raise ValueError(f"The 'tables' link does not point to an ODS file: {ods_url}")

    # Ensure the href is an absolute URL
    if not ods_url.startswith("http"):
        ods_url = "https://www.gov.uk" + ods_url

    # Download the ODS file
    ods_response = requests.get(ods_url)
    ods_response.raise_for_status()

    # Extract the filename from the URL
    filename = os.path.basename(ods_url)

    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    # Define the full path to save the file
    file_path = os.path.join(download_dir, filename)

    # Save the ODS file
    with open(file_path, "wb") as file:
        file.write(ods_response.content)

    print(f"Downloaded {filename} to {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and filter Criminal Justice System statistics quarterly links by year range and download associated ODS files."
    )
    parser.add_argument(
        "--start_year",
        type=int,
        default=2022,
        help="The starting year of the range (default: 2022).",
    )
    parser.add_argument(
        "--end_year",
        type=int,
        default=2025,
        help="The ending year of the range (default: 2025).",
    )
    parser.add_argument(
        "--download_dir",
        type=str,
        default="./data/ccsq/raw",
        help="Directory to download ODS files (default: ./data/ccsq/raw).",
    )
    args = parser.parse_args()

    url = "https://www.gov.uk/government/collections/criminal-court-statistics"
    links_dict = fetch_links(url)
    filtered_links = filter_links_by_year(links_dict, args.start_year, args.end_year)

    for text, href in filtered_links.items():
        print(f"Processing: {text}\nLink: {href}")
        try:
            download_ods_file(href, args.download_dir)
        except Exception as e:
            print(f"Error processing {href}: {e}")


if __name__ == "__main__":
    main()
