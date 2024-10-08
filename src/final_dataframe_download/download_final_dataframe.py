import gdown
import os

def download_from_google_drive(file_id, output_path):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # URL format for Google Drive files
    url = f"https://drive.google.com/uc?id={file_id}"
    
    # Download the file
    gdown.download(url, output_path, quiet=False)

# Usage
file_id = "1hW7Q2h9wkQ6uRQO2ZDwDQpSSye7Y3eg6"  # Replace with your actual file ID
output_path = "data/final_dataframe/final_sensor_data.csv"

download_from_google_drive(file_id, output_path)