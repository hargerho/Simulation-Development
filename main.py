from Simulation import Simulation
from Window import Window

def main():
    # Creating instances
    simulation = Simulation()
    # is_running = True
    is_paused = False
    is_recording = False

    print("Start")

    display_vehicles, simulation_record = simulation.run(is_paused=is_paused, is_recording=is_recording)

    for vehicle in display_vehicles:
        id = vehicle.vehicle_id['uuid']
        print(id)
if __name__ == "__main__":
    main()
