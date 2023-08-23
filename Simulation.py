import json
import os
import math
from statistics import harmonic_mean

from Vehicle import Vehicle
from Road import Road
from common.config import simulation_params

class SimulationManager:
    def __init__(self):
        self.road = Road() # Create Road class
        self.display_vehicles = {}
        self.record_dict = {} # Dict of vehicle_list, key = iteration, value = vehicle_list

        self.realtime_flow = [0,0,0,0]
        self.metric_list = [(40,325), (280,390), (16000,390), (31900, 390)]


    def speed_conversion(self, value):
        # 1m = 10px
        # Converts pixel/seconds -> pixel/h
        return float(value * (3600/2000))

    def density_conversion(self, value, dist):
        # Interval of 400 px
        # 1m = 10px
        return float(value * (2000/dist))

    def assign_section(self, loc, speed, vehicle_metrics):
        for idx, metric_loc in enumerate(self.metric_list):
            if idx == 0: # if vehicle is at the first checkpoint
                if loc[0] >= metric_loc[0] and loc[0] <= metric_loc[0] + 100:
                    vehicle_metrics[idx].append((speed, 667))
            elif loc[0] >= metric_loc[0] - 100 and loc[0] <= metric_loc[0] + 100:
                vehicle_metrics[idx].append((speed, 1000))

    def compute_metrics(self, vehicle_metric, realtime_metrics):

        for idx, sections in enumerate(vehicle_metric):
            num_vehicles = len(sections)
            if num_vehicles > 0:
                space_mean_speed = harmonic_mean([speed[0] for speed in sections])
                density = self.density_conversion(num_vehicles,sections[0][1])
                speed = self.speed_conversion(space_mean_speed)
                flow = int(density * speed)
                realtime_metrics[idx] = (flow, density, speed)

        return realtime_metrics

    def converting_objects(self, vehicle_list):
        vehicle_metrics = [[], [], [], []] # 1st, 2nd, middle, last
        for vehicle in vehicle_list:
            if isinstance(vehicle, Vehicle):
                vehicle_id = vehicle.vehicle_id()
                self.assign_section(loc=vehicle_id['location'], speed=vehicle_id['speed'], vehicle_metrics=vehicle_metrics)
                # vehicle_stats.append(vehicle.vehicle_id())
            else:
                for convoy in vehicle.convoy_list:
                    vehicle_id=convoy.vehicle_id()
                    self.assign_section(loc=vehicle_id['location'], speed=vehicle_id['speed'], vehicle_metrics=vehicle_metrics)
                    # vehicle_stats.append(convoy.vehicle_id())
        self.realtime_flow = self.compute_metrics(vehicle_metrics, self.realtime_flow)

        return self.realtime_flow

    def update_frame(self, is_recording, frame, restart):

        vehicle_list, run_flag = self.road.update_road(restart=restart) # List of vehicle objects

        if is_recording:
            self.record_dict[frame] = self.converting_objects(vehicle_list=vehicle_list)

        if restart:
            self.record_dict = {}

        return vehicle_list, run_flag

    def saving_record(self):
        print("Saving data ...")
        filepath = os.path.join(simulation_params['folderpath'], simulation_params['filename'] + ".json")
        idx = 0

        while os.path.exists(filepath):
            filename = f"{simulation_params['filename']}_{idx}"
            filepath = os.path.join(simulation_params['folderpath'], f"{filename}.json")
            idx += 1

        with open(filepath, "w") as file:
            json.dump(self.record_dict, file, indent=4)
        print("Data Saved!")

