from src.Vehicle import Vehicle
from common.config import simulation_params, driving_params, window_params
from typing import List, Dict, Any


class Convoy:

    """A class instance to represent ACC
    """

    def __init__(self, logic_dict: Dict[str, float], lead_spawn_loc: List[float], vehicle_type: str, num_subconvoy: int) -> None:

        """Creates a Convoy instance with 3 vehicles

        Args:
            logic_dict (Dict[str, float]): the level of driving cautiousness
            lead_spawn_loc (List[float]): x,y coordinates of the spawn location
            vehicle_type (str): a vehicle type descriptor
            num_subconvoy (int): number of sub-convoy in ACC
        """

        self.ts = simulation_params['ts']

        # Creating the convoy
        self.convoy_list = [
            Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type)
            for _ in range(num_subconvoy)
        ]

        # Initialize convoy-level params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.loc = lead_spawn_loc
        self.v = self.lead_vehicle.v
        self.veh_length = abs(self.loc_front - self.loc_back)
        self.convoy_dist = logic_dict.get('safe_headway') + driving_params['safety_threshold'] + window_params['vehicle_length']


    def update_convoy_local(self, vehicle_list: List[Any], vehicle_type: str) -> None:

        """Updates the convoy local parameters

        Args:
            vehicle_list (List[Any]): list of Vehicle and Convoy instances
            vehicle_type (str): a vehicle type descriptor
        """

        for idx, vehicle in enumerate(self.convoy_list):
            if idx == 0: # lead vehicle
                vehicle.update_local(vehicle_list, vehicle_type=vehicle_type)
            elif len(self.convoy_list) > 1: # update subconvoy
                # Update position
                vehicle.local_loc[1] = self.convoy_list[idx-1].local_loc[1]
                vehicle.local_loc[0] = self.convoy_list[idx-1].local_loc[0] - self.convoy_dist

                # Update driving params
                vehicle.local_v = self.convoy_list[idx-1].local_v
                vehicle.local_accel = self.convoy_list[idx-1].local_accel


    def update_convoy_global(self) -> None:

        """Updates the convoy global parameters and convoy-level parameters
        """

        for idx, vehicle in enumerate(self.convoy_list):
            if idx == 0: # lead vehicle
                vehicle.update_global()
                self.v = vehicle.v
            elif len(self.convoy_list) > 1:
                # Update driving params
                vehicle.v = vehicle.local_v

                # Update position
                new_x = self.convoy_list[idx-1].local_loc[0] - self.convoy_dist
                new_y = self.convoy_list[idx-1].local_loc[1]
                vehicle.loc = [new_x, new_y]
                vehicle.loc_front = vehicle.loc[0] + (vehicle.veh_length/2)
                vehicle.loc_back = vehicle.loc[0] - (vehicle.veh_length/2)

        # Convoy Level Params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.veh_length = abs(self.loc_front - self.loc_back)
        new_x_convoy = self.loc_front - self.veh_length/2
        new_y_convoy = self.lead_vehicle.loc[1]
        self.loc = [new_x_convoy, new_y_convoy]