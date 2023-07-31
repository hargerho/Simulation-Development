import uuid
import numpy as np
import time

from common.config import driving_params, window_params, road_params
from DriverModel import DriverModel as DM

class Vehicle:
    """Class to store the vehicle parameters, including IDM parameters

    Kwargs:
        If arg is passed as tuple, then first value is the average and second is the standard deviation (with cuttof at 2 sigma)

        v_0: Desired velocity
        s_0: Safety threshold
        T: Safe time headway
        a: Maximum acceleration
        b: Comfortable deceleration
        delta: Acceleration component
        veh_length: Vehicle length
        change_threshold: lane_change_threshold
        politeness: lane change politeness
        left_bias: Bias to switch to the left lane
    """
    def __init__(self, logic_dict, spawn_loc, vehicle_type):

        self.id = str(uuid.uuid4()) # unique id for each vehicle

        # Road Params
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']
        # Getting y-coord of lanes
        self.toplane = self.toplane_loc[1]
        self.bottomlane = self.toplane + self.lanewidth * (self.num_lanes-1)

        self.v_0 = driving_params['desired_velocity']
        self.s_0 = driving_params['safety_threshold']
        self.a = driving_params['max_acceleration']
        self.b = driving_params['comfortable_deceleration']
        self.delta = driving_params['acceleration_component']
        self.veh_length = window_params['vehicle_length'] # in window params
        self.left_bias = driving_params['left_bias']
        self.change_threshold = driving_params['lane_change_threshold']

        # Driving Logic Dependent Params
        self.T = logic_dict.get('safe_headyway')
        self.v_var = logic_dict.get('speed_variation')
        self.politeness = logic_dict.get('politeness_factor')

        self.v = self.variation(self.v_0, self.v_var)

        self.loc = spawn_loc
        self.loc_back = self.loc[0] - self.veh_length / 2
        self.loc_front = self.loc[0] + self.veh_length / 2

        # Local Values
        self.local_loc = list(spawn_loc)
        self.local_v = self.v # initial
        self.local_accel = 0.

        self.vehicle_type = vehicle_type

        model_params = {
            "v_0": self.v_0,
            "s_0": self.s_0,
            "a": self.a,
            "b": self.b,
            "delta": self.delta,
            "T": self.T,
            "left_bias": self.left_bias,
            "politeness": self.politeness,
            "change_threshold": self.change_threshold
        }

        # Init DriverModel to this Vehicle class
        self.driver = DM(model_params=model_params)

    def variation(self,avg, dev):
        val = abs(np.random.normal(avg, dev))
        if avg - 2 * dev <= val <= avg + 2 * dev:
            return val
        else:
            return avg

    def vehicle_id(self):
        """Identifies the vehicle by a set of identifications
        """

        dict_id = {
            'uuid': self.id,
            'vehicle_type': self.vehicle_type,
            'location': self.loc,
            'speed': self.v,
            'acceleration': self.local_accel,
            'vehicle_length': self.veh_length
        }

        return dict_id

    def get_fov(self, vehicle_list):
        """
        Get other vehicles around this vehicle

        Returns: Dictionary with:
            frontNow: current vehicle in front of this vehicle
            frontLeft: front left vehicle
            frontRight: front right vehicle
            backLeft: back left vehicle
            backRight: back right vehicle
        """
        front = None
        front_left = None
        front_right = None
        back_left = None
        back_right = None

        for vehicle in vehicle_list:
            x_coord = vehicle.loc[0]
            current_y_coord = self.loc[1]
            x_diff = x_coord - self.loc[0]
            y_diff = vehicle.loc[1] - current_y_coord
            right_check = vehicle.loc[1] == current_y_coord + self.lanewidth
            left_check = vehicle.loc[1] == current_y_coord - self.lanewidth
            front_check = x_coord > self.loc[0]
            back_check = x_coord < self.loc[0]

            not_right_lane = current_y_coord != self.bottomlane
            not_left_lane = current_y_coord != self.toplane

            if x_diff > 0 and y_diff == 0:
                if front is None or x_coord < front.loc[0]:
                    front = vehicle
                else:
                    front = front

            if not_right_lane and front_check and right_check:
                # Front right
                if front_right is None or x_coord < front_right.loc[0]:
                    front_right = vehicle

            if not_right_lane and back_check and right_check:
                # Back right
                if back_right is None or x_coord > back_right.loc[0]:
                    back_right = vehicle

            if not_left_lane and front_check and left_check:
                # Front left
                if front_left is None or x_coord < front_left.loc[0]:
                    front_left = vehicle

            if not_left_lane and back_check and left_check:
                # Back left
                if back_left is None or x_coord > back_left.loc[0]:
                    back_left = vehicle
            else:
                continue

        surrounding_vehicles = {
            "front": front,
            "front_left": front_left,
            "front_right": front_right,
            "back_left": back_left,
            "back_right": back_right
        }

        return surrounding_vehicles

    def calc_lane_change(self, change_dir, current_front, new_front, new_back):
        """Calculates if a vehicle should change lanes

        Args:
            change_dir: string of change direction
            current_front: vehicle that is currently in front
            new_front: vehicle that will be in front after the change
            new_back: vehicle that will be in the back after the change

        Returns: True if the lane change should happen
        """

        # Current timestep
        # Getting distance of front vehicle
        if current_front is not None:
            # If there is a front vehicle
            current_front_dist = current_front.loc_back - self.loc_front
            current_front_v = current_front.v
        else:
            # No vehicles infront
            current_front_dist = self.road_length
            current_front_v = self.v

        # Next timestep
        # Getting distance of new front vehicle
        if new_front is not None:
            # If there is a front vehicle
            new_front_dist = new_front.loc_back - self.loc_front
            new_front_v = new_front.v
        else:
            # No vehicles infront
            new_front_dist = self.road_length
            new_front_v = self.v

        # Considering the vehicle behind
        if new_back is None:
            # If there is no vehicle behind
            disadvantage, new_back_accel = 0, 0
        else:
            # Current timestep
            if new_front is not None:
                current_back_dist = new_front.loc_back - new_back.loc_front
                current_back_v = new_front.v
            else:
                current_back_dist = self.road_length
                current_back_v = self.v

            new_back_dist = self.loc_back - new_back.loc_front
            new_back_v = self.v

            # Getting the disadvantage in changing
            # Consider effects to back vehicle
            disadvantage, new_back_accel = new_back.driver.calc_disadvantage(v=new_back.v, new_surrounding_v=new_back_v, new_surrounding_dist=new_back_dist,
                                                                     old_surrounding_v=current_back_v, old_surrounding_dist=current_back_dist)

        # Considering front vehicle
        change_incentive = self.driver.calc_incentive(change_direction=change_dir, v=self.v, new_front_v=new_front_v, new_front_dist=new_front_dist, old_front_v=current_front_v,
                                            old_front_dist=current_front_dist, disadvantage=disadvantage, new_back_accel=new_back_accel)

        # Extra safety check
        if new_front is not None:
            safeFront = new_front.loc_back > self.loc_front
        else:
            safeFront = True

        if new_back is not None:
            safeBack = new_back.loc_front < self.loc_back
        else:
            safeBack = True

        changeFlag = change_incentive and safeFront and safeBack

        return changeFlag

    def update_local(self, ts, vehicle_list):
        """Update local timestep

        Args:
            ts (float): timestep
        """

        # Get surrounding vehicles
        surrounding = self.get_fov(vehicle_list)
        change_flag = False

        # Lane change flag and update lane location
        # Right change
        if self.loc[1] != self.bottomlane:
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'])
            if change_flag:
                self.local_loc[1] += self.lanewidth
        # Left change
        if self.loc[1] != self.toplane:
            change_flag = self.calc_lane_change(change_dir='left', current_front=surrounding['front'],
                                                new_front=surrounding['front_left'], new_back=surrounding['back_left'])
            if change_flag:
                self.local_loc[1] -= self.lanewidth

        # Update road traverse
        self.local_loc[0] += (self.v * ts)

        # Updating local dist
        if surrounding['front'] is not None:
            dist = surrounding['front'].loc_back - self.loc_front
            # Ensure dist is non-zero
            if dist <= 0:
                dist = 1e-9
        else:
            dist = self.road_length

        if surrounding['front'] is not None:
            front_v = surrounding['front'].v
        else:
            front_v = self.v

        # Update local driving parameters
        self.local_v = self.v
        self.local_accel = self.driver.calc_acceleration(v=self.v, surrounding_v=front_v, s=dist) * ts
        self.local_v += self.local_accel
        self.local_v = max(self.local_v, 0)

    def update_global(self):
        """Update global timestep
        """
        self.v = self.local_v
        self.loc = self.local_loc.copy()
        self.loc_front = self.loc[0] - (self.veh_length / 2)
        self.loc_back = self.loc[0] - (self.veh_length / 2)




