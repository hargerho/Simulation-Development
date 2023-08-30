import json
import os

from Vehicle import Vehicle
from Road import Road
from common.config import simulation_params

class SimulationManager:
    def __init__(self):
        self.road = Road() # Create Road class
        self.display_vehicles = {}
        self.record_dict = {} # Dict of vehicle_list, key = iteration, value = vehicle_list

    def converting_objects(self, vehicle_list):
        # sourcery skip: for-append-to-extend
        vehicle_stats = []
        for vehicle in vehicle_list:
            if isinstance(vehicle, Vehicle):
                vehicle_stats.append(vehicle.vehicle_id())
            else:
                for convoy in vehicle.convoy_list:
                    vehicle_stats.append(convoy.vehicle_id())
        return vehicle_stats

    def update_frame(self, is_recording, frame, restart):

        # print("Frame Count: ", frame)
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