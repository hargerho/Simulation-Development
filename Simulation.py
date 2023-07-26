import numpy as np
from Road import Road
from collections import deque

class SimulationManager:
    """Class to manage the simulation

    Args:
        params_list: List of car params defining the different car types
        toplane_loc: Position of the top most lane
        road_length: Road length
        num_lanes: Amount of lanes
        lanewidth: Width of the car lanes
        ts: Time step to use when running the simulation
    """
    def __init__(self, vehicle_models, toplane_loc=(0,0), road_length = 600, num_lanes=2, lanewidth=5, vehicle_inflow=4000, ts=0.1):
        self.ts = ts
        self.road = Road(vehicle_models=vehicle_models, num_lanes=num_lanes, toplane_loc=toplane_loc,
                         lanewidth=lanewidth, road_length=road_length, vehicle_inflow=vehicle_inflow)

        # Simulation Controls
        self.record_flag = False
        self.pause_flag = False
        self.terminate_flag = False

    def frame(self):
        while not self.terminate_flag:
            self.road.update_road(ts=self.ts)
            if self.record_flag:
                # records
                pass
            if self.pause_flag:
                #pause
                pass

        return self.road.vehicle_list

