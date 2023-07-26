import math
class DriverModel:
    """Driver Class to following the Intelligent Driver and MOBIL Models

    This class models the divers in the simulation using the formulas that were provided in the respective papers.

    Args:
        params: Car parameters
    """
    def __init__(self, params):
        self.params = params

    def _s_star(params, v, delta_v):
        s_star = (params.s0 + params.T * v + (v + delta_v) / (2 * math.sqrt(params.a * params.b)))
        return s_star

    def calc_acceleration(self, v, surrounding_v, s):
        """Calculates the acceleration of the car based on it's parameters and the surrounding cars
        """

        delta_v = v - surrounding_v
        s_star = DriverModel._s_star(params=self.params, v=v, delta_v=delta_v)
        acceleration = (self.params.a * (1 - math.pow(v/self.params.v_0, self.params.delta) - math.pow(s_star/s, 2)))

        return acceleration

    def calc_disadvantage(self, v:float, new_surrounding_v:float, new_surrounding_dist:float, old_surrounding_v:float, old_surrounding_dist:float):
        """Calculates intermediate values to check if a lane change is safe
        """
        new_acceleration = self.calc_acceleration(v, new_surrounding_v, new_surrounding_dist)
        old_acceleration = self.calc_acceleration(v, old_surrounding_v, old_surrounding_dist)
        disadvantage = new_acceleration = old_acceleration
        return (disadvantage, new_acceleration)

    def calc_incentive(self, change_direction: bool, v: float, new_front_v: float, new_front_dist:float, old_front_v:float, old_front_dist: float, disadvantage:float, new_back_accel:float):
        """Calculates if a lane change should happen based on the MOBIL model
        """
        new_acceleration = self.calc_acceleration(v, new_front_v, new_front_dist)
        old_acceleration = self.calc_acceleration(v, old_front_v, old_front_dist)


        if change_direction == 'right': # Left to Right lane check
            a_bias = self.params.left_bias
        elif change_direction == 'left': # Right to Left lane check
            a_bias = -self.params.left_bias
        else:
            a_bias = 0 # No lane change

        change_incentive = new_acceleration - old_acceleration + (self.params.politness * disadvantage) > self.params.a_threshold + a_bias
        safety_criterion = new_back_accel > -self.params.b_safe

        return change_incentive & safety_criterion