import uuid
import time
import numpy as np
import math

from common.config import driving_params, window_params, road_params, simulation_params
from DriverModel import DriverModel as DM

class Vehicle:
    def __init__(self, logic_dict, spawn_loc, vehicle_type):

        self.id = str(uuid.uuid4()) # unique id for each vehicle
        self.ts = simulation_params['ts']

        # Road Params
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']
        self.onramp_length = road_params['onramp_length']

        # Getting y-coord of lanes
        self.onramp = self.toplane_loc[1]
        self.leftlane = self.toplane_loc[1] + self.lanewidth
        self.middlelane = self.toplane_loc[1] + (self.lanewidth * 2)
        self.rightlane = self.toplane_loc[1] + self.lanewidth * (self.num_lanes - 1)

        self.v_0 = driving_params['desired_velocity']
        self.s_0 = driving_params['safety_threshold']
        self.a = driving_params['max_acceleration']
        self.b = driving_params['comfortable_deceleration']
        self.delta = driving_params['acceleration_component']
        self.veh_length = window_params['vehicle_length']
        self.left_bias = driving_params['left_bias']
        self.change_threshold = driving_params['lane_change_threshold']

        # Driving Logic Dependent Params
        self.T = logic_dict.get('safe_headway')
        self.v_var = logic_dict.get('speed_variation')
        self.politeness = logic_dict.get('politeness_factor')

        self.v = self.variation(self.v_0, self.v_var)

        self.loc = spawn_loc # The middle of the vehicle
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
        return val if avg - 2 * dev <= val <= avg + 2 * dev else avg

    def vehicle_id(self):
        """Identifies the vehicle by a set of identifications
        """

        return {
            'uuid': self.id,
            'vehicle_type': self.vehicle_type,
            'location': self.loc,
            'speed': self.v,
            'timestamp': time.perf_counter(), # higher precision
        }

    @staticmethod
    def get_closest_vehicle(vehicle, current_closest):
        if current_closest is None or vehicle.loc[0] < current_closest.loc[0]:
            return vehicle
        return current_closest

    @staticmethod
    def update_positions(vehicle, x_coord, not_left_lane, not_right_lane, front_check, back_check, left_check, right_check,
                         front_left, front_right, back_left, back_right, right, left):

        if right_check:
            right = vehicle if (right is None) else right

        if left_check:
            left = vehicle if (left is None) else left

        if not_right_lane and front_check and right_check:
            front_right = vehicle if (front_right is None or  vehicle.loc_front < front_right.loc_back) else front_right

        if not_right_lane and back_check and right_check:
            back_right = vehicle if (back_right is None or vehicle.loc_back > back_right.loc_front) else back_right

        if not_left_lane and front_check and left_check:
            front_left = vehicle if (front_left is None or vehicle.loc_front < front_left.loc_back) else front_left

        if not_left_lane and back_check and left_check:
            back_left = vehicle if (back_left is None or vehicle.loc_back > back_left.loc_front) else back_left

        return front_left, front_right, back_left, back_right, right, left

    def get_fov_params(self, vehicle):
        x_coord = vehicle.loc_back
        current_y_coord = self.loc[1]
        x_diff = vehicle.loc_back - self.loc_front
        y_diff = vehicle.loc[1] - current_y_coord

        y_right_check = vehicle.loc[1] == current_y_coord + self.lanewidth
        y_left_check = vehicle.loc[1] == current_y_coord - self.lanewidth

        x_check = ((vehicle.loc_back < self.loc_back) and (vehicle.loc_front < self.loc_front)) or ((vehicle.loc_back > self.loc_back) and (vehicle.loc_front > self.loc_front))

        right_check = y_right_check and x_check
        left_check = y_left_check and x_check

        front_check = vehicle.loc_back > self.loc_front
        back_check = vehicle.loc_front < self.loc_back

        not_right_lane = current_y_coord != self.rightlane
        not_left_lane = current_y_coord != self.leftlane

        return x_coord, x_diff, y_diff, right_check, left_check, front_check, back_check, not_right_lane, not_left_lane

    def get_convoy_fov(self, convoy, front, front_left, front_right, back_left, back_right, right, left):

        # Lead vehicle will be the back of a vehicle POV
        # Tail vehicle will be front of a vehicle POV
        lead_vehicle = convoy.convoy_list[0]

        current_y_coord = self.loc[1]

        x_diff = convoy.loc_back - self.loc_front
        y_diff = lead_vehicle.loc[1] - current_y_coord

        y_right_check = convoy.loc[1] == current_y_coord + self.lanewidth
        y_left_check = convoy.loc[1] == current_y_coord - self.lanewidth

        x_check = ((convoy.loc_back < self.loc_back) and (convoy.loc_front > self.loc_front)) or ((convoy.loc_back > self.loc_back) and (convoy.loc_front > self.loc_front)) or ((convoy.loc_back < self.loc_back) and (convoy.loc_front < self.loc_front))

        right_check = y_right_check and x_check
        left_check = y_left_check and x_check

        front_check = convoy.loc_back > self.loc_front
        back_check = convoy.loc_front < self.loc_back

        not_right_lane = current_y_coord != self.rightlane
        not_left_lane = current_y_coord != self.leftlane

        # Right/Left avaliable space check
        if right_check:
            right = convoy if (right is None) else right

        if left_check:
            left = convoy if (left is None) else left

        if x_diff > 0 and y_diff == 0:
            front = convoy if front is None or convoy.loc_front < front.loc[0] else front

        if not_right_lane and front_check and right_check:
            front_right = convoy if (front_right is None or convoy.loc_front < front_right.loc_back) else front_right

        if not_right_lane and back_check and right_check:
            back_right = convoy if (back_right is None or convoy.loc_back > back_right.loc_front) else back_right

        if not_left_lane and front_check and left_check:
            front_left = convoy if (front_left is None or convoy.loc_front < front_left.loc_back) else front_left

        if not_left_lane and back_check and left_check:
            back_left = convoy if (back_left is None or convoy.loc_back > back_left.loc_front) else back_left

        return front, front_left, front_right, back_left, back_right, right, left

    def get_fov(self, vehicle_list):
        front, front_left, front_right, back_left, back_right, right, left = None, None, None, None, None, None, None

        for vehicle in vehicle_list:
            # If convoy left 1 vehicle, treat it like a shc vehicle
            if isinstance(vehicle, Vehicle) or (len(vehicle.convoy_list) == 1):
                # get the last acc vehicle in conovy list and treat it like shc vehicle
                if not isinstance(vehicle, Vehicle):
                    vehicle = vehicle.convoy_list[0]
                x_coord, x_diff, y_diff, right_check, left_check, front_check, back_check, not_right_lane, not_left_lane = self.get_fov_params(vehicle)

                if x_diff > 0 and y_diff == 0:
                    front = self.get_closest_vehicle(vehicle, front)

                front_left, front_right, back_left, back_right, right, left = self.update_positions(
                    vehicle, x_coord, not_left_lane, not_right_lane, front_check, back_check, left_check, right_check,
                    front_left, front_right, back_left, back_right, right, left
                )
            else:
                front, front_left, front_right, back_left, back_right, right, left = self.get_convoy_fov(vehicle, front, front_left, front_right, back_left, back_right, right, left)

        return {
            "front": front,
            "front_left": front_left,
            "front_right": front_right,
            "back_left": back_left,
            "back_right": back_right,
            "right": right,
            "left": left
        }

    def headway_check(self, surround):
        if surround is not None and self.v != 0:
            headway = (surround.loc_back - self.loc_front) / self.v
        else:
            headway = self.T
        return headway >= self.T

    def is_safe_to_change(self, change_dir, new_front, new_back, right, left):
        safe_front = (new_front.loc_back > self.loc_front and self.headway_check(new_front)) if new_front is not None else True
        safe_back = (new_back.loc_front < self.loc_back and self.headway_check(new_back)) if new_back is not None else True
        safe_side = False

        if (change_dir == 'left') and (left is None):
            safe_side = True
        elif (change_dir == 'right') and (right is None):
            safe_side = True

        return safe_front and safe_back and safe_side

    def calc_lane_change(self, change_dir, current_front, new_front, new_back, right, left):
        # Checking if onramp
        onramp_flag = self.loc[1] == self.onramp

        # Current timestep
        # Getting distance of front vehicle
        if current_front is None: # No vehicles infront
            current_front_dist = self.onramp_length if onramp_flag else self.road_length
            current_front_v = self.v
        else:
            # If there is a front shc vehicle
            current_front_dist = current_front.loc_back - self.loc_front
            current_front_v = current_front.v

        # Next timestep
        # Getting distance of new front vehicle
        if new_front is None: # No vehicles infront
            new_front_dist = self.onramp_length if onramp_flag else self.road_length
            new_front_v = self.v
        else:
            # If there is a front shc vehicle
            new_front_dist = new_front.loc_back - self.loc_front
            new_front_v = new_front.v
        # Considering the vehicle behind
        if new_back is None:
            # If there is no vehicle behind
            disadvantage, new_back_accel = 0, 0
        else:
            new_back_front = new_back.loc_front
            new_back_v = new_back.v
            # Getting the correct new_back assignment
            if not isinstance(new_back, Vehicle):
                new_back = new_back.convoy_list[-1] # i think should be new_back.convoy_list[0]

            # Current timestep
            if new_front is None:
                current_back_dist = self.onramp_length if onramp_flag else self.road_length
                current_back_v = self.v
            else:
                current_back_dist = new_front.loc_back - new_back_front
                current_back_v = new_front.v
            new_back_dist = self.loc_back - new_back_front
            new_back_v = self.v

            # Getting the disadvantage in changing
            # Consider effects to back vehicle
            disadvantage, new_back_accel = new_back.driver.calc_disadvantage(v=new_back.v, new_surrounding_v=new_back_v, new_surrounding_dist=new_back_dist,
                                                                     old_surrounding_v=current_back_v, old_surrounding_dist=current_back_dist)

        # Considering front vehicle
        change_incentive = self.driver.calc_incentive(change_direction=change_dir, v=self.v, new_front_v=new_front_v, new_front_dist=new_front_dist, old_front_v=current_front_v,
                                            old_front_dist=current_front_dist, disadvantage=disadvantage, new_back_accel=new_back_accel, onramp_flag=onramp_flag)

        is_safe = self.is_safe_to_change(change_dir, new_front, new_back, right, left)

        # For front vehicle stopped at onramp
        if is_safe and current_front is None and (self.loc[0] >= self.onramp_length - self.loc_front - self.veh_length - self.s_0) and self.v >= 0 and onramp_flag:
            return True

        if (self.v == 0) and is_safe:
            if current_front is not None:
                if current_front_v == 0:
                    change_incentive = True

        return change_incentive and is_safe

    def check_lane_change(self, surrounding):
        # if surrounding['front'] is not None and (surrounding['front'].v == 0) and self.loc[1] == self.rightlane: # Left change
        if self.loc[1] == self.rightlane:
            change_flag = self.calc_lane_change(change_dir='left', current_front=surrounding['front'],
                                                new_front=surrounding['front_left'], new_back=surrounding['back_left'], right=surrounding['right'], left=surrounding['left'])
            if change_flag:
                self.local_loc[1] -= self.lanewidth
        # Right change
        if surrounding['front'] is not None and (surrounding['front'].v == 0) and self.loc[1] in [self.leftlane, self.middlelane]: # Left change
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'], right=surrounding['right'], left=surrounding['left'])
            if change_flag:
                self.local_loc[1] += self.lanewidth
        # For special case on-ramp
        if self.loc[1] == self.onramp and (self.loc_front > self.onramp_length/2): # Start changing in the middle of onramp to prevent lane hogging from the main road spawn
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'], right=surrounding['right'], left=surrounding['left'])
            if change_flag:
                self.local_loc[1] += self.lanewidth

    def update_driving_params(self, surrounding):
        # IDM Updates
        # Update road traverse and velocity
        self.local_v = self.v # Assign global variable to local computations

        # If negative velocity (not allowed)
        if self.local_v + self.local_accel * self.ts < 0:
            self.local_loc[0] -= (1/2) * (math.pow(self.local_v, 2)/self.local_accel) # based on IDM paper
            self.local_v = 0
        else:
            self.local_v += self.local_accel * self.ts
            self.local_loc[0] += (self.local_v * self.ts) + self.local_accel * math.pow(self.ts,2)/2

        # Updating acceleration
        # If there is a front vehicle
        if surrounding['front'] is not None:
            dist = max(surrounding['front'].loc_back - self.loc_front - self.s_0, 1e-9)
            front_v = surrounding['front'].v
        elif self.local_loc[1] == self.onramp:
            dist = max(self.onramp_length - self.loc_front - self.veh_length - self.s_0, 1e-9)
            front_v = self.local_v
        else:
            dist = self.road_length
            front_v = self.local_v

        self.local_accel = self.driver.calc_acceleration(v=self.local_v, surrounding_v=front_v, s=dist) * self.ts

    def update_local(self, vehicle_list, vehicle_type):
        # Get surrounding vehicles
        surrounding = self.get_fov(vehicle_list)

        if vehicle_type == 'shc':
            # Lane change flag and update lane location
            # Right change
            self.check_lane_change(surrounding=surrounding)
        else:
            # Change right if front vehicle is stationary and currently on left lane
            if surrounding['front'] is not None and (surrounding['front'].v == 0) and self.loc[1] == self.leftlane:
                change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                    new_front=surrounding['front_right'], new_back=surrounding['back_right'], right=surrounding['right'], left=surrounding['left'])
                if change_flag:
                    self.local_loc[1] += self.lanewidth
            # Left change if it is on middle or right lane
            if self.loc[1] in [self.middlelane, self.rightlane]:
                change_flag = self.calc_lane_change(change_dir='left', current_front=surrounding['front'],
                                                    new_front=surrounding['front_left'], new_back=surrounding['back_left'], right=surrounding['right'], left=surrounding['left'])
                if change_flag:
                    self.local_loc[1] -= self.lanewidth

        self.update_driving_params(surrounding)

    def update_global(self):
        """Update global timestep
        """
        self.v = self.local_v
        self.loc = self.local_loc.copy()
        self.loc_front = self.loc[0] + (self.veh_length / 2)
        self.loc_back = self.loc[0] - (self.veh_length / 2)