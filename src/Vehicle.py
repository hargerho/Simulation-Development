import uuid
import time
import math
import numpy as np

from src.DriverModel import DriverModel as DM
from common.config import driving_params, window_params, road_params, simulation_params
from typing import List, Dict, Any, Tuple


class Vehicle:

    """Create a Vehicle instance
    """

    def __init__(self, logic_dict: Dict[str, float], spawn_loc: List[float], vehicle_type: str) -> None:

        """Intializing a Vehicle instance

        Args:
            logic_dict (Dict[str, float]): the level of driving cautiousness
            spawn_loc (List[float]): x,y coordinates of the spawn location
            vehicle_type (str): a vehicle type descriptor
        """

        self.id = str(uuid.uuid4()) # unique id for each vehicle
        self.ts = simulation_params['ts']

        # Road params
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

        # Getting road closure locations
        if road_params["road_closed"] == "left":
            self.road_closed = self.leftlane
        elif road_params["road_closed"] == "middle":
            self.road_closed = self.middlelane
        elif road_params["road_closed"] == "right":
            self.road_closed = self.rightlane
        else:
            self.road_closed = None

        # Vehicle params
        ## Driving params
        self.v_0 = driving_params['desired_velocity']
        self.s_0 = driving_params['safety_threshold']
        self.a = driving_params['max_acceleration']
        self.b = driving_params['comfortable_deceleration']
        self.delta = driving_params['acceleration_component']
        self.left_bias = driving_params['left_bias']
        self.change_threshold = driving_params['lane_change_threshold']
        ## Location params
        self.veh_length = window_params['vehicle_length']
        self.loc = spawn_loc # The middle of the vehicle
        self.loc_back = self.loc[0] - self.veh_length / 2
        self.loc_front = self.loc[0] + self.veh_length / 2

        # Driving logic dependent params
        self.T = logic_dict.get('safe_headway')
        self.v_var = logic_dict.get('speed_variation')
        self.politeness = logic_dict.get('politeness_factor')

        # Varying the starting speed based on vehicle logic
        val = abs(np.random.normal(self.v_0, self.v_var))
        self.v = val if (self.v_0 - 2 * self.v_var <= val <= self.v_0 + 2 * self.v_var) else self.v_0

        # Local values
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

        # Init DriverModel to this Vehicle instance
        self.driver = DM(model_params=model_params)


    def vehicle_id(self) -> None:

        """Identifies the vehicle by a set of identifications
        """

        return {
            'uuid': self.id,
            'vehicle_type': self.vehicle_type,
            'location': self.loc,
            'speed': self.v,
            'timestamp': time.perf_counter(), # higher precision
        }


    def update_positions(self, vehicle: Any, x_coord: float, not_left_lane: bool, not_right_lane: bool,
                        front_check: bool, back_check: bool, left_check: bool, right_check: bool,
                        front_left: Any, front_right: Any, back_left: Any, back_right: Any, in_between_check: bool, right: Any, left: Any) -> Tuple[Any,...]:

        """Updating the vehicle that is closest to the currently investigated vehicle

        Args:
            vehicle (Any): currently investigated vehicle
            x_coord (float): x-coordinates of the currently investigated vehicle
            not_left_lane (bool): current vehicle left lane position check
            not_right_lane (bool): current vehicle right lane position check
            front_check (bool): current vehicle front flag
            back_check (bool): current vehicle back flag
            left_check (bool): current vehicle left flag
            right_check (bool): current vehicle right flag
            front_left (Any): front left vehicle
            front_right (Any): front right vehicle
            back_left (Any): back left vehicle
            back_right (Any): back right vehicle
            in_between_check (bool): if left or right vehicle in between current vehicle
            right (Any): right vehicle
            left (Any): left vehicle

        Returns:
            Tuple[Any,...]: updated closest vehicle surrounding the current vehicle
        """


        def checking_left(vehicle: Any, left_check: bool, front_left: Any, back_left: Any, in_between_check: bool, left: Any) -> Any:

            """Checking adjacent right vehicle

            Args:
                vehicle (Any): currently investigated vehicle
                left_check (bool): right vehicle flag
                front_left (Any): front vehicle flag
                back_left (Any): back right vehicle flag
                in_between_check (bool): if the vehicle is in-between the current vehicle
                left (Any): vehicle on the right of the currently investigated vehicle

            Returns:
                Left (Any): updated vehicle on the right
            """

            if in_between_check and left_check:
                if left is None:
                    left = vehicle
                elif (
                    (abs(self.loc_back - vehicle.loc_front) <= abs(self.loc_back - left.loc_front))
                    or (abs(self.loc_front - vehicle.loc_back) <= abs(self.loc_front - left.loc_front))
                    ):
                    left = vehicle
                elif (
                    not front_left
                    and not back_left
                    and (
                        (left.loc_back - self.loc_front > 2 * left.veh_length)
                        or (self.loc_back - left.loc_front > 2 * left.veh_length)
                        )
                    ):
                    left = None

            return left


        def checking_right(vehicle: Any, right_check: bool, front_right: Any, back_right: Any, in_between_check: bool, right: Any) -> Any:

            """Checking adjacent right vehicle

            Args:
                vehicle (Any): currently investigated vehicle
                right_check (bool): right vehicle flag
                front_right (Any): front right vehicle flag
                back_right (Any): back right vehicle flag
                in_between_check (bool): if the vehicle is in-between the current vehicle
                right (Any): vehicle on the right of the currently investigated vehicle

            Returns:
                right (Any): updated vehicle on the right
            """

            if in_between_check and right_check:
                if right is None:
                    right = vehicle
                elif (
                        (abs(self.loc_back - vehicle.loc_front) <= abs(self.loc_back - right.loc_front))
                        or (abs(self.loc_front - vehicle.loc_back) <= abs(self.loc_front - right.loc_front))
                    ): # update to the new right vehicle
                    right = vehicle
                elif (
                    not front_right
                    and not back_right
                    and (
                        (right.loc_back - self.loc_front > 2 * right.veh_length)
                        or (self.loc_back - right.loc_front > 2 * right.veh_length))
                    ):
                    right = None

            return right

        if not_right_lane and front_check and right_check and (front_right is None or x_coord < front_right.loc[0]):
            front_right = vehicle

        if not_right_lane and back_check and right_check and (back_right is None or x_coord > back_right.loc[0]):
            back_right = vehicle

        if not_left_lane and front_check and left_check and (front_left is None or x_coord < front_left.loc[0]):
            front_left = vehicle

        if not_left_lane and back_check and left_check and (back_left is None or x_coord > back_left.loc[0]):
            back_left = vehicle

        # Side checks
        if isinstance(vehicle, Vehicle):
            right = checking_right(vehicle, right_check, front_right, back_right, in_between_check, right)
            left = checking_left(vehicle, left_check, front_left, back_left, in_between_check, left)
        else:
            for vehicle in vehicle.convoy_list:
                right = checking_right(vehicle, right_check, front_right, back_right, in_between_check, right)
                left = checking_left(vehicle, left_check, front_left, back_left, in_between_check, left)

        return front_left, front_right, back_left, back_right, right, left


    def get_side_params(self, vehicle: Any, front_check: bool, back_check: bool) -> bool:

        """Intermediate step to get the location of adjacent vehicles

        Args:
            vehicle (Any): currently investigated vehicle
            front_check (bool): front vehicle flag
            back_check (bool): back vehicle falg

        Returns:
            bool: if there is a vehicle adjacent to the investigated vehicle
        """

        # Vehicle behind self
        cond1 = back_check and ((self.loc_back - vehicle.loc_front <= 3*vehicle.veh_length) and (self.loc_front > vehicle.loc_front))

        # vehicle and self inline
        cond2 = ((self.loc_back >= vehicle.loc_back) and (self.loc_front <= vehicle.loc_front))

        # Vehicle infront of self
        cond3 = front_check and ((vehicle.loc_back - self.loc_front <= 3*vehicle.veh_length) and (self.loc_front > vehicle.loc_back))

        return (cond1 or cond2 or cond3)


    def get_fov_params(self, vehicle: Any) -> Tuple[float, float, float, bool, bool, bool, bool, bool, bool, bool]:

        """Intermediate step to get the location flag of surrounding vehicles

        Args:
            vehicle (Any): currently investigated vehicle

        Returns:
            Tuple[float, float, float, bool, bool, bool, bool, bool, bool, bool]: surrounding checks
        """

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


    def get_fov(self, vehicle_list: List[Any]) -> Dict[str, Any]:

        """Getting the immediate surrounding vehicles around the investigated vehicle

        Args:
            vehicle_list (List[Any]): list of Vehicles and Convoy instances

        Returns:
            Dict[str, Any]: dictionary of surrounding vehicles around the currently
            investigated vehicle
        """

        front, front_left, front_right, back_left, back_right, right, left = None, None, None, None, None, None, None


        def get_closest_vehicle(vehicle: Any, current_closest: Any) -> Any:

            """Updating the closest vehicle around the investigate vehicle

            Args:
                vehicle (Any): currently investigated vehicle
                current_closest (Any): current closest vehicle

            Returns:
                Any: updated closest vehicle
            """

            if current_closest is None or vehicle.loc[0] < current_closest.loc[0]:
                return vehicle

            return current_closest

        for vehicle in vehicle_list:
            if not isinstance(vehicle, Vehicle) and len(vehicle.convoy_list) == 1:
                vehicle = vehicle.convoy_list[0]
            x_coord, x_diff, y_diff, right_check, left_check, front_check, back_check, not_right_lane, not_left_lane, in_between_check = self.get_fov_params(vehicle)

            if x_diff > 0 and y_diff == 0:
                front = get_closest_vehicle(vehicle, front)

            front_left, front_right, back_left, back_right, right, left = self.update_positions(vehicle, x_coord, not_left_lane, not_right_lane,
                                                                                                front_check, back_check, left_check, right_check,
                                                                                                front_left, front_right, back_left, back_right,
                                                                                                in_between_check, right, left)

        return {
            "front": front,
            "front_left": front_left,
            "front_right": front_right,
            "back_left": back_left,
            "back_right": back_right,
            "right": right,
            "left": left
        }


    def is_safe_to_change(self, change_dir: str, new_front: Any, new_back: Any, right: Any, left: Any) -> bool:

        """Positional check if it is safe to change lane

        Args:
            change_dir (str): the direction of the lane change
            new_front (Any): front vehicle in the targeted lane
            new_back (Any): back vehicle in the targeted lane
            right (Any): adjacent right vehicle
            left (Any): adjacent left vehicle

        Returns:
            bool: positionally safe change lane flag
        """

        safe_front = new_front is None or new_front.loc_back > self.loc_front
        safe_back = new_back is None or new_back.loc_back < self.loc_back
        safe_side = (change_dir == 'left' and not left) or (change_dir == 'right' and not right)

        return safe_front and safe_back and safe_side


    def calc_lane_change(self, change_dir: str, current_front: Any, new_front: Any, new_back: Any, right: Any, left: Any) -> bool:

        """Determines if a vehicle should change lane or not

        Args:
            change_dir (str): the direction of the lane change
            current_front (Any): current front vehicle
            new_front (Any): front vehicle in the targeted lane
            new_back (Any): back vehicle in the targeted lane
            right (Any): adjacent right vehicle
            left (Any): adjacent left vehicle

        Returns:
            bool: change lane flag
        """


        def get_distance_and_velocity(front_vehicle: Any) -> Tuple[float, float]:

            """Getting the distance and velocity of the current vehicle in relation
            to the front vehicle

            Args:
                front_vehicle (Any): either Vehicle or Convoy instance

            Returns:
                Tuple[float, float]: distance and velocity values
            """

            if front_vehicle is None:
                distance = self.onramp_length if self.loc[1] == self.onramp else self.road_length
                velocity = self.v
            else:
                distance = front_vehicle.loc_back - self.loc_front
                velocity = front_vehicle.v

            return distance, velocity

        onramp_flag = (self.loc[1] == self.onramp)

        # Considering cases where surrounding vehicle is part of convoy
        # Front vehicle would be tail sub-convoy vehicle
        if not isinstance(current_front, Vehicle) and (current_front is not None):
            current_front = current_front.convoy_list[-1]
        if not isinstance(new_front, Vehicle) and (new_front is not None):
            new_front = new_front.convoy_list[-1]
        # Back vehicle would be lead convoy vehicle
        if not isinstance(new_back, Vehicle) and (new_back is not None):
            new_back = new_back.convoy_list[0]

        # Calculate distance and velocity of current and new front vehicles
        if onramp_flag and current_front is None:
            current_front_dist = self.onramp_length - self.loc_front
            current_front_v = 0
        else:
            current_front_dist, current_front_v = get_distance_and_velocity(front_vehicle=current_front)

        new_front_dist, new_front_v = get_distance_and_velocity(front_vehicle=new_front)

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

        change_incentive = self.driver.calc_incentive(change_direction=change_dir, v=self.v, new_front_v=new_front_v,
                                                    new_front_dist=new_front_dist, old_front_v=current_front_v,
                                                    old_front_dist=current_front_dist, disadvantage=disadvantage,
                                                    new_back_accel=new_back_accel, onramp_flag=onramp_flag)

        # For front vehicle stopped at onramp
        if (is_safe
            and current_front is None
            and (self.loc[0] >= self.onramp_length - self.loc_front - self.veh_length - self.s_0)
            and self.v >= 0
            ):
            return True

        return change_incentive and is_safe


    def shc_check_lane_change(self, surrounding: Dict[str, Any]) -> None:

        """Checking lane change for a SHC vehicle

        Args:
            surrounding (Dict[str, Any]): dictionary of surrounding vehicles around the currently
            investigated vehicle
        """

        # Left Change
        if (surrounding['front'] is not None
            and (surrounding['front'].v == 0)
            and self.loc[1] == self.rightlane
            ):
            change_flag = self.calc_lane_change(change_dir='left', current_front=surrounding['front'],
                                                new_front=surrounding['front_left'], new_back=surrounding['back_left'],
                                                right=surrounding['right'], left=surrounding['left'])

            if change_flag:
                self.local_loc[1] -= self.lanewidth

        # Right change
        if (surrounding['front'] is not None
            and (surrounding['front'].v < self.v_0)
            and self.loc[1] in [self.leftlane, self.middlelane]
            ):
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'],
                                                right=surrounding['right'], left=surrounding['left'])

            if change_flag:
                self.local_loc[1] += self.lanewidth

        # For special case on-ramp
        # Start changing in the middle of onramp to prevent lane hogging from the main road spawn
        if self.loc[1] == self.onramp and (self.loc_front > self.onramp_length/2 + road_params['onramp_offset']):
            change_flag = self.calc_lane_change(change_dir='right', current_front=surrounding['front'],
                                                new_front=surrounding['front_right'], new_back=surrounding['back_right'],
                                                right=surrounding['right'], left=surrounding['left'])

            if change_flag:
                self.local_loc[1] += self.lanewidth


    def acc_check_lane_change(self, surrounding: Dict[str, Any]) -> None:

        """Checking lane change for ACC

        Args:
            surrounding (Dict[str, Any]): dictionary of surrounding vehicles around the currently
            investigated vehicle
        """

        # Change right if front vehicle is stationary and currently on left lane
        if (surrounding['front'] is not None
            and (surrounding['front'].v == 0)
            and self.loc[1] == self.leftlane
            and (surrounding['front'].loc_back - self.loc_front <= 2 * self.veh_length)
            ):
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

            if change_flag and surrounding['left'] is None:
                if self.road_closed:
                    if (self.local_loc[1] - self.lanewidth != self.road_closed): # if lane changed into not closed
                        self.local_loc[1] -= self.lanewidth
                else:
                    self.local_loc[1] -= self.lanewidth


    def update_driving_params(self, surrounding: Dict[str, Any]) -> None:

        """Local updates of driving parameters using the IDM

        Args:
            surrounding (Dict[str, Any]): dictionary of surrounding vehicles around the currently
            investigated vehicle
        """

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

        self.local_accel = self.driver.calc_acceleration(v=self.local_v, surrounding_v=front_v, s=dist) * self.ts


    def update_local(self, vehicle_list: List[Any], vehicle_type: str) -> None:

        """Update local parameters

        Args:
            vehicle_list (List[Any]): list of Vehicle and Convoy instances
            vehicle_type (str): a vehicle type descriptor
        """

        # Get surrounding vehicles
        surrounding = self.get_fov(vehicle_list)

        if vehicle_type == 'shc':
            self.shc_check_lane_change(surrounding=surrounding)
        else:
            self.acc_check_lane_change(surrounding=surrounding)

        self.update_driving_params(surrounding)


    def update_global(self) -> None:

        """Update global timestep
        """

        self.v = self.local_v
        self.loc = self.local_loc.copy()
        self.loc_front = self.loc[0] + (self.veh_length / 2)
        self.loc_back = self.loc[0] - (self.veh_length / 2)