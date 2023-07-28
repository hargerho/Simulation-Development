import numpy as np
from collections import deque

from common.config import simulation_params
from Road import Road

class Simulation:
    """Class to manage the simulation

    Args:
        ts: Time step to use when running the simulation
    """
    def __init__(self):
        self.ts = simulation_params['ts']
        self.road = Road()

        self.simulation_record = []
        self.display_vehicles = []

    # def timestep(self):
    #     """Single timestep frame
    #     """

    #     if not self.terminate_flag and not self.pause_flag:
    #         self.road.update_road(ts=self.ts)

    #     return self.road.vehicle_list

    def run(self, is_paused, is_recording):
        while not is_paused:
            self.road.update_road(ts=self.ts)
            self.display_vehicles.append([vehicle.vehicle_id() for vehicle in self.timestep()])
            if is_recording:
                # records simulation
                self.record_simulation.append([vehicle.vehicle_id() for vehicle in self.timestep()]) # List of dict_id

        return self.display_vehicles, self.simulation_record

