import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from common.config import road_params

# 1m : 2px
def loc_conversion(value):
    return value*2

folderpath = "data/1000_vehicles/"

road_length = road_params['road_length']

testList = [[0, loc_conversion(1000)], [loc_conversion(1000), loc_conversion(1000)+loc_conversion(2000)],[(int(road_length/2) - loc_conversion(500)), (int(road_length/2) + loc_conversion(500))], [(road_length-loc_conversion(1000)), road_length], [0, road_length]]
nameList = [[0, 1], [1, 2], ['Roadblock-500m', '+500'], [15, 16], [0, 16]]

for index, item in tqdm(enumerate(testList), total=len(testList), desc="Processing"):
    section_start = item[0]
    section_end = item[1]
    start_name = nameList[index][0]
    end_name = nameList[index][1]
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

            # Filter rows based on x-coordinate range
            filtered_df = df[df['location'].apply(lambda loc: section_start <= loc[0] <= section_end)]

            # Converting pixel/second -> kmph
            filtered_df.loc[:,'speed']= filtered_df['speed'] * (3600/2000) # Converts back to kmph

            # Remove unnecessary columns
            dropped_df = filtered_df.drop(['vehicle_type', 'location', 'timestamp'], axis=1)

            # Counting Vehicle Density = vehicles/km per frame
            dropped_df['num_vehicles'] = dropped_df.groupby('frame')['uuid'].transform('nunique')
            dropped_df = dropped_df.drop(['uuid'], axis=1)

            # Counting Space mean speed per frame
            dropped_df['average_speed'] = dropped_df.groupby('frame')['speed'].transform('mean')
            result_df = dropped_df.drop_duplicates(subset=['frame'])
            sorted_df = result_df.sort_values('frame')

            # Compute vehicle flow per km per frame
            sorted_df['flow'] = sorted_df['num_vehicles'].multiply(sorted_df['average_speed'])

            # Compute traffic flow moving average across 10 frame intervals
            moving_average_flow_df = sorted_df['flow'].rolling(window=10).mean()
            cleaned_df = moving_average_flow_df.dropna(axis=0)
            moving_average_list = cleaned_df.tolist()

            num_vehicles = sorted_df['num_vehicles'].values.tolist()
            flow = sorted_df['flow'].values.tolist()

            # Plotting Data
            plt.figure(figsize=(12,8))

            # Plotting Vehicle Flow vs Vehicle Density
            plt.subplot(3,1,1)
            plt.scatter(num_vehicles, flow, 0.1)
            plt.xlabel('Vehicle Density (Vehicle/km)')
            plt.ylabel('Vehicle Flow (Vehicle/Hour)')
            plt.title(f"Vehicle Flow vs Vehicle Density from {start_name}-{end_name}km")

            # Plotting Vehicle Flow vs Timestep
            plt.subplot(3,1,2)
            plt.scatter(range(len(flow)), flow, 0.1)
            plt.xlabel('Timestep')
            plt.ylabel('Vehicle Flow (Vehicle/Hour)')
            plt.title(f"Vehicle Flow vs Timestep from {start_name}-{end_name}km")

            # Plotting Vehicle Flow Moving Average vs Timestep
            plt.subplot(3,1,3)
            plt.scatter(range(len(moving_average_list)), moving_average_list, 0.1)  # Adding markers for each data point
            plt.xlabel('Timestep')
            plt.ylabel('Flow Moving Average')
            plt.title(f"Plot of Vehicle Flow Moving Average from {start_name}-{end_name}km")

            plt.tight_layout()
            name = f"{filename}{start_name}-{end_name}km.png"
            save_name = name.replace("data/", "").replace(".json", "").replace("1000_vehicles/", "100_vehicles_")
            plt.savefig(save_name)

folderpath2 = "data/ranged/"

for index, item in tqdm(enumerate(testList), total=len(testList), desc="Processing"):
    section_start = item[0]
    section_end = item[1]
    start_name = nameList[index][0]
    end_name = nameList[index][1]
    # Iterate through the files in the folder
    for filename in tqdm(os.listdir(folderpath2), desc="Files"):
        if filename.endswith('.json'):
            json_path = os.path.join(folderpath2, filename)

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

            # Filter rows based on x-coordinate range
            filtered_df = df[df['location'].apply(lambda loc: section_start <= loc[0] <= section_end)]

            # Converting pixel/second -> kmph
            filtered_df.loc[:,'speed']= filtered_df['speed'] * (3600/2000) # Converts back to kmph

            # Remove unnecessary columns
            dropped_df = filtered_df.drop(['vehicle_type', 'location', 'timestamp'], axis=1)

            # Counting Vehicle Density = vehicles/km per frame
            dropped_df['num_vehicles'] = dropped_df.groupby('frame')['uuid'].transform('nunique')
            dropped_df = dropped_df.drop(['uuid'], axis=1)

            # Counting Space mean speed per frame
            dropped_df['average_speed'] = dropped_df.groupby('frame')['speed'].transform('mean')
            result_df = dropped_df.drop_duplicates(subset=['frame'])
            sorted_df = result_df.sort_values('frame')

            # Compute vehicle flow per km per frame
            sorted_df['flow'] = sorted_df['num_vehicles'].multiply(sorted_df['average_speed'])

            # Compute traffic flow moving average across 10 frame intervals
            moving_average_flow_df = sorted_df['flow'].rolling(window=10).mean()
            cleaned_df = moving_average_flow_df.dropna(axis=0)
            moving_average_list = cleaned_df.tolist()

            num_vehicles = sorted_df['num_vehicles'].values.tolist()
            flow = sorted_df['flow'].values.tolist()

            # Plotting Data
            plt.figure(figsize=(12,8))

            # Plotting Vehicle Flow vs Vehicle Density
            plt.subplot(3,1,1)
            plt.scatter(num_vehicles, flow, 0.1)
            plt.xlabel('Vehicle Density (Vehicle/km)')
            plt.ylabel('Vehicle Flow (Vehicle/Hour)')
            plt.title(f"Vehicle Flow vs Vehicle Density from {start_name}-{end_name}km")

            # Plotting Vehicle Flow vs Timestep
            plt.subplot(3,1,2)
            plt.scatter(range(len(flow)), flow, 0.1)
            plt.xlabel('Timestep')
            plt.ylabel('Vehicle Flow (Vehicle/Hour)')
            plt.title(f"Vehicle Flow vs Timestep from {start_name}-{end_name}km")

            # Plotting Vehicle Flow Moving Average vs Timestep
            plt.subplot(3,1,3)
            plt.scatter(range(len(moving_average_list)), moving_average_list, 0.1)  # Adding markers for each data point
            plt.xlabel('Timestep')
            plt.ylabel('Flow Moving Average')
            plt.title(f"Plot of Vehicle Flow Moving Average from {start_name}-{end_name}km")

            plt.tight_layout()
            name = f"{filename}{start_name}-{end_name}km.png"
            save_name = name.replace("data/ranged/", "").replace(".json", "")
            plt.savefig(save_name)