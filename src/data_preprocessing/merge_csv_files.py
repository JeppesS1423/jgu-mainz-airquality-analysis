import os
import pandas as pd
from tqdm import tqdm

def merge_csv_files(input_directory, output_file):
    # Create a list to store all CSV file paths
    csv_files = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        print(f"No CSV files found in {input_directory} or its subdirectories")
        return

    # Create an empty list to store individual dataframes
    dfs = []
    
    # Read each CSV file and append to the list
    for file in tqdm(csv_files, desc="Processing files"):
        try:
            df = pd.read_csv(file, sep=';')  # Use semicolon as separator
            
            # Ensure the timestamp column is parsed as datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            dfs.append(df)
        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue
    
    if not dfs:
        print("No valid data frames to merge. Check your CSV files and column names.")
        return

    # Concatenate all dataframes in the list
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Sort the combined dataframe by timestamp
    combined_df.sort_values('timestamp', inplace=True)
    
    # Write the combined dataframe to a new CSV file
    combined_df.to_csv(output_file, index=False, sep=';')  # Use semicolon as separator
    print(f"Merged data saved to {output_file}")

# Usage
input_directory = input("Path to the folder containing the data: ")
output_file = "merged_sensor_data.csv"
merge_csv_files(input_directory, output_file)