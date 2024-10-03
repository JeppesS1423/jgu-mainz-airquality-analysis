import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import gzip
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime, timedelta
from urllib.robotparser import RobotFileParser
import backoff

# Constants for scraper behavior
MAX_RETRIES = 4
CONCURRENT_REQUESTS = 5
DELAY_BETWEEN_REQUESTS = 1  # 1 second delay between requests

async def check_robots_txt(session, base_url):
    """Check the robots.txt file of the target website."""
    parsed_url = urlparse(base_url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = RobotFileParser()
    async with session.get(robots_url) as response:
        content = await response.text()
        rp.parse(content.splitlines())
    print(f"Checked robots.txt at: {robots_url}")
    return rp

def can_fetch(rp, url):
    """Check if the URL can be fetched according to robots.txt rules."""
    return rp.can_fetch("*", url)

@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=MAX_RETRIES)
async def download_file(session, url, local_filename):
    """Download a file from the given URL and save it locally."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.read()
            os.makedirs(os.path.dirname(local_filename), exist_ok=True)
            with open(local_filename, 'wb') as f:
                f.write(content)
        print(f"Successfully downloaded: {local_filename}")
        
        # Decompress the file if it's a gzip file
        if local_filename.endswith('.gz'):
            try:
                with gzip.open(local_filename, 'rb') as f_in:
                    with open(local_filename[:-3], 'wb') as f_out:
                        f_out.write(f_in.read())
                os.remove(local_filename)
                print(f"Decompressed {local_filename}")
            except Exception as e:
                print(f"Error decompressing {local_filename}: {str(e)}")
    except aiohttp.ClientError as e:
        print(f"Error downloading {url}: {str(e)}")
        raise  # Re-raise the exception for the backoff decorator

@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=MAX_RETRIES)
async def process_date(session, rp, base_url, date, sensor_numbers, semaphore):
    """Process data for a specific date, downloading files for each sensor."""
    date_str = date.strftime("%Y-%m-%d")
    url = f"{base_url}/{date_str}/"  # Alternative URLs: 
                                     # f"{base_url}/{year}/{date_str}/"
    if not can_fetch(rp, url):
        print(f"robots.txt disallows access to {url}. Skipping.")
        return
    
    print(f"Checking URL: {url}")
    
    try:
        async with semaphore:
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)  # Add request delay
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.text()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        tasks = []
        for sensor_number in sensor_numbers:
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and re.match(f"{date_str}_.*_sensor_{sensor_number}"
                                     f"\.csv(\.gz)?$", href):
                    
                    file_url = urljoin(url, href)
                    local_filename = os.path.join("downloaded_data", 
                                                  sensor_number, href)
                    
                    tasks.append(download_file(session, 
                                               file_url, local_filename))
        
        await asyncio.gather(*tasks)
    
    except aiohttp.ClientError as e:
        print(f"Error accessing {url}: {str(e)}")
        raise  # Re-raise the exception for the backoff decorator

async def scrape_sensor_data(base_url, start_date, end_date, sensor_numbers):
    """Main function to scrape sensor data for a given date range and 
    given sensor numbers."""
    timeout = aiohttp.ClientTimeout(total=3600)  # 1 hour timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        rp = await check_robots_txt(session, base_url)
        
        # Generate a list of dates to process
        date_range = [start_date + timedelta(days=x) for x in 
                      range((end_date - start_date).days + 1)]
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        tasks = [process_date(session, rp, base_url,
                              date, sensor_numbers,
                              semaphore) for date in date_range]
        await asyncio.gather(*tasks)

# Main loop
base_url = "https://archive.sensor.community/"
start_date = datetime(2024, 1, 30)
end_date = datetime(2024, 12, 31)
sensor_numbers = ["26656", "10701", "83487", "21886", "803",
                  "77220", "66816", "23712", "48807", "47739"]

print("Starting scraper...")
asyncio.run(scrape_sensor_data(base_url, start_date,
                               end_date, sensor_numbers))
print("Scraper finished.")