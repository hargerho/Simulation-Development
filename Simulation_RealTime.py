import numpy as np
import keyboard

from Road import Road
import time
from Window_RealTime import Window

class Simulation:
    """Class to manage the simulation

    Args:
        ts: Time step to use when running the simulation
    """
    def __init__(self):
        self.road = Road() # Create Road class
        self.display_vehicles = {} # Dict of vehicle_list, key = iteration, value = vehicle_list
        self.win = Window()

    def run(self, is_paused, is_recording):
        is_paused = False
        is_recording = False
        is_running = True
        record_simulation = []
        print("Simulation Running")
        main_iteration = 0
        while is_running:
            save_list = []
            if not is_paused:
                # print("Main_iteration: ", main_iteration)
                vehicle_list_obj = self.road.update_road()

                # Iterate through the list of vehicle objects
                for vehicle_obj in vehicle_list_obj:
                    # For each vehicle object, obtain its vehicle id Dict
                    vehicle_list = vehicle_obj.vehicle_id()

                    # Store dict in list
                    save_list.append(vehicle_list)

                self.display_vehicles[main_iteration]=save_list
                main_iteration += 1
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


        return self.display_vehicles, record_simulation

