import random
import numpy as np

from ACC import Convoy
from Vehicle import Vehicle
from common.config import road_params, driving_params, vehicle_models, simulation_params
from tqdm import tqdm
from typing import List, Type, Any, Tuple

# For repeatabiity
random.seed(42)


class Road:

    """Creates a road instance that managers all vehicles on the motorway
    """

    def __init__(self) -> None:

        """Initializing the Road parameters
        """

        # Getting road params
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.onramp_x = self.toplane_loc[0] + road_params['onramp_offset']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']
        self.onramp_length = road_params['onramp_length']

        # Getting y-coord of lanes
        self.onramp = self.toplane_loc[1]
        self.leftlane = self.toplane_loc[1] + self.lanewidth
        self.middlelane = self.toplane_loc[1] + (self.lanewidth * 2)
        self.rightlane = self.toplane_loc[1] + self.lanewidth * (self.num_lanes - 1)

        # Getting road closure locations
        if road_params["road_closed"] == "left":
            self.road_closed = self.leftlane
        elif road_params["road_closed"] == "middle":
            self.road_closed = self.middlelane
        elif road_params["road_closed"] == "right":
            self.road_closed = self.rightlane
        else:
            self.road_closed = None

        # Driving params
        self.safety_distance = driving_params['safety_threshold']
        self.vehicle_list = []

        # Road spawning
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
        else:
            self.onramp_frequency, self.onramp_spawn_interval, self.onramp_timer, self.onramp_last_spawn_time = 0, 0, 0, 0

        # Convoy params
        self.num_convoy_vehicles = road_params['num_convoy_vehicles']  # Queue counter of 3 acc vehicles to form a convoy
        self.acc_spawn_loc = [self.toplane_loc[0], self.leftlane] # acc vehicle always spawns in left lane
        self.convoy_spawned = False

        # Testing and simulation controls
        self.vehicle_despawn = 0
        self.run_flag = True
        self.ts = simulation_params['ts']
        self.total_vehicles = simulation_params['num_vehicles']
        if simulation_params['testing']:
            self.progress_bar = tqdm(total=self.total_vehicles, desc="Despawning Vehicles")


    def spawn_helper(self, tmp_vehicle: Type[Vehicle], vehicle_type: str) -> Tuple[bool]:

        """Checks if tmp_vehicle can spawn into the motorway safely

        Args:
            tmp_vehicle (Type[Vehicle]): The temporary vehicle to be spawned
            vehicle_type (str): a vehicle type descriptor

        Returns:
            headway_flag (bool): Determine if tmp_vehicle have enough headway to the front vehicle
            overlap_flag (bool): Determine if tmp_vehicle will overlap front vehicle
        """

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
             # Lead ACC vehicle
            tmp_lead = tmp_vehicle.convoy_list[0]
            tmp_front = tmp_lead.get_fov(vehicle_list=self.vehicle_list)['front']

            # If there is a vehicle infront
            if tmp_front is not None:
                if tmp_lead.v != 0:
                    headway = (tmp_front.loc_back - tmp_lead.loc_front) / tmp_lead.v
                else:
                    headway = tmp_lead.T

                # Check the size of the car
                overlap_flag = (tmp_front.loc_back - tmp_lead.loc_front  - self.safety_distance) < 0
            else:
                # If no vehicles infront
                headway = tmp_lead.T
                overlap_flag = False
            headway_flag = headway >= tmp_lead.T

        return headway_flag, overlap_flag


    def spawn_vehicle(self) -> None:

        """Spawns a car when internval is met with additional checks
        """

        # Choosing spawned vehicle type
        random_vehicle = random.random()
        acc_spawnrate = vehicle_models[1].get("acc_spawnrate")

        if random_vehicle <= acc_spawnrate:
            # Spawn ACC, get acc_params from config
            vehicle_type = 'acc'
            logic_level = driving_params["acc_logic"]
            logic_dict = vehicle_models[1][logic_level]
        else:
            # Spawn SHC, get shc_params from config
            vehicle_type = 'shc'
            logic_level = driving_params["shc_logic"]
            logic_dict = vehicle_models[0][logic_level]

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


    def spawn_onramp(self) -> None:

        """Handles the vehicle spawn into the onramp
        """

        # Spawn SHC, get shc_params from config
        vehicle_type = 'shc'
        logic_level = driving_params["shc_logic"]
        logic_dict = vehicle_models[0][logic_level]
        spawn_loc = [self.onramp_x, self.toplane_loc[1]]

        # Create a tmp Vehicle Object
        tmp_vehicle = Vehicle(logic_dict=logic_dict, spawn_loc=spawn_loc, vehicle_type=vehicle_type)
        headway_flag, overlap_flag = self.spawn_helper(tmp_vehicle=tmp_vehicle, vehicle_type=vehicle_type)

        # Spawn safety check
        if (headway_flag and not overlap_flag):
            self.vehicle_list.append(tmp_vehicle)

        # Reset onramp spawn timer if vehicle is not spawn to prevent upstream overcrowding
        self.onramp_last_spawn_time = self.onramp_timer


    def check_road_closed(self) -> None:

        """Check for updated road closure location from user interaction
        """

        if road_params["road_closed"] == "left":
            self.road_closed = self.leftlane
        elif road_params["road_closed"] == "middle":
            self.road_closed = self.middlelane
        elif road_params["road_closed"] == "right":
            self.road_closed = self.rightlane
        else:
            self.road_closed = None


    def check_inflow(self, timer: float, last_spawn_time: float, onramp_timer: float, onramp_last_spawn_time: float) -> None:

        """Checks for new inflow update from user interaction

        Args:
            timer (float): motorway timer for vehicle spawns
            last_spawn_time (float): time at which the vehicle was last spawned
            onramp_timer (float): onramp timer for onramp vehicle spawns
            onramp_last_spawn_time (float): time at which onramp vehicle was last spawned
        """

        # Road spawning
        if road_params['vehicle_inflow'] > 0:
            self.vehicle_frequency = road_params['vehicle_inflow'] / 3600
            self.spawn_interval = round(1.0/self.vehicle_frequency, 1)
            self.timer = timer
            self.last_spawn_time = last_spawn_time
        else:
            self.vehicle_frequency, self.spawn_interval, self.timer, self.last_spawn_time = 0, 0, 0, 0

        # Onramp frequency
        if road_params['onramp_inflow'] > 0:
            self.onramp_frequency = road_params['onramp_inflow'] / 3600
            self.onramp_spawn_interval = round(1.0/self.onramp_frequency, 1)
            self.onramp_timer = onramp_timer
            self.onramp_last_spawn_time = onramp_last_spawn_time
        else:
            self.onramp_frequency, self.onramp_spawn_interval, self.onramp_timer, self.onramp_last_spawn_time = 0, 0, 0, 0


    def despawn_stop_vehicles(self, vehicle: Any) -> None:

        """Remove the vehicle when reach the end of the road.
        Stps vehicle if road closed

        Args:
            vehicle (Any): Either a Vehicle or Convoy instance
        """

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
        if self.road_closed is not None:
            if vehicle.loc[1] == self.road_closed and isinstance(vehicle, Vehicle):
                if (vehicle.loc_front >= self.road_length/2) and (vehicle.loc_front <= self.road_length/2 + 20):
                    vehicle.v = 0
                    vehicle.local_v = 0
                    vehicle.local_accel = 0

        if isinstance(vehicle, Vehicle) and vehicle.loc_front > self.road_length:
            self.vehicle_list.remove(vehicle)
            self.vehicle_despawn += 1
            if simulation_params['testing']:
                self.progress_bar.update(1)


    def update_vehicle(self) -> None:

        """Updates the vehicle local and global parameters
        """

        # Update vehicle local state
        for idx, vehicle in enumerate(self.vehicle_list):
            tmp_list = self.vehicle_list.copy()
            tmp_list.pop(idx)
            if isinstance(vehicle, Convoy):
                vehicle.update_convoy_local(self.vehicle_list, vehicle_type='acc')
            else:
                vehicle.update_local(tmp_list, vehicle_type='shc')

        for vehicle in self.vehicle_list:
            if isinstance(vehicle, Convoy):
                vehicle.update_convoy_global()
            else:
                vehicle.update_global()

            self.despawn_stop_vehicles(vehicle=vehicle)


    def spawning(self) -> None:

        """Initiate a vehicle spawn
        """

        # Update spawn_timer
        if road_params['vehicle_inflow'] > 0:
            self.timer += (self.ts * simulation_params['playback_speed'])
            if self.timer - self.last_spawn_time >= self.spawn_interval:
                self.spawn_vehicle()

        if road_params['onramp_inflow'] > 0:
            # Update onramp_spawn_timer
            self.onramp_timer += (self.ts * simulation_params['playback_speed'])
            if self.onramp_timer - self.onramp_last_spawn_time >= self.onramp_spawn_interval:
                self.spawn_onramp()
        else:
            self.onramp_timer, self.onramp_last_spawn_time, self.onramp_spawn_interval = 0,0,0


    def update_road(self, restart: bool) -> Tuple[List[Any], bool]:

        """Update the road simulation when called by Simulation

        Args:
            restart (bool): Restart flag that resets the vehicle list when true

        Returns:
            self.vehicle_list (List[Any]): Contains Vehicles and Convoy on the road at a specific frame
            self.run_flag (bool): Terminates the Simulation when testing is completed
        """

        if restart:
            self.vehicle_list = []

        # Checking for road close updates
        self.check_road_closed()

        # Checking for flow updates
        self.check_inflow(self.timer, self.last_spawn_time, self.onramp_timer, self.onramp_last_spawn_time)

        self.update_vehicle()

        self.spawning()

        # Terminates simulation when testing is completed
        if simulation_params['testing'] and self.vehicle_despawn > self.total_vehicles:
            self.run_flag = False

        return self.vehicle_list, self.run_flag # return vehicle list of this frame

