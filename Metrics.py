import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from common.config import road_params

pd.options.mode.chained_assignment = None  # default='warn'

# 1m : 2px
def loc_conversion(value):
    return value*2

folderpath = "data/1000_vehicles/"

road_length = road_params['road_length']

testDict = {
    '0-1km': (0, loc_conversion(1000)),
    '1-2km': (loc_conversion(1000), loc_conversion(1000)+loc_conversion(2000)),
    'Roadblock:+-500m': ((int(road_length/2) - loc_conversion(500)), (int(road_length/2) + loc_conversion(500))),
    '15-16km': ((road_length-loc_conversion(1000)), road_length),
}

# Iterate through the files in the folder
for filename in tqdm(os.listdir(folderpath), desc="Files"):
    if filename.endswith('.json'):
        json_path = os.path.join(folderpath, filename)

        # Read JSON file
        with open(json_path, 'r') as json_file:
            json_data = json.load(json_file)

        # Convert data to a flat list of dictionaries
        flat_data = []
        for frame_key, frame_data in json_data.items():
            for vehicle in frame_data:
                flat_data.append({
                    'frame': int(frame_key),
                    'uuid': vehicle['uuid'],
                    'vehicle_type': vehicle['vehicle_type'],
                    'location': vehicle['location'],
                    'speed': vehicle['speed'],
                    'timestamp': vehicle['timestamp']
                })
        # Create a DataFrame from the flat data
        df = pd.DataFrame(flat_data)

        # Create a list to store interval-specific DataFrames
        interval_dfs = []

        # Filter rows and create interval-specific DataFrames
        for label, (start, end) in testDict.items():
            interval_rows = df[df['location'].apply(lambda x: start <= x[0] <= end)]
            interval_rows['Interval'] = label  # Add a new column for interval label
            interval_dfs.append(interval_rows)

        # Combine interval-specific DataFrames into a single DataFrame
        combined_df = pd.concat(interval_dfs, ignore_index=True)

        # Convert speed from pixel/second -> kmph
        combined_df['speed'] *= (3600 / 2000)

        # Group by interval and frame, and calculate necessary statistics
        grouped_df = combined_df.groupby(['Interval', 'frame']).agg({
            'speed': 'mean',
            'uuid': 'nunique'
        }).reset_index()

        # Rename columns for clarity
        grouped_df.rename(columns={'speed': 'average_speed', 'uuid': 'num_vehicles'}, inplace=True)

        # Compute flow and moving average
        grouped_df['flow'] = grouped_df['num_vehicles'] * grouped_df['average_speed']
        grouped_df['moving_average_flow'] = grouped_df.groupby('Interval')['flow'].rolling(window=10).mean().reset_index(level=0, drop=True)

        # Filter out NaN values from moving average
        grouped_df.dropna(subset=['moving_average_flow'], inplace=True)

        # Iterate over intervals and create separate plots
        for interval_label, interval_df in grouped_df.groupby('Interval'):
            plt.figure(figsize=(12, 8))

            plt.subplot(3,1,1)
            plt.scatter(interval_df['num_vehicles'], interval_df['flow'], 0.1)
            plt.xlabel('Vehicle Density')
            plt.ylabel('Vehicle Flow')
            plt.title(f'Vehicle Flow vs Vehicle Density per Timestep ({interval_label})')

            plt.subplot(3,1,2)
            plt.scatter(interval_df['frame'], interval_df['flow'], 0.1)
            plt.xlabel('Timestep')
            plt.ylabel('Vehicle Flow')
            plt.title(f'Vehicle Flow vs Timestep ({interval_label})')

            plt.subplot(3,1,3)
            plt.scatter(interval_df['frame'], interval_df['moving_average_flow'], 0.1)
            plt.xlabel('Timestep')
            plt.ylabel('Flow Moving Average')
            plt.title(f'Vehicle Flow Moving Average ({interval_label})')

            plt.tight_layout()
            name = f"{filename}_{interval_label}.png"
            save_name = name.replace("data/", "").replace(".json", "").replace("1000_vehicles/", "100_vehicles_")
            plt.savefig(save_name)