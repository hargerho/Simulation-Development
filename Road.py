import numpy as np
import random
import time
from tqdm import tqdm

from common.config import road_params, driving_params, vehicle_models, simulation_params
from Vehicle import Vehicle
from ACC import Convoy

class Road:
    def __init__(self):
        # General params
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']
        self.onramp_length = road_params['onramp_length']
        self.ts = simulation_params['ts']
        self.safety_distance = driving_params['safety_threshold']
        self.vehicle_list = []

        # Road Spawning
        if road_params['vehicle_inflow'] > 0:
            self.vehicle_frequency = road_params['vehicle_inflow'] / 3600 # per/hour -> per second
            self.spawn_interval = round(1.0/self.vehicle_frequency, 1) # Round to 1dp since ts is 1dp
            self.timer = 0.0
            self.last_spawn_time = 0
        else:
            self.vehicle_frequency, self.spawn_interval, self.timer, self.last_spawn_time = 0, 0, 0, 0

        # Onramp frequency
        if road_params['onramp_inflow'] > 0:
            self.onramp_frequency = road_params['onramp_inflow'] / 3600
            self.onramp_spawn_interval = round(1.0/self.onramp_frequency, 1)
            self.onramp_timer = 0.0
            self.onramp_last_spawn_time = 0

        # Getting y-coord of lanes
        self.onramp = self.toplane_loc[1]
        self.leftlane = self.toplane_loc[1] + self.lanewidth
        self.middlelane = self.toplane_loc[1] + (self.lanewidth * 2)
        self.rightlane = self.toplane_loc[1] + self.lanewidth * (self.num_lanes - 1)

        if road_params["road_closed"] == "left":
            self.road_closed = self.leftlane
        elif road_params["road_closed"] == "middle":
            self.road_closed = self.middlelane
        elif road_params["road_closed"] == "right":
            self.road_closed = self.rightlane
        else:
            self.road_closed = None

        # Convoy Params
        self.num_convoy_vehicles = road_params['num_convoy_vehicles']  # Queue counter of 3 acc vehicles to form a convoy
        self.acc_spawn_loc = [self.toplane_loc[0], self.leftlane] # acc vehicle always spawns in left lane
        self.frames = 0
        self.convoy_spawned = False

        # Testing Controls
        self.vehicle_despawn = 0
        self.run_flag = True
        self.total_vehicles = simulation_params['num_vehicles']
        self.progress_bar = tqdm(total=self.total_vehicles, desc="Despawning Vehicles")

    def spawn_helper(self, tmp_vehicle, vehicle_type):

        if vehicle_type == 'shc':
            # Check vehicle surrounding
            tmp_front = tmp_vehicle.get_fov(vehicle_list=self.vehicle_list)['front']
            # If there is a vehicle infront
            if tmp_front is not None:
                if tmp_vehicle.v != 0:
                    headway = (tmp_front.loc_back - tmp_vehicle.loc_front) / tmp_vehicle.v
                else:
                    headway = tmp_vehicle.T
                # Check the size of the car
                overlap_flag = (tmp_front.loc_back - tmp_vehicle.loc_front - self.safety_distance) < 0
            else:
                # If no vehicles infront
                headway = tmp_vehicle.T
                overlap_flag = False

            headway_flag = headway >= tmp_vehicle.T

        else:
            tmp_lead = tmp_vehicle.convoy_list[0] # Lead ACC vehicle
            tmp_vehicle_tail = tmp_vehicle.convoy_list[-1]
            tmp_front = tmp_lead.get_fov(vehicle_list=self.vehicle_list)['front']

            # If there is a vehicle infront
            if tmp_front is not None:
                if tmp_lead.v != 0:
                    headway = (tmp_front.loc_back - tmp_lead.loc_front) / tmp_lead.v
                else:
                    headway = tmp_lead.T
                # Check the size of the car
                # TODO CHECK i think is tmp_lead.loc_front
                overlap_flag = (tmp_front.loc_back - tmp_vehicle_tail.loc_front - self.safety_distance) < 0
            else:
                # If no vehicles infront
                headway = tmp_lead.T
                overlap_flag = False
            headway_flag = headway >= tmp_lead.T

        return headway_flag, overlap_flag

    def spawn_vehicle(self):
        """Spawns a car when internval is met with additional checks
        """
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

        # Choosing a spawn lane from the 3 motorway lanes
        lane = int(np.random.choice(range(1,self.num_lanes)) * self.lanewidth)

        # Spawn location
        if vehicle_type == 'acc':

            # Create a tmp convoy
            tmp_convoy = Convoy(logic_dict=logic_dict, lead_spawn_loc=self.acc_spawn_loc, vehicle_type=vehicle_type,
                                num_subconvoy=self.num_convoy_vehicles)
            headway_flag, overlap_flag = self.spawn_helper(tmp_vehicle=tmp_convoy,vehicle_type=vehicle_type)

        else:
            spawn_loc = [self.toplane_loc[0], self.toplane_loc[1] + lane]

            # Create a tmp Vehicle Object
            tmp_vehicle = Vehicle(logic_dict=logic_dict, spawn_loc=spawn_loc, vehicle_type=vehicle_type)

            headway_flag, overlap_flag = self.spawn_helper(tmp_vehicle=tmp_vehicle, vehicle_type=vehicle_type)

        # Spawn safety check
        if (headway_flag and not overlap_flag):
            if vehicle_type == 'shc':
                self.convoy_spawned = False
                self.vehicle_list.append(tmp_vehicle)
            else:
                self.convoy_spawned = True
                self.vehicle_list.append(tmp_convoy)

        # Reset spawn timer even if vehicle is not spawn to prevent upstream overcrowding
        if self.convoy_spawned:
            self.last_spawn_time = self.timer + (2*self.spawn_interval)
        else:
            self.last_spawn_time = self.timer

    def spawn_onramp(self):
        # Spawn SHC, get shc_params from config
        logic_level = driving_params["shc_logic"]
        logic_dict = vehicle_models[0][logic_level]
        vehicle_type = 'shc'
        spawn_loc = self.toplane_loc

        # Create a tmp Vehicle Object
        tmp_vehicle = Vehicle(logic_dict=logic_dict, spawn_loc=spawn_loc, vehicle_type=vehicle_type)
        headway_flag, overlap_flag = self.spawn_helper(tmp_vehicle=tmp_vehicle, vehicle_type=vehicle_type)

        # Spawn safety check
        if (headway_flag and not overlap_flag):
            self.vehicle_list.append(tmp_vehicle)

        # Reset onramp spawn timer if vehicle is not spawn to prevent upstream overcrowding
        self.onramp_last_spawn_time = self.onramp_timer

    def update_road(self, restart):
        if restart:
            self.vehicle_list = []

        # Update vehicle local state
        for vehicle in self.vehicle_list:

            if isinstance(vehicle, Convoy):
                vehicle.update_convoy(self.vehicle_list, vehicle_type='acc')
            else:
                vehicle.update_local(self.vehicle_list, vehicle_type='shc')

        for vehicle in self.vehicle_list:
            if not isinstance(vehicle, Convoy):
                vehicle.update_global()

            # If vehicle reached the end of the road
            # Remove vehicle from road
            if isinstance(vehicle, Convoy):
                for convoy in vehicle.convoy_list:
                    if convoy.loc_front > self.road_length:
                        if len(vehicle.convoy_list) == 1: # If last convoy in the convoy_list
                            self.vehicle_list.remove(vehicle)
                        else: # Remove one vehicle from the convoy
                            vehicle.convoy_list.remove(convoy)
            # Simulate roadblock by setting a SHC vehicle to 0m/s
            elif self.road_closed is not None:
                if vehicle.loc_front > self.road_length/2 and vehicle.loc[1] == self.road_closed:
                    vehicle.v = 0
            if isinstance(vehicle, Vehicle) and vehicle.loc_front > self.road_length:
                self.vehicle_list.remove(vehicle)
                self.vehicle_despawn += 1
                # self.progress_bar.update(1)

        # Update spawn_timer
        if road_params['vehicle_inflow'] > 0:
            self.timer += self.ts
            if self.timer - self.last_spawn_time >= self.spawn_interval:
                self.spawn_vehicle()

        if road_params['onramp_inflow'] > 0:
            # Update onramp_spawn_timer
            self.onramp_timer += self.ts
            if self.onramp_timer - self.onramp_last_spawn_time >= self.onramp_spawn_interval:
                self.spawn_onramp()

        self.frames += 1

        if simulation_params['testing'] and self.vehicle_despawn > self.total_vehicles:
            self.run_flag = False

        return self.vehicle_list, self.run_flag # return vehicle list of this frame

