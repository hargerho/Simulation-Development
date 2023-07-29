from Simulation import Simulation
from Window import Window
import json

def save_data(data, filename):
    print("Saving data, this might take a while...")
    json.dump(data, open(filename, "w"))

def main():
    # Creating instances
    simulation = Simulation()
    # is_running = True
    is_paused = False
    is_recording = False

    print("Start")

    display_vehicles, record_simulation = simulation.run()

    # vehicle_data = json.dumps(display_vehicles)
    # with open("data/vehicle_data.json", "w") as outfile:
    #     outfile.write(vehicle_data)
    save_data(display_vehicles, "data/vehicle_data.json")

if __name__ == "__main__":
    main()
