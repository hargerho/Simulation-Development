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
        initdf = pd.DataFrame(flat_data)

        df = initdf.copy()
        df = df.drop(columns=['vehicle_type', 'timestamp'])
        section_length = loc_conversion(1000)
        def assign_section(location):
            return int(location[0]//section_length)
        df['section'] = df['location'].apply(assign_section)
        df['speed'] *= (3600/2000)
        df['num_vehicles'] = df.groupby(['frame', 'section'])['uuid'].transform('count')
        df['section'] = df['location'].apply(assign_section)

        df['reciprocal_speed'] = 1 / df['speed']
        flow_df = df.drop_duplicates(subset=['frame', 'section','uuid'])
        flow_df['space_mean_speed_denom'] = flow_df.groupby(['frame', 'section'])['reciprocal_speed'].transform('sum')

        flow_df['space_mean_speed'] = flow_df['num_vehicles'] / flow_df['space_mean_speed_denom']
        flow_df['traffic_flow'] = flow_df['space_mean_speed'] * flow_df['num_vehicles']

        flow_df = flow_df.drop_duplicates(subset=['frame', 'section'])
        flow_df.dropna(subset=['traffic_flow'], inplace=True)

        # Saving timestep plots
        num_plots = flow_df['section'].max()
        # Create a figure with subplots
        fig, axes = plt.subplots(nrows=num_plots, figsize=(40, 10*num_plots))  # You can adjust figsize as needed

        for i, ax in enumerate(axes):
            # Filter data for the current section
            visual = flow_df[flow_df['section'] == i]

            # Calculate the average traffic flow
            averaged = visual['traffic_flow'].mean()

            # Plot the average line
            ax.axhline(y=averaged, color='red', linestyle='--', label=f'Average: {averaged:.3f}')

            # Plot the data
            ax.plot(visual['frame'], visual['traffic_flow'], label='Traffic Flow')

            # Set title, xlabel, and ylabel
            ax.set_title(f"Traffic Flow vs Timestep: Interval {i}")
            ax.set_xlabel("Timestep")
            ax.set_ylabel("Traffic Flow (veh/h)")

            # Add legend
            ax.legend()

        # Adjust layout and spacing
        plt.tight_layout()

        # Save the figure as a single image
        plot_name = filename.replace(".json", "")
        plt.savefig(f'{plot_name}.png', dpi=300)

        # Fundamental Diagrams
        # Calculate linear fit
        m, c = np.polyfit(flow_df['num_vehicles'], flow_df['space_mean_speed'], 1)
        y_fit = m * flow_df['num_vehicles'] + c
        flow_capacity = (c*c)/(4*abs(m)) # Greenshields Maximum Flow Rate Relationship

        # Generate data for Speed vs Flow
        density = np.arange(int(c/abs(m)))
        speed = c + density * m
        flow = density * speed

        # Generate data for Flow vs Density
        density = np.arange(int(c/abs(m)))
        kj = c/abs(m)
        kcap = kj/2
        flowden = c * (density - ((density * density) / kj))

        # Create figure and axis objects
        fig, axs = plt.subplots(3, 1, figsize=(10, 8*2))

        # Plot Speed vs Density
        axs[0].scatter(flow_df['num_vehicles'], flow_df['space_mean_speed'], s=0.01)
        axs[0].plot(flow_df['num_vehicles'], y_fit, 'black', linestyle='dotted', label=f'Bestfit = {m:.3g}k + {c:.3g}')
        axs[0].set_ylim(bottom=0)
        axs[0].set_xlabel('Traffic Density (veh/km)')
        axs[0].set_ylabel('Traffic Speed (km/h)')
        axs[0].set_title('Traffic Speed vs. Traffic Density')
        axs[0].legend()



        # Plot Speed vs Flow
        axs[1].plot(flow, speed, label='Model')
        axs[1].scatter(flow_df['traffic_flow'], flow_df['space_mean_speed'], s=0.01)
        axs[1].axvline(x=flow_capacity, color='yellow', label=f'Flow Capacity: {flow_capacity:.3f}', linestyle='dotted')
        axs[1].axhline(y=c/2, color='black', label=f'Speed Capacity: {c/2:.3f}', linestyle='dotted')
        axs[1].set_xlabel('Traffic Flow (veh/h)')
        axs[1].set_ylabel('Traffic Speed (km/h)')
        axs[1].set_title('Traffic Speed vs. Traffic Flow')
        axs[1].legend()



        # Plot Flow vs Density
        axs[2].plot(density, flowden, label='Model')
        axs[2].scatter(flow_df['num_vehicles'], flow_df['traffic_flow'], s=0.01)
        axs[2].axhline(y=flow_capacity, color='yellow', label=f'Flow Capacity: {flow_capacity:.3f}', linestyle='dotted')
        axs[2].axvline(x=kcap, color='r', label=f'Density Capacity: {kcap:.3f}', linestyle='dotted')
        axs[2].set_xlabel('Traffic Density (veh/h)')
        axs[2].set_ylabel('Traffic Flow (km/h)')
        axs[2].set_title('Traffic Flow vs. Traffic Density')
        axs[2].legend(loc='upper right')

        # Adjust layout and display plots
        plt.tight_layout()
        # Save the figure as a single image
        plt.savefig(f'_{plot_name}.png', dpi=300)  # Change filename and format as needed