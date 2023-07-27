import numpy as np
from collections import deque

from common.config import simulation_params
from Road import Road

class SimulationManager:
    """Class to manage the simulation

    Args:
        ts: Time step to use when running the simulation
    """
    def __init__(self, record_flag, pause_flag, terminate_flag):
        self.ts = simulation_params['ts']
        self.road = Road()

        # Simulation Controls
        # Default values commented
        self.record_flag = record_flag # False
        self.pause_flag = pause_flag # False
        self.terminate_flag = terminate_flag # False

        self.simulation_record = []
    def timestep(self):
        """Single timestep frame
        """

        if not self.terminate_flag and not self.pause_flag:
            self.road.update_road(ts=self.ts)

        return self.road.vehicle_list

    def run(self):
        while not self.terminate_flag:
            self.road.update_road(ts=self.ts)
            if self.record_flag:
                # records simulation
                self.record_simulation.append([vehicle.vehicle_id() for vehicle in self.timestep()]) # List of dict_id

        return self.simulation_record

