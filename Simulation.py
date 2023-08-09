import json
import os

from Road import Road
from common.config import simulation_params

class SimulationManager:
    def __init__(self):
        self.road = Road() # Create Road class
        self.display_vehicles = {}
        self.record_dict = {} # Dict of vehicle_list, key = iteration, value = vehicle_list

    def converting_objects(self, vehicle_list):
        return [vehicle.vehicle_id() for vehicle in vehicle_list]

    def update_frame(self, is_recording, frame):

        # print("Frame Count: ", frame)
        vehicle_list, run_flag = self.road.update_road() # List of vehicle objects

        if is_recording:
            self.record_dict[frame] = self.converting_objects(vehicle_list=vehicle_list)

        return vehicle_list, run_flag

    # TODO
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

