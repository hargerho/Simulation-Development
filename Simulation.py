import numpy as np
import keyboard
from collections import deque

from common.config import simulation_params
from Road import Road

class Simulation:
    """Class to manage the simulation

    Args:
        ts: Time step to use when running the simulation
    """
    def __init__(self):
        self.ts = simulation_params['ts']
        self.road = Road()

        # self.simulation_record = []
        # self.display_vehicles = [1]

    def run(self):
        is_paused = False
        is_recording = False
        is_running = True
        display_vehicles = deque()
        record_simulation = []
        print("Simulation Running")
        while is_running:

            if not is_paused:
                self.road.update_road(ts=self.ts)
                for vehicle in self.road.vehicle_list:
                    display_vehicles.append(vehicle.vehicle_id())

                # Pause Simulation
                if keyboard.is_pressed('p'):
                    is_paused = True
                    print("Simulation Paused")

                # Start recording the simulation
                if is_recording:
                    # records simulation
                    record_simulation.append([vehicle.vehicle_id() for vehicle in self.road.vehicle_list]) # List of dict_id

                # Terminate simulation
                if keyboard.is_pressed('q'):
                    is_running = False
                    print("Simulation Quits")

            # Continue looping if no keyboard command is pressed
            elif is_paused:
                if keyboard.is_pressed('c'):
                    is_paused = False
                    print("Simulation Unpaused")
                elif keyboard.is_pressed('q'):
                    is_running = False
                    print("Simulation Quited")
            else:
                continue


        return display_vehicles, record_simulation

