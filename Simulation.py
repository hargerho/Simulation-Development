import json
import os

from Road import Road
from common.config import simulation_params

class SimulationManager:
    def __init__(self):
        self.road = Road() # Create Road class
        self.display_vehicles = {}
        self.record_list = {} # Dict of vehicle_list, key = iteration, value = vehicle_list

    def update_frame(self, is_recording):

        frame = 0

        # print("Frame Count: ", frame)
        vehicle_list = self.road.update_road() # List of vehicle objects

        if is_recording:
            self.record_list[frame] = vehicle_list

        frame += 1

        return vehicle_list, self.record_list

    # TODO
    def saving_record(self):
        print("Saving data ...")
        filepath = os.path.join(simulation_params['filepath', simulation_params['filename' + ".json"]])
        idx = 0

        while os.path.exists(filepath):
            filename = f"{filename}_{idx}"
            filepath = os.path.join(simulation_params['filepath', simulation_params['filename' + ".json"]])
            idx += 1

        with open(filepath, "w") as file:
            json.dump(self.record_list, file)

