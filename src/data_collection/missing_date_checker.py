import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import csv
from datetime import datetime
import re
import gzip
import shutil

# Constants
BASE_URL = "https://archive.sensor.community"
MAX_RETRIES = 3
CONCURRENT_REQUESTS = 5
YEAR_THRESHOLD = 2023

async def download_file(session, url, local_filename):
    """
    Downloads a file from the given URL and saves it locally.
    If the file is a gzip file, it is decompressed after download.

    :param session: The aiohttp session to use for the request
    :param url: The URL of the file to download
    :param local_filename: The local path where the file should be saved
    :return: True if the download was successful, False otherwise
    """
    for _ in range(MAX_RETRIES):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    os.makedirs(os.path.dirname(local_filename), exist_ok=True)
                    with open(local_filename, 'wb') as f:
                        f.write(content)
                    print(f"Successfully downloaded: {local_filename}")
                    
                    # Decompress if it's a gzip file
                    if local_filename.endswith('.gz'):
                        try:
                            uncompressed_filename = local_filename[:-3]
                            with gzip.open(local_filename, 'rb') as f_in:
                                with open(uncompressed_filename, 'wb') as f_out:
                                    shutil.copyfileobj(f_in, f_out)
                            os.remove(local_filename)
                            print(f"Decompressed {local_filename} to {uncompressed_filename}")
                        except Exception as e:
                            print(f"Error decompressing {local_filename}: {str(e)}")
                    
                    return True
                elif response.status == 404:
                    print(f"File not found: {url}")
                    return False
        except aiohttp.ClientError as e:
            print(f"Error downloading {url}: {str(e)}")
    print(f"Failed to download {url} after {MAX_RETRIES} attempts")
    return False

async def process_date(session, sensor_id, date, semaphore):
    """
    Processes a single date for a given sensor ID.
    Attempts to download all relevant CSV files for the specified date and sensor.

    :param session: The aiohttp session to use for requests
    :param sensor_id: The ID of the sensor to process
    :param date: The date to process in 'YYYY-MM-DD' format
    :param semaphore: Semaphore to limit concurrent requests
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        year = date_obj.year
        
        if year < YEAR_THRESHOLD:
            url = f"{BASE_URL}/{year}/{date}/"
        else:
            url = f"{BASE_URL}/{date}/"
        
        print(f"Accessing URL: {url}")
        
        async with semaphore:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f"Failed to access {url}")
                        return
                    content = await response.text()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                tasks = []
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href and re.match(f"{date}_.*_sensor_{sensor_id}\.csv(\.gz)?$", href):
                        file_url = f"{url}{href}"
                        local_filename = os.path.join("downloaded_data", sensor_id, href)
                        tasks.append(download_file(session, file_url, local_filename))
                
                results = await asyncio.gather(*tasks)
                if not any(results):
                    print(f"No files found or downloaded for date: {date}")
            except aiohttp.ClientError as e:
                print(f"Error accessing {url}: {str(e)}")
    except ValueError:
        print(f"Invalid date format: {date}")

async def scrape_missing_dates(sensor_id, missing_dates_file):
    """
    Scrapes data for all missing dates for a given sensor ID.

    :param sensor_id: The ID of the sensor to process
    :param missing_dates_file: Path to the CSV file containing missing dates
    """
    timeout = aiohttp.ClientTimeout(total=7200)  # 2 hour timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        tasks = []

        with open(missing_dates_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                date = row[0]
                tasks.append(process_date(session, sensor_id, date, semaphore))
        
        await asyncio.gather(*tasks)

def main():
    """
    Main function to run the sensor data scraper.
    Prompts the user for a sensor ID and processes all missing dates for that sensor.
    """
    sensor_id = input("Enter the sensor ID: ")
    missing_dates_file = f"missing_sensor_dates/{sensor_id}_missing_dates.csv"

    if not os.path.exists(missing_dates_file):
        print(f"Error: {missing_dates_file} not found.")
        return

    print(f"Starting scraper for sensor {sensor_id}...")
    print(f"Downloading data for all missing dates...")
    print(f"Using URL structure {{year}}/{{year-month-date}} for years before {YEAR_THRESHOLD}")
    print(f"Using URL structure {{year-month-date}} for years {YEAR_THRESHOLD} and later")
    asyncio.run(scrape_missing_dates(sensor_id, missing_dates_file))
    print("Scraper finished.")

if __name__ == "__main__":
    main()