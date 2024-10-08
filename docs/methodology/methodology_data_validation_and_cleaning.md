# Methodology: Data Validation and Cleaning

## Overview

This document outlines the methodology used for validating and cleaning air quality data collected from sensor.community for our research project at Johannes Gutenberg University, Mainz. The process involved thorough data examination, handling of missing values, and data type optimization.

## Data Source

The data used in this project was collected from [sensor.community](https://sensor.community/), a global sensor network for citizen science environmental monitoring. The dataset comprises readings from 10 different sensors located in Mainz and surrounding areas, with varying periods of activity ranging from 2 to 6 years.

## Data Validation Process

### Initial Data Examination

1. **Data Loading**:
   - Each sensor's data was loaded into separate pandas DataFrames.
   - A list of all DataFrames was created for easier iteration and analysis.

2. **Column Identification**:
   - We identified all columns present in the datasets: sensor_id, sensor_type, location, lat, lon, timestamp, P1, durP1, ratioP1, P2, durP2, ratioP2.

### Missing Value Analysis

1. **Null Value Check**:
   - We performed a systematic check for null values in each column across all sensor DataFrames.
   - This was done using a custom function `check_missing_data()` that iterated through all DataFrames.

2. **Findings**:
   - Columns durP1, ratioP1, durP2, and ratioP2 contained no data for any sensor.
   - P1 and P2 columns had a few missing values across different sensors.
   - All other columns (sensor_id, sensor_type, location, lat, lon, timestamp) had no missing values.

### Data Type Validation

1. **Data Type Examination**:
   - We used the `info()` method to examine the data types of each column.

2. **Findings and Decisions**:
   - sensor_id and location: Currently int64, could be reduced to int32.
   - lat, lon, P1, P2: Currently float64, could be reduced to float32.
   - timestamp: Stored as object, needed conversion to datetime.

## Data Cleaning Process

Based on our validation findings, we implemented the following cleaning steps:

1. **Removal of Unnecessary Columns**:
   - Columns durP1, ratioP1, durP2, and ratioP2 were removed due to lack of data.

2. **Handling Missing Values**:
   - For P1 and P2 columns, we implemented a forward fill method within groups defined by sensor_id.
   - This approach ensures that missing values are filled with the most recent valid measurement from the same sensor.

3. **Data Type Optimization**:
   - sensor_id and location were converted to int32.
   - lat, lon, P1, and P2 were converted to float32.
   - timestamp was converted to datetime format.

4. **Standardization Across Sensors**:
   - The same cleaning process was applied to all sensor DataFrames to ensure consistency.

## Implementation

The data cleaning process was implemented through a custom Python function `clean_sensor_data()`. This function performs the following operations:

1. Removes unnecessary columns.
2. Handles missing values in P1 and P2 using grouped forward fill.
3. Converts data types as specified.
4. Converts timestamp to datetime format.

The function was applied to all sensor DataFrames, and the results were verified to ensure successful cleaning.

## Challenges and Solutions

1. **Ineffective Initial Missing Value Handling**:
   - Challenge: Initial attempt to fill missing values did not account for sensor-specific data.
   - Solution: Implemented grouped forward fill based on sensor_id.

2. **Large Dataset Handling**:
   - Challenge: Working with multiple large DataFrames could potentially lead to memory issues.
   - Solution: Processed each DataFrame individually before merging, and optimized data types to reduce memory usage.

3. **Timestamp Conversion**:
   - Challenge: Ensuring consistent datetime format across all sensors.
   - Solution: Standardized timestamp conversion within the cleaning function.

## Conclusion

Our data validation and cleaning methodology ensured the integrity and consistency of the air quality data across all sensors. By systematically addressing missing values, optimizing data types, and standardizing the data structure, we have prepared a robust dataset for subsequent analysis. This process has set a strong foundation for our research into air quality patterns in Mainz and surrounding areas.

---

Last Updated: 2024-10-08

Note: This methodology document is subject to updates as we continue to refine our data processing techniques.