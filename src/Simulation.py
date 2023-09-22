import json
import os

from src.Road import Road
from src.Vehicle import Vehicle
from common.config import simulation_params
from typing import Dict, List, Any, Tuple

class SimulationManager:

    """
    This class links the Window class to the Road class via `update_frame`
    """

    def __init__(self) -> None:

        """Initializes the class by creating instances of the Road class, and initializing
        dictionaries for displaying vehicles and recording data.
        """

        self.road = Road() # Create Road class
        self.record_dict = {} # Dict of vehicle_list, key = iteration, value = vehicle_list


    def converting_objects(self, vehicle_list: List[Any]) -> List[Dict[str, float]]:

        """The function "converting_objects" takes a list of vehicles
        and returns a list of their vehicle IDs, including ACC vehicles.

        Args:
            vehicle_list (List[Any]): list of Vehicles and Convoy

        Returns:
            List[Dict[str, float]]: list of dictionary vehicle attributes
        """

        vehicle_stats = []

        for vehicle in vehicle_list:
            if isinstance(vehicle, Vehicle):
                vehicle_stats.append(vehicle.vehicle_id())
            else:
                vehicle_stats.extend(convoy.vehicle_id() for convoy in vehicle.convoy_list)

        return vehicle_stats


    def update_frame(self, is_recording: bool, frame: int, restart: bool) -> Tuple[List[Any], bool]:

        """Executing functions that is refreshed for each frame

        Args:
            is_recording (bool): recording flag
            frame (int): frame index
            restart (bool): restart flag

        Returns:
            Tuple[List[Any], bool]: list of Vehicles and Convoy, simulation running flag
        """

        vehicle_list, run_flag = self.road.update_road(restart=restart)

        # Records the simulation
        if is_recording:
            self.record_dict[frame] = self.converting_objects(vehicle_list=vehicle_list)

        # Resets the recorded dictionary
        if restart:
            self.record_dict = {}

        return vehicle_list, run_flag


    def saving_record(self) -> None:

        """Saves the recorded vehicle attributes
        """

        idx = 0
        filepath = os.path.join(simulation_params['folderpath'], simulation_params['filename'] + ".json")

        print("Saving data ...")

        # If file exist in folder, append an index to the back of the filename
        while os.path.exists(filepath):
            filename = f"{simulation_params['filename']}_{idx}"
            filepath = os.path.join(simulation_params['folderpath'], f"{filename}.json")
            idx += 1

        with open(filepath, "w") as file:
            json.dump(self.record_dict, file, indent=4)

        print("Data Saved!")