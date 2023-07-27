import numpy as np
import random

from common.config import road_params, driving_params
from Vehicle import Vehicle

class Road:
    """Keep track, spawn and despawn vehicles on the road
    """

    def __init__(self):
        self.vehicle_models = road_params['vehicle_models']
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']

        # Spawn frequency
        self.vehicle_frequency = road_params['vehicle_inflow'] / 3600 # per/hour -> per second
        self.spawn_interval = 1.0/self.vehicle_frequency

        # Initial spawn timer
        self.spawn_timer = self.spawn_interval

        self.toplane = self.toplane_loc[1]
        self.bottomlane = self.toplane_loc + self.lanewidth * (self.num_lanes-1)

        self.vehicle_list = []

    def spawn_flag(self):
        """Boolean flag to determine if a vehicle should be spawn
        """
        # Choosing a spawn lane
        lane = int(np.random.choice(range(self.num_lanes)) * self.lanewidth)

        # Choosing spawned vehicle type
        random_vehicle = random.random()
        acc_spawnrate = self.vehicle_models[1]['acc_spawnrate']
        if random_vehicle <= acc_spawnrate:
            # Spawn ACC, get acc_params from config
            logic_level = driving_params["acc_logic"]
            spawn_params = self.vehicle_models[1][logic_level]
        else:
            # Spawn SHC, get shc_params from config
            logic_level = driving_params["shc_logic"]
            spawn_params = self.vehicle_models[0][logic_level]

        spawn_loc = [self.toplane_loc[0], self.toplane_loc[1] + self.num_lanes]

        tmp_vehicle = Vehicle(vehicle_params=spawn_params, road=self, spawn_loc=spawn_loc)

        # Check surroundings
        tmp_front = tmp_vehicle.get_fov()['front']

        if tmp_front is not None:
            if tmp_vehicle.v != 0:
                headway = (tmp_front.loc_back - tmp_vehicle.loc_front) / tmp_vehicle.v
            else:
                headway = tmp_vehicle.T
            overlap_flag = (tmp_front.loc_back - tmp_vehicle.loc_front) <= 0
        else:
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
        destroy_flag = False

        # Update vehicle local state
        for vehicle in self.vehicle_list:
            vehicle.update_local(ts)

        for vehicle in self.vehicle_list:
            vehicle.update_global()

            # if vehicle reached the end of the road
            if vehicle.loc_back > self.road_length:
                self.vehicle_list.remove(vehicle)
                destroy_flag = True

        # Update spawn_timer
        self.spawn_timer += ts

        return destroy_flag


