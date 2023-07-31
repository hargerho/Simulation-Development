import numpy as np
import random
import time

from common.config import road_params, driving_params, vehicle_models, simulation_params
from Vehicle import Vehicle

class Road:
    """Keep track, spawn and despawn vehicles on the road
    """

    def __init__(self):
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']
        self.ts = simulation_params['ts']

        # Spawn frequency
        self.vehicle_frequency = road_params['vehicle_inflow'] / 3600 # per/hour -> per second
        self.spawn_interval = round(1.0/self.vehicle_frequency, 1) # Round to 1dp since ts is 1dp

        # Initial spawn timer
        self.timer = 0.0
        self.last_spawn_time = 0

        # Getting y-coord of lanes
        self.toplane = self.toplane_loc[1]
        self.bottomlane = self.toplane + self.lanewidth * (self.num_lanes-1)

        self.vehicle_list = []
        self.spawn_counter = 0
        self.convoy_q = 2 # Queue counter of 3 acc vehicles to form a convoy
        self.acc_spawn_loc = [self.toplane_loc[0], self.toplane_loc[1]] # acc vehicle always spawns in left lane

        self.frames = 0

    def spawn_helper(self, tmp_vehicle, vehicle_type):

        # Check vehicle surrounding
        tmp_front = tmp_vehicle.get_fov(vehicle_list=self.vehicle_list)['front']

        # If there is a vehicle infront
        if tmp_front is not None:
            front_id = tmp_front.vehicle_id()
            # If the current vehicle and the next one are both acc vehicles
            if (vehicle_type == 'acc') and (front_id['vehicle_type'] == 'acc'):
                headway = tmp_vehicle.T
            else:
                if tmp_vehicle.v != 0:
                    headway = (tmp_front.loc_back - tmp_vehicle.loc_front) / tmp_vehicle.v
                else:
                    headway = tmp_vehicle.T
            # Check the size of the car
            overlap_flag = (tmp_front.loc_back - tmp_vehicle.loc_front) <= 0
        else:
            # If no vehicles infront
            headway = tmp_vehicle.T
            overlap_flag = False

        return headway, overlap_flag

    def spawn_vehicle(self):
        """Spawns a car when internval is met with additional checks
        """

        if self.convoy_q != 0:

            # Spawn ACC, get acc_params from config
            logic_level = driving_params["acc_logic"]
            logic_dict = vehicle_models[1][logic_level]
            vehicle_type = 'acc'

            # Create a tmp Vehicle Object
            tmp_vehicle = Vehicle(logic_dict=logic_dict, spawn_loc=self.acc_spawn_loc, vehicle_type=vehicle_type)

            headway, overlap_flag = self.spawn_helper(tmp_vehicle=tmp_vehicle, vehicle_type=vehicle_type)

            if (headway >= tmp_vehicle.T and not overlap_flag):
                self.vehicle_list.append(tmp_vehicle)
                self.convoy_q -= 1

        # else:
        #     print("convoy size", self.convoy_q)
        #     # Choosing spawned vehicle type
        #     random_vehicle = random.random()
        #     acc_spawnrate = vehicle_models[1].get("acc_spawnrate")

        #     if random_vehicle <= acc_spawnrate:
        #         # Spawn ACC, get acc_params from config
        #         logic_level = driving_params["acc_logic"]
        #         logic_dict = vehicle_models[1][logic_level]
        #         vehicle_type = 'acc'
        #         self.convoy_q = 2 # add 2 acc vehicles to be spawned
        #     else:
        #         # Spawn SHC, get shc_params from config
        #         logic_level = driving_params["shc_logic"]
        #         logic_dict = vehicle_models[0][logic_level]
        #         vehicle_type = 'shc'

        #     # Choosing a spawn lane
        #     lane = int(np.random.choice(range(self.num_lanes)) * self.lanewidth)

        #     # Spawn location
        #     if vehicle_type == 'acc':
        #         print("Acc spawned")
        #         spawn_loc = self.acc_spawn_loc
        #     else:
        #         spawn_loc = [self.toplane_loc[0], self.toplane_loc[1] + lane]

        #     # Create a tmp Vehicle Object
        #     tmp_vehicle = Vehicle(logic_dict=logic_dict, spawn_loc=spawn_loc, vehicle_type=vehicle_type)

        #     headway, overlap_flag = self.spawn_helper(tmp_vehicle=tmp_vehicle)

        #     # Spawn safety check
        #     if (headway >= tmp_vehicle.T and not overlap_flag):
        #         self.vehicle_list.append(tmp_vehicle)

        #         # Reset spawn timer
        #         self.last_spawn_time = self.timer
        #         # print("Vehicle Spawned")

    def update_road(self):
        # Update vehicle local state
        for vehicle in self.vehicle_list:
            vehicle.update_local(self.ts, self.vehicle_list)

        for vehicle in self.vehicle_list:
            vehicle.update_global()

            # If vehicle reached the end of the road
            # Remove vehicle from road
            if vehicle.loc_back > self.road_length:
                self.vehicle_list.remove(vehicle)
                print("Vehicle Removed")

        # Update spawn_timer
        self.timer += self.ts
        if self.timer - self.last_spawn_time >= self.spawn_interval:
            self.spawn_vehicle()

        self.frames += 1

        return self.vehicle_list # return vehicle list of this frame

