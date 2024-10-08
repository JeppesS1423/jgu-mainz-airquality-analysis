# JGU Mainz Air Quality Analysis

## Project Overview
This project is part of an internship at Johannes Gutenberg University (JGU) in Mainz, Germany. It focuses on collecting and analyzing air quality data from sensor.community for cardiovascular disease research under the CuraTime team.

## Objectives
- Collect air quality data from sensor.community devices in Mainz
- Perform data analysis using traditional statistical methods
- Implement AI-based analysis techniques
- Contribute to atherombosis research for the CuraTime project

## Data Source
The primary data source for this project is [sensor.community](https://sensor.community/), a global sensor network for citizen science environmental monitoring.

## Data Download
Due to the large size of our dataset, I am hosting the main data file on Google Drive. Follow these steps to download the data:

1. Ensure you have Python installed on your system.

2. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

3. Run the `download_final_dataframe.py` script in the root directory of this project:
   ```
   python download_final_dataframe.py
   ```

   This script will:
   - Create a `data/final_dataframe` directory if it doesn't exist
   - Download the large CSV file from Google Drive
   - Save it as `final_sensor_data.csv` in the `data/final_dataframe` directory

4. The download may take some time depending on your internet connection. Please be patient.

Note: If you encounter any issues with the download, ensure that you have the necessary permissions to access the file on Google Drive.

## Technologies Used
- Python for data collection and analysis
- Pandas, Jupyter

## Project Structure
```
project-root/
│
├── data/                  # Raw and processed data files
│   └── final_dataframe/   # Directory for the downloaded large CSV file
├── notebooks/             # Jupyter notebooks for analysis
├── docs/                  # Documentation files
└── src/                   # Python source files and scripts
```

## Contributing
This project is part of an internship and research initiative. For questions about the research or findings, please reach out to me.

## Acknowledgments
- Johannes Gutenberg University, Mainz
- CuraTime Research Team
- sensor.community and its contributors

## Contact
Jesper H - jesperh0914@proton.me
Project Link: https://github.com/JeppesS1423/jgu-mainz-airquality-analysis