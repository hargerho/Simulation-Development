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

def interval_plots(flow_df):
    folderpath1 = 'data/new_data/plots/interval_plots'
    # Saving timestep plots
    num_plots = flow_df['section'].max()
    # Create a figure with subplots
    fig, axes = plt.subplots(nrows=num_plots, figsize=(40, 10*num_plots))

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
    plot_name = filename.replace(".json", "").replace("data/new_data","")
    plt.savefig(f'{folderpath1}/{plot_name}.png', dpi=300)
    print("Saved timesteps")

def fundamental_plots(flow_df):
    folderpath2 = 'data/new_data/plots/fundamental_plots'
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
    plot_name2 = filename.replace(".json", "").replace("data/new_data","")
    plt.savefig(f'{folderpath2}/{plot_name2}_plots.png', dpi=300)  # Change filename and format as needed
    print("Saved fundamental")

def metrics_plots(flow_df):
    folderpath3 = 'data/new_data/plots/metrics_plots'
    # Find the indices of the maximum values for space_mean_speed and num_vehicles
    maxv_idx = flow_df['space_mean_speed'].idxmax()
    maxd_idx = flow_df['num_vehicles'].idxmax()
    maxq_idx = flow_df['traffic_flow'].idxmax()

    max_v = flow_df.loc[maxv_idx, 'space_mean_speed']
    max_d = flow_df.loc[maxd_idx, 'num_vehicles']
    max_q = flow_df.loc[maxq_idx, 'traffic_flow']

    corr_vd = flow_df.loc[maxv_idx, 'num_vehicles']
    corr_dv = flow_df.loc[maxd_idx, 'space_mean_speed']
    corr_qv = flow_df.loc[maxq_idx, 'space_mean_speed']
    corr_vq = flow_df.loc[maxv_idx, 'traffic_flow']
    corr_dq = flow_df.loc[maxd_idx, 'traffic_flow']
    corr_qd = flow_df.loc[maxq_idx, 'num_vehicles']

    flow_df['combi_vd'] = flow_df['space_mean_speed'] + flow_df['num_vehicles']
    flow_df['combi_vq'] = flow_df['space_mean_speed'] + flow_df['traffic_flow']
    flow_df['combi_qd'] = flow_df['traffic_flow'] + flow_df['num_vehicles']

    combi_vd_idx = flow_df[flow_df['combi_vd'] == flow_df['combi_vd'].max()].index
    combi_vq_idx = flow_df[flow_df['combi_vq'] == flow_df['combi_vq'].max()].index
    combi_qd_idx = flow_df[flow_df['combi_qd'] == flow_df['combi_qd'].max()].index

    combi_vd = flow_df.loc[combi_vd_idx, ['space_mean_speed', 'num_vehicles']]
    combi_vq = flow_df.loc[combi_vq_idx, ['space_mean_speed', 'traffic_flow']]
    combi_qd = flow_df.loc[combi_qd_idx, ['traffic_flow', 'num_vehicles']]

    combi_v = flow_df['space_mean_speed'][combi_vd_idx]
    combi_d = flow_df['num_vehicles'][combi_vd_idx]
    combi_v = flow_df['space_mean_speed'][combi_vq_idx]
    combi_q = flow_df['traffic_flow'][combi_vq_idx]
    combi_d = flow_df['num_vehicles'][combi_qd_idx]
    combi_q = flow_df['traffic_flow'][combi_qd_idx]

    # Create figure and axis objects
    fig, axs = plt.subplots(3, 1, figsize=(12, 24))

    # Create the plot Speed vs Density
    axs[0].scatter(flow_df['num_vehicles'], flow_df['space_mean_speed'], s=0.01)
    axs[0].scatter(corr_vd, max_v, color='red', label=f'Max Speed: {max_v:.2f}')
    axs[0].scatter(max_d, corr_dv, color='blue', label=f'Max Density: {max_d}')
    axs[0].scatter(combi_d, combi_v, color='green', label=f'Max (v&d) combination')
    for index, row in combi_vd.iterrows():
        axs[0].annotate(f'Density={int(row["num_vehicles"])}\nSpeed={row["space_mean_speed"]:.2f}', (row["num_vehicles"], row["space_mean_speed"]), textcoords="offset points", xytext=(0, 10), ha='center')
    axs[0].set_xlabel('Traffic Density (veh/km)')
    axs[0].set_ylabel('Traffic Speed (km/h)')
    axs[0].set_title('Traffic Speed vs. Traffic Density')
    axs[0].legend()

    # Create the plot Speed vs Flow
    axs[1].scatter(flow_df['traffic_flow'], flow_df['space_mean_speed'], s=0.01)
    axs[1].scatter(corr_vq, max_v, color='red', label=f'Max Speed: {max_v:.2f}')
    axs[1].scatter(max_q, corr_qv, color='blue', label=f'Max Flow: {max_q:.2f}')
    axs[1].scatter(combi_q, combi_v, color='green', label=f'Max (v&q) combination')
    for index, row in combi_vq.iterrows():
        axs[1].annotate(f'Flow={row["traffic_flow"]:.2f}\nSpeed={row["space_mean_speed"]:.2f}', (row["traffic_flow"], row["space_mean_speed"]), textcoords="offset points", xytext=(0, 10), ha='center')
    axs[1].set_xlabel('Traffic Flow (veh/h)')
    axs[1].set_ylabel('Traffic Speed (km/h)')
    axs[1].set_title('Traffic Speed vs. Traffic Flow')
    axs[1].legend()


    # Create the plot Flow vs Density
    axs[2].scatter(flow_df['num_vehicles'], flow_df['traffic_flow'], s=0.01)
    axs[2].scatter(corr_qd, max_q, color='red', label=f'Max Flow: {max_q:.2f}')
    axs[2].scatter(max_d, corr_dq, color='blue', label=f'Max Density: {max_d}')
    axs[2].scatter(combi_d, combi_q, color='green', label=f'Max (v&d) combination')
    for index, row in combi_qd.iterrows():
        axs[2].annotate(f'Density={int(row["num_vehicles"])}\nFlow={row["traffic_flow"]:.2f}', (row["num_vehicles"], row["traffic_flow"]), textcoords="offset points", xytext=(0, 10), ha='center')
    axs[2].set_xlabel('Traffic Density (veh/h)')
    axs[2].set_ylabel('Traffic Flow (km/h)')
    axs[2].set_title('Traffic Flow vs. Traffic Density')
    axs[2].legend(loc='upper right')

    # Adjust layout and display plots
    plt.tight_layout()
    # Save the figure as a single image
    plot_name3 = filename.replace(".json", "").replace("data/new_data","")
    plt.savefig(f'{folderpath3}/{plot_name3}_points.png', dpi=300)

folderpath = "data/new_data/"

road_length = road_params['road_length']

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

        interval_plots(flow_df)

        fundamental_plots(flow_df)

        metrics_plots(flow_df)