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

        self.simulation_record = []
        self.display_vehicles = [1]

    def run(self):
        is_paused = False
        is_recording = False
        is_running = True

        while is_running:
            print("Simulation Running")
            if not is_paused:
                print("Updating")
                self.road.update_road(ts=self.ts)
                for vehicle in self.road.vehicle_list:
                    self.display_vehicles.append(vehicle.vehicle_id())

                # Pause Simulation
                if keyboard.is_pressed('p'):
                    is_paused = True
                    print("Simulation Paused")

                # Continue simulation if previously paused
                elif is_paused and keyboard.is_pressed('c'):
                    is_paused = False
                    print("Simulation Unpaused")

                # Start recording the simulation
                elif is_recording:
                    # records simulation
                    self.record_simulation.append([vehicle.vehicle_id() for vehicle in self.road.vehicle_list]) # List of dict_id

                # Terminate simulation
                elif keyboard.is_pressed('q'):
                    is_running = False
                    print("Simulation Quit")

            # Continue looping if no keyboard command is pressed
            else:
                continue


        return self.display_vehicles, self.simulation_record

