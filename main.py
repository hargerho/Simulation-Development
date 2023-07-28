from Simulation import Simulation
from Window import Window

def main():
    # Creating instances
    simulation = Simulation()
    # is_running = True
    is_paused = False
    is_recording = False

    print("Start")

    display_vehicles, record_simulation = simulation.run()
    print(display_vehicles)

if __name__ == "__main__":
    main()
