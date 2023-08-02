import math
import time
class DriverModel:
    def __init__(self, model_params):
        self.v_0 = model_params['v_0']
        self.s_0 = model_params['s_0']
        self.a = model_params['a']
        self.b = model_params['b']
        self.delta = model_params['delta']
        self.T = model_params['T']
        self.left_bias = model_params['left_bias']
        self.politeness = model_params['politeness']
        self.change_threshold = model_params['change_threshold']

    def s_star(self, v, delta_v):
        return (
            self.s_0
            + self.T * v
            + (v + delta_v) / (2 * math.sqrt(self.a * self.b))
        )

    def calc_acceleration(self, v, surrounding_v, s):
        """Calculates the acceleration of the car based on it's parameters and the surrounding cars
        """
        delta_v = v - surrounding_v
        s_star = self.s_star(v=v, delta_v=delta_v)
        x = math.pow(v/self.v_0, self.delta)
        return (self.a * (1 - x - math.pow(s_star/s, 2)))

    def calc_disadvantage(self, v, new_surrounding_v, new_surrounding_dist, old_surrounding_v, old_surrounding_dist):
        """Calculates intermediate values to check if a lane change is safe
        """
        new_acceleration = self.calc_acceleration(v, new_surrounding_v, new_surrounding_dist)
        old_acceleration = self.calc_acceleration(v, old_surrounding_v, old_surrounding_dist)
        disadvantage = new_acceleration - old_acceleration
        return (disadvantage, new_acceleration)

    def calc_incentive(self, change_direction, v, new_front_v, new_front_dist, old_front_v, old_front_dist, disadvantage, new_back_accel):
        """Calculates if a lane change should happen based on the MOBIL model
        """
        new_acceleration = self.calc_acceleration(v, new_front_v, new_front_dist)
        old_acceleration = self.calc_acceleration(v, old_front_v, old_front_dist)


        if change_direction == 'right': # Left to Right lane check
            a_bias = self.left_bias
        elif change_direction == 'left': # Right to Left lane check
            a_bias = -self.left_bias
        else:
            a_bias = 0 # No lane change

        change_incentive = new_acceleration - old_acceleration + (self.politeness * disadvantage) > self.change_threshold + a_bias
        safety_criterion = new_back_accel > -self.b

        return change_incentive & safety_criterion