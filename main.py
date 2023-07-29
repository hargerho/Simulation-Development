from Simulation import Simulation
from Window import Window
import json

def main():
    # Creating instances
    simulation = Simulation()
    # is_running = True
    is_paused = False
    is_recording = False

    print("Start")

    display_vehicles, record_simulation = simulation.run()

    vehicle_data = json.dumps(display_vehicles)
    with open("data/vehicle_data.json", "w") as outfile:
        outfile.write(vehicle_data)

if __name__ == "__main__":
    main()
