import numpy as np
import random

from common.config import road_params, driving_params, vehicle_models
from Vehicle import Vehicle

class Road:
    """Keep track, spawn and despawn vehicles on the road
    """

    def __init__(self):
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']

        # Spawn frequency
        self.vehicle_frequency = road_params['vehicle_inflow'] / 3600 # per/hour -> per second
        self.spawn_interval = round(1.0/self.vehicle_frequency, 1) # Round to 1dp since ts is 1dp

        # Initial spawn timer
        self.spawn_timer = self.spawn_interval

        # Getting y-coord of lanes
        self.toplane = self.toplane_loc[1]
        self.bottomlane = self.toplane + self.lanewidth * (self.num_lanes-1)

        self.vehicle_list: list[Vehicle] = []
        self.spawn_counter = 0

    def spawn_vehicle(self):
        """Spawns a car when internval is met with additional checks
        """
        # Choosing a spawn lane
        lane = int(np.random.choice(range(self.num_lanes)) * self.lanewidth)

        # Choosing spawned vehicle type
        random_vehicle = random.random()
        acc_spawnrate = vehicle_models[1].get("acc_spawnrate")

        if random_vehicle <= acc_spawnrate:
            # Spawn ACC, get acc_params from config
            logic_level = driving_params["acc_logic"]
            logic_dict = vehicle_models[1][logic_level]
            vehicle_type = 'acc'
        else:
            # Spawn SHC, get shc_params from config
            logic_level = driving_params["shc_logic"]
            logic_dict = vehicle_models[0][logic_level]
            vehicle_type = 'shc'

        # Spawn location
        spawn_loc = [self.toplane_loc[0], self.toplane_loc[1] + lane]

        # Creating the vehicle
        tmp_vehicle = Vehicle(logic_dict=logic_dict, road=self, spawn_loc=spawn_loc, vehicle_type=vehicle_type)

        # Check vehicle surroundings
        tmp_front = tmp_vehicle.get_fov()['front']

        # If there is a vehicle infront
        if tmp_front is not None:
            if tmp_vehicle.v != 0:
                headway = (tmp_front.loc_back - tmp_vehicle.loc_front) / tmp_vehicle.v
            else:
                headway = tmp_vehicle.T
            overlap_flag = (tmp_front.loc_back - tmp_vehicle.loc_front) <= 0
        else:
            # If no vehicles infront
            headway = tmp_vehicle.T
            overlap_flag = False

        # Spawn check
        if (self.spawn_timer >= self.spawn_interval
            and headway >= tmp_vehicle.T
            and not overlap_flag):
            # Spawn vehicle
            self.vehicle_list.append(tmp_vehicle)
            # Reset spawn timer
            self.spawn_timer = 0

    def update_road(self, ts):
        # Update vehicle local state
        for vehicle in self.vehicle_list:
            vehicle.update_local(ts)

        for vehicle in self.vehicle_list:
            vehicle.update_global()

            # If vehicle reached the end of the road
            # Remove vehicle from road
            if vehicle.loc_back > self.road_length:
                self.vehicle_list.remove(vehicle)

        # Update spawn_timer
        self.spawn_timer += ts
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_vehicle()
        # print("Updating Spawn Timer: ", self.spawn_timer)

