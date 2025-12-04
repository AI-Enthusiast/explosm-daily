"""
Explosm Comic Scraper

This module provides functionality to scrape Explosm (Cyanide & Happiness) comics,
including the comic image, title, and author information. It fetches the current
latest comic from the Explosm website.

Usage:
    python scraper.py
"""

import datetime
import os
from typing import Optional, Dict
from bs4 import BeautifulSoup
import requests


# Constants
EXPLOSM_BASE_URL = "https://explosm.net/"
INVALID_FILENAME_CHARS = ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.']


def sanitize_filename(filename: str) -> str:
    """
    Remove characters from a string that are invalid in filenames.

    Args:
        filename: The original filename string to sanitize

    Returns:
        A sanitized filename string with invalid characters removed
    """
    return ''.join(char for char in filename if char not in INVALID_FILENAME_CHARS)


def fetch_webpage(url: str) -> Optional[BeautifulSoup]:
    """
    Fetch and parse a webpage into a BeautifulSoup object.

    Args:
        url: The URL of the webpage to fetch

    Returns:
        BeautifulSoup object if successful, None if request fails
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_comic_data(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    """
    Extract comic data (image URL, date, author) from parsed HTML.

    Args:
        soup: BeautifulSoup object containing the parsed Explosm page

    Returns:
        Dictionary containing 'image_url', 'date', and 'author' keys,
        or None if extraction fails
    """
    try:
        # Extract image URL from the MainComic div
        comic_div = soup.find('div', class_='MainComic__ComicImage-sc-ndbx87-2')
        if not comic_div:
            # Try alternative class name (may change over time)
            comic_div = soup.find('div', class_=lambda x: x and 'MainComic__ComicImage' in x)

        if not comic_div:
            print("Error: Could not find comic div")
            return None

        comic_img = comic_div.find("img")
        if not comic_img or 'src' not in comic_img.attrs:
            print("Error: Could not find comic image")
            return None

        image_url = comic_img["src"]

        # Extract date and author from the Author container
        author_container = soup.find('div', class_='Author__Container-sc-1w0z97f-0')
        date = "unknown"
        author = "unknown"

        if author_container:
            author_right = author_container.find('div', class_='Author__Right-sc-1w0z97f-2')
            if author_right:
                paragraphs = author_right.find_all('p')
                if len(paragraphs) > 0:
                    date = paragraphs[0].get_text().strip()
                if len(paragraphs) > 1:
                    author = paragraphs[1].get_text().strip().replace('by ', '')

        return {
            'image_url': image_url,
            'date': date,
            'author': author
        }
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error extracting comic data: {e}")
        return None


def download_image(image_url: str) -> Optional[bytes]:
    """
    Download image data from a URL.

    Args:
        image_url: The URL of the image to download

    Returns:
        Image data as bytes if successful, None if download fails
    """
    # Add https: prefix if not present
    if image_url.startswith("//"):
        image_url = "https:" + image_url

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error downloading image from {image_url}: {e}")
        return None


def save_image(image_data: bytes, filepath: str) -> bool:
    """
    Save image data to a file.

    Args:
        image_data: The image data as bytes
        filepath: The path where the image should be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'wb') as handler:
            handler.write(image_data)
        return True
    except IOError as e:
        print(f"Error saving image to {filepath}: {e}")
        return False


def get_file_extension(url: str) -> str:
    """
    Extract file extension from a URL.

    Args:
        url: The URL to extract extension from

    Returns:
        File extension (e.g., 'png', 'jpg')
    """
    return url.split('.')[-1]



def get_current_comic() -> bool:
    """
    Download the current latest Explosm comic.

    This function fetches the Explosm homepage to get the latest comic,
    then downloads the image and saves metadata to the current working directory.

    Returns:
        True if successful, False otherwise
    """
    # Fetch the main Explosm page
    soup = fetch_webpage(EXPLOSM_BASE_URL)
    if soup is None:
        return False

    # Extract comic data
    comic_data = extract_comic_data(soup)
    if comic_data is None:
        return False

    # Create filename from date and author
    date_str = comic_data['date'].replace('.', '-')
    author_str = sanitize_filename(comic_data['author'])
    base_filename = f"{date_str}_{author_str}"

    # Download the image
    image_data = download_image(comic_data['image_url'])
    if image_data is None:
        return False

    # Save the image
    file_extension = get_file_extension(comic_data['image_url'])
    image_path = f"{base_filename}.{file_extension}"
    if not save_image(image_data, image_path):
        return False

    # Save metadata
    metadata_path = f"{base_filename}_metadata.txt"
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"Date: {comic_data['date']}\n")
            f.write(f"Author: {comic_data['author']}\n")
            f.write(f"Image URL: {comic_data['image_url']}\n")
    except IOError as e:
        print(f"Error saving metadata to {metadata_path}: {e}")
        return False

    print(f"Successfully downloaded current comic: {comic_data['date']} by {comic_data['author']}")
    return True


def setup_daily_directory() -> str:
    """
    Create and return the path to today's data directory.

    Creates a directory structure: data/YYYY-MM-DD/ relative to the project root.

    Returns:
        The absolute path to the created directory
    """
    # Get current date
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Construct path to data directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data', date)

    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    return data_dir


def main():
    """
    Main function to run the daily comic scraper.

    Sets up the daily directory and downloads the current Explosm comic.
    """
    # Create and change to today's data directory
    data_dir = setup_daily_directory()
    os.chdir(data_dir)

    print(f"Saving comic to: {data_dir}")

    # Download the current comic
    success = get_current_comic()

    if success:
        print("Comic download completed successfully!")
    else:
        print("Failed to download comic.")


if __name__ == "__main__":
    main()

