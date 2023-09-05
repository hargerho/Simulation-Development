import math
from typing import Dict, Tuple


class DriverModel:

    """Creating the DriverModel specific to the created vehicle
    """

    def __init__(self, model_params: Dict[str, float]) -> None:

        """Intializing IDM based on level of driving cautiousness

        Args:
            model_params (Dict[str, float]): parameters used for the driving logic selected
        """

        self.v_0 = model_params['v_0'] # Max desired speed of vehicle
        self.s_0 = model_params['s_0'] # Min desired distance between vehicles
        self.a = model_params['a'] # Max acceleration
        self.b = model_params['b'] # Comfortable deceleration
        self.delta = model_params['delta'] # Acceleration component
        self.T = model_params['T'] # Reaction time safe headway
        self.left_bias = model_params['left_bias'] # Keep left bias
        self.politeness = model_params['politeness'] # Change lane politeness
        self.change_threshold = model_params['change_threshold'] # Change lane threshold


    def s_star(self, v: float, delta_v: float) -> float:

        """Computes the actual desired distance between vehicle i and vehicle i-1

        Args:
            v (float): current velocity
            delta_v (float): velocity difference

        Returns:
            float: actual desired distance between vehicle i and vehicle i-1
        """

        return (self.s_0
            + max(0, self.T * v + (v * delta_v) / (2 * math.sqrt(self.a * self.b)))
            )


    def calc_acceleration(self, v: float, surrounding_v: float, s: float) -> float:

        """Calculates the vehicle acceleration based on it's parameters and the surrounding cars

        Args:
            v (float): current vehicle velocity
            surrounding_v (float): velocity of other vehicle
            s (float): current actual distance

        Returns:
            float: vehicle acceleration
        """

        delta_v = v - surrounding_v
        s_star = self.s_star(v=v, delta_v=delta_v)

        return (self.a * (1 - math.pow(v/self.v_0, self.delta) - math.pow(s_star/s, 2)))


    def calc_disadvantage(self, v: float, new_surrounding_v: float, new_surrounding_dist: float, old_surrounding_v: float, old_surrounding_dist: float) -> Tuple[float, float]:

        """Calculates intermediate values to check if a lane change is safe

        Args:
            v (float): current vehicle velocity
            new_surrounding_v (float): velocity of targeted front vehicle
            new_surrounding_dist (float): distance between targeted front vehicle and current vehicle if change lane
            old_surrounding_v (float): velocity of current front vehicle
            old_surrounding_dist (float): distance between current front vehicle and current vehicle

        Returns:
            Tuple[float, float]: disadvantage of changing lanes and new acceleration if lane is changed
        """

        new_acceleration = self.calc_acceleration(v, new_surrounding_v, new_surrounding_dist)
        old_acceleration = self.calc_acceleration(v, old_surrounding_v, old_surrounding_dist)
        disadvantage = old_acceleration - new_acceleration

        return (disadvantage, new_acceleration)


    def calc_incentive(self, change_direction: str, v: float, new_front_v: float, new_front_dist: float,
                    old_front_v: float, old_front_dist: float, disadvantage: float, new_back_accel: float, onramp_flag: bool) -> bool:

        """Calculates if a lane change should happen based on the MOBIL model

        Args:
            change_direction (str): the direction of the lane change
            v (float): current vehicle velocity
            new_front_v (float): velocity of targeted front vehicle
            new_front_dist (float): distance between targeted front vehicle and current vehicle if change lane
            old_front_v (float): velocity of current front vehicle
            old_front_dist (float): distance between current front vehicle and current vehicle
            disadvantage (float): difference in acceleration if lane changed
            new_back_accel (float): new acceleration if lane is changed
            onramp_flag (bool): onramp vehicle check

        Returns:
            bool: if a lane change should happen
        """

        new_acceleration = self.calc_acceleration(v, new_front_v, new_front_dist)
        old_acceleration = self.calc_acceleration(v, old_front_v, old_front_dist)

        if change_direction == 'right':
            a_bias = self.left_bias
        elif change_direction == 'left':
            a_bias = -self.left_bias
        elif onramp_flag: # If the vehicle is onramp, decrease threshold for right lane change
            a_bias = -self.left_bias
        else:
            a_bias = 0 # No lane change

        change_incentive = new_acceleration - old_acceleration - (self.politeness * disadvantage) > self.change_threshold + a_bias
        safety_criterion = new_back_accel >= -self.b

        return change_incentive & safety_criterion