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
        self.name = 'vehicle'

        # Road Params
        self.num_lanes = road_params['num_lanes']
        self.toplane_loc = road_params['toplane_loc']
        self.lanewidth = road_params['lanewidth']
        self.road_length = road_params['road_length']
        self.onramp_length = road_params['onramp_length']
        self.onramp_offset = road_params['onramp_offset']

        # Getting y-coord of lanes
        self.onramp = self.toplane_loc[1]
        self.leftlane = self.toplane_loc[1] + self.lanewidth
        self.middlelane = self.toplane_loc[1] + (self.lanewidth * 2)
        self.rightlane = self.toplane_loc[1] + self.lanewidth * (self.num_lanes - 1)

        # Getting road closure
        if road_params["road_closed"] == "left":
            self.road_closed = self.leftlane
        elif road_params["road_closed"] == "middle":
            self.road_closed = self.middlelane
        elif road_params["road_closed"] == "right":
            self.road_closed = self.rightlane
        else:
            self.road_closed = None
        self.partial_close = road_params['partial_close']

        # Vehicle params
        self.v_0 = driving_params['desired_velocity']
        self.s_0 = driving_params['safety_threshold']
        self.a = driving_params['max_acceleration']
        self.b = driving_params['comfortable_deceleration']
        self.delta = driving_params['acceleration_component']
        self.veh_length = window_params['vehicle_length'] # in window params
        self.left_bias = driving_params['left_bias']
        self.change_threshold = driving_params['lane_change_threshold']
        self.convoy_dist = driving_params['convoy_dist']

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

        self.model_params = {
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
        self.driver = DM(model_params=self.model_params)

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

    def update_positions(self, vehicle, x_coord, not_left_lane, not_right_lane, front_check, back_check, left_check, right_check,
                         front_left, front_right, back_left, back_right, in_between_check, right, left):

        if not_right_lane and front_check and right_check and (front_right is None or x_coord < front_right.loc[0]):
            front_right = vehicle

        if not_right_lane and back_check and right_check and (back_right is None or x_coord > back_right.loc[0]):
            back_right = vehicle

        if not_left_lane and front_check and left_check and (front_left is None or x_coord < front_left.loc[0]):
            front_left = vehicle

        if not_left_lane and back_check and left_check and (back_left is None or x_coord > back_left.loc[0]):
            back_left = vehicle

        if isinstance(vehicle, Vehicle):
            if in_between_check and right_check:
                if right is None:
                    right = vehicle
                elif ((abs(self.loc_back - vehicle.loc_front) <= abs(self.loc_back - right.loc_front)) or (abs(self.loc_front - vehicle.loc_back) <= abs(self.loc_front - right.loc_front))): # update to the new right vehicle
                    right = vehicle
                elif not (front_right or back_right) and ((right.loc_back - self.loc_front > 2 * right.veh_length) or (self.loc_back - right.loc_front > 2 * right.veh_length)):
                    right = None

            if in_between_check and left_check:
                if left is None:
                    left = vehicle
                elif ((abs(self.loc_back - vehicle.loc_front) <= abs(self.loc_back - left.loc_front)) or (abs(self.loc_front - vehicle.loc_back) <= abs(self.loc_front - left.loc_front))):
                    left = vehicle
                elif not (front_left or back_left) and ((left.loc_back - self.loc_front > 2 * left.veh_length) or (self.loc_back - left.loc_front > 2 * left.veh_length)):
                    left = None
        else:
            for vehicle in vehicle.convoy_list:
                if in_between_check and right_check:
                    if right is None:
                        right = vehicle
                    elif ((abs(self.loc_back - vehicle.loc_front) <= abs(self.loc_back - right.loc_front)) or (abs(self.loc_front - vehicle.loc_back) <= abs(self.loc_front - right.loc_front))): # update to the new right vehicle
                        right = vehicle
                    elif not (front_right or back_right) and ((right.loc_back - self.loc_front > 2 * right.veh_length) or (self.loc_back - right.loc_front > 2 * right.veh_length)):
                        right = None

                if in_between_check and left_check:
                    if left is None:
                        left = vehicle
                    elif ((abs(self.loc_back - vehicle.loc_front) <= abs(self.loc_back - left.loc_front)) or (abs(self.loc_front - vehicle.loc_back) <= abs(self.loc_front - left.loc_front))):
                        left = vehicle
                    elif not (front_left or back_left) and ((left.loc_back - self.loc_front > 2 * left.veh_length) or (self.loc_back - left.loc_front > 2 * left.veh_length)):
                        left = None
        return front_left, front_right, back_left, back_right, right, left

    def get_distance_and_velocity(self, front_vehicle):
        if front_vehicle is None:
            distance = self.onramp_length if self.loc[1] == self.onramp else self.road_length
            velocity = self.v
        else:
            distance = front_vehicle.loc_back - self.loc_front
            velocity = front_vehicle.v
        return distance, velocity

    def get_side_params(self, vehicle, front_check, back_check):
        cond1 = back_check and ((self.loc_back - vehicle.loc_front <= 3*vehicle.veh_length) and (self.loc_front > vehicle.loc_front)) # Vehicle behind self
        cond2 = ((self.loc_back >= vehicle.loc_back) and (self.loc_front <= vehicle.loc_front)) # vehicle and self inline
        cond3 = front_check and ((vehicle.loc_back - self.loc_front <= 3*vehicle.veh_length) and (self.loc_front > vehicle.loc_back)) # Vehicle infront of self
        return (cond1 or cond2 or cond3)

    def get_fov_params(self, vehicle):
        x_coord = vehicle.loc[0]
        current_y_coord = self.loc[1]
        x_diff = x_coord - self.loc[0]
        y_diff = vehicle.loc[1] - current_y_coord
        right_check = vehicle.loc[1] == current_y_coord + self.lanewidth
        left_check = vehicle.loc[1] == current_y_coord - self.lanewidth
        front_check = x_coord > self.loc[0]
        back_check = x_coord < self.loc[0]

        not_right_lane = current_y_coord != self.rightlane
        not_left_lane = current_y_coord != self.leftlane

        if isinstance(vehicle, Vehicle):
            in_between_check = self.get_side_params(vehicle=vehicle, front_check=front_check, back_check=back_check)
        else:
            checklist = []
            for convoy in vehicle.convoy_list:
                side_check = self.get_side_params(vehicle=convoy, front_check=front_check, back_check=back_check)
                checklist.append(side_check)
            in_between_check = any(checklist)

        return x_coord, x_diff, y_diff, right_check, left_check, front_check, back_check, not_right_lane, not_left_lane, in_between_check

    def get_fov(self, vehicle_list):
        front, front_left, front_right, back_left, back_right, right, left = None, None, None, None, None, None, None

        for vehicle in vehicle_list:
            if not isinstance(vehicle, Vehicle) and len(vehicle.convoy_list) == 1:
                vehicle = vehicle.convoy_list[0]
            x_coord, x_diff, y_diff, right_check, left_check, front_check, back_check, not_right_lane, not_left_lane, in_between_check = self.get_fov_params(vehicle)

            if x_diff > 0 and y_diff == 0:
                front = self.get_closest_vehicle(vehicle, front)

            front_left, front_right, back_left, back_right, right, left = self.update_positions(
                vehicle, x_coord, not_left_lane, not_right_lane, front_check, back_check, left_check, right_check,
                front_left, front_right, back_left, back_right, in_between_check, right, left
            )

        return {
            "front": front,
            "front_left": front_left,
            "front_right": front_right,
            "back_left": back_left,
            "back_right": back_right,
            "right": right,
            "left": left
        }

    def is_safe_to_change(self, change_dir, new_front, new_back, right, left):

        safe_front = new_front is None or new_front.loc_back > self.loc_front
        safe_back = new_back is None or new_back.loc_back < self.loc_back
        safe_side = (change_dir == 'left' and not left) or (change_dir == 'right' and not right)

        return safe_front and safe_back and safe_side

    def calc_lane_change(self, change_dir, current_front, new_front, new_back, right, left):

        onramp_flag = (self.loc[1] == self.onramp)

        if not isinstance(current_front, Vehicle) and (current_front is not None):
            current_front = current_front.convoy_list[-1]
        if not isinstance(new_front, Vehicle) and (new_front is not None):
            new_front = new_front.convoy_list[-1]
        if not isinstance(new_back, Vehicle) and (new_back is not None):
            new_back = new_back.convoy_list[0]

        # Calculate distance and velocity of current and new front vehicles
        if onramp_flag and current_front is None:
            current_front_dist = self.onramp_length - self.loc_front
            current_front_v = 0
        else:
            current_front_dist, current_front_v = self.get_distance_and_velocity(current_front)

        new_front_dist, new_front_v = self.get_distance_and_velocity(new_front)

        # Calculate the disadvantage and new back acceleration if there is a vehicle behind
        if new_back is None:
            disadvantage, new_back_accel = 0, 0
        else:
            new_back_front = new_back.loc_front
            new_back_v = new_back.v
            # Current timestep
            if new_front is None:
                current_back_dist = self.onramp_length if onramp_flag else self.road_length
                current_back_v = self.v
            else:
                current_back_dist = new_front.loc_back - new_back_front
                current_back_v = new_front.v

            if onramp_flag and current_front is None:
                current_back_dist = self.onramp_length - self.loc_back
                current_back_v = self.v

            new_back_dist = self.loc_back - new_back_front
            new_back_v = self.v

            # Getting the disadvantage in changing
            # Consider effects to back vehicle
            disadvantage, new_back_accel = new_back.driver.calc_disadvantage(v=new_back.v, new_surrounding_v=new_back_v, new_surrounding_dist=new_back_dist,
                                                                        old_surrounding_v=current_back_v, old_surrounding_dist=current_back_dist)

        is_safe = self.is_safe_to_change(change_dir, new_front, new_back, right, left)

        change_incentive = self.driver.calc_incentive(
            change_direction=change_dir, v=self.v, new_front_v=new_front_v,
            new_front_dist=new_front_dist, old_front_v=current_front_v,
            old_front_dist=current_front_dist, disadvantage=disadvantage,
            new_back_accel=new_back_accel, onramp_flag=onramp_flag
        )

        # For front vehicle stopped at onramp
        if is_safe and current_front is None and (self.loc[0] >= self.onramp_length - self.loc_front - self.veh_length - self.s_0) and self.v >= 0:
            return True

        return change_incentive and is_safe

    def update_driving_params(self, surrounding):
        # IDM Updates
        # Update road traverse and velocity
        self.local_v = self.v # Assign global variable to local computations

        # If negative velocity (not allowed)
        if self.local_v + self.local_accel * self.ts < 0:
            self.local_loc[0] -= (1/2) * (self.local_v/self.local_accel) # based on IDM paper
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
            dist = max(self.onramp_length + self.onramp_offset - self.loc_front - self.s_0 - self.veh_length, 1e-9)
            front_v = self.local_v
        else:
            dist = self.road_length
            front_v = self.local_v

        self.local_accel = self.driver.calc_acceleration(v=self.local_v, surrounding_v=front_v, s=dist, lead_flag=True) * self.ts

    def update_acc_driving_params(self, surrounding):

        self.local_v = self.v

        # If negative velocity (not allowed)
        if self.local_v + self.local_accel * self.ts < 0:
            self.local_loc[0] -= (1/2) * (self.local_v/self.local_accel) # based on IDM paper
            self.local_v = 0
        else:
            self.local_v += self.local_accel * self.ts
            self.local_loc[0] += (self.local_v * self.ts) + self.local_accel * math.pow(self.ts,2)/2

        if surrounding is not None:
            # dist_tmp = max(surrounding.loc_back - self.loc_front, self.convoy_dist)
            # dist = max(dist_tmp, 1e-9)
            dist = max(surrounding.loc_back - self.loc_front, self.convoy_dist)
            front_v = surrounding.v
        else:
            print("True")
            dist = self.road_length
            front_v = self.local_v
        self.local_accel = self.driver.calc_acceleration(v=self.local_v, surrounding_v=front_v, s=dist, lead_flag=False) * self.ts

    def partial_road_close(self, surrounding):
        # for partial road close
        if (surrounding['front_left'] is None and surrounding['back_left'] is None): # if no vehicle in front and back of to change lane
            self.local_loc[1] -= self.lanewidth
        if (surrounding['front_left'] is None and surrounding['back_left'] is not None):
            if surrounding['back_left'].loc_front + self.s_0 + self.veh_length < self.loc_back:
                self.local_loc[1] -= self.lanewidth
        if (surrounding['back_left'] is None and surrounding['front_left'] is not None and surrounding['front_left'].v != 0):
            if surrounding['front_left'].loc_back - self.s_0 - self.veh_length > self.loc_front:
                self.local_loc[1] -= self.lanewidth
        if (surrounding['front_left'] is not None and surrounding['front_left'].v != 0 and surrounding['back_left'] is not None):
            if (surrounding['front_left'].loc_back - self.s_0 - self.veh_length > self.loc_front and surrounding['back_left'].loc_front + self.s_0 < self.loc_back): # if there are vehicles but no possible collision
                self.local_loc[1] -= self.lanewidth

    def shc_check_lane_change(self, surrounding):
        # Left Change
        if surrounding['front'] is not None and (surrounding['front'].v == 0) and self.loc[1] == self.rightlane:
            change_flag = self.calc_lane_change(change_dir='left', current_front=surrounding['front'],
                                                new_front=surrounding['front_left'], new_back=surrounding['back_left'],
                                                right=surrounding['right'], left=surrounding['left'])
            if change_flag:
                self.local_loc[1] -= self.lanewidth
        # Right change
        if surrounding['front'] is not None and (surrounding['front'].v == 0) and self.loc[1] in [self.leftlane, self.middlelane]:
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'],
                                                right=surrounding['right'], left=surrounding['left'])
            if change_flag:
                self.local_loc[1] += self.lanewidth
        # For special case on-ramp
        if self.loc[1] == self.onramp and (self.loc_front > self.onramp_length/2 + road_params['onramp_offset']): # Start changing in the middle of onramp to prevent lane hogging from the main road spawn
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'],
                                                right=surrounding['right'], left=surrounding['left'])
            if change_flag:
                self.local_loc[1] += self.lanewidth

    def acc_check_lane_change(self, surrounding):
        # Change right if front vehicle is stationary and currently on left lane
        if surrounding['front'] is not None and (surrounding['front'].v == 0) and self.loc[1] == self.leftlane and (surrounding['front'].loc_back - self.loc_front <= 2 * self.veh_length):
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'],
                                                right=surrounding['right'], left=surrounding['left'])
            if change_flag:
                self.local_loc[1] += self.lanewidth
        # Left change if it is on middle or right lane
        if self.loc[1] in [self.middlelane, self.rightlane]:
            change_flag = self.calc_lane_change(change_dir='left', current_front=surrounding['front'],
                                                    new_front=surrounding['front_left'], new_back=surrounding['back_left'],
                                                    right=surrounding['right'], left=surrounding['left'])

            if self.partial_close: # ACC can return back to blocked lane
                if change_flag and surrounding['left'] is None:
                    self.partial_road_close(surrounding=surrounding)
            elif self.road_closed: # if there is a road closure
                if change_flag and (self.local_loc[1] - self.lanewidth != self.road_closed): # if lane changed into not closed
                    self.local_loc[1] -= self.lanewidth
            elif change_flag: # if can change but road is closed
                self.local_loc[1] = self.local_loc[1]

    def update_local(self, vehicle_list, vehicle_type, lead_flag):
        # Get surrounding vehicles
        surrounding = self.get_fov(vehicle_list)

        if vehicle_type == 'shc':
            # Lane change flag and update lane location
            # Right change
            self.shc_check_lane_change(surrounding=surrounding)
        elif lead_flag:
            self.acc_check_lane_change(surrounding=surrounding)

        if vehicle_type == 'shc' or lead_flag:
            self.update_driving_params(surrounding)
        elif not lead_flag:
            self.update_acc_driving_params(surrounding)

    def update_global(self):
        """Update global timestep
        """
        self.v = self.local_v
        self.loc = self.local_loc.copy()
        self.loc_front = self.loc[0] + (self.veh_length / 2)
        self.loc_back = self.loc[0] - (self.veh_length / 2)