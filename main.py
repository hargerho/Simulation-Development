from Simulation import Simulation
from Window import Window

def main():
    # Creating instances
    # simulation = Simulation()
    display = Window()

    while display.is_running:
        # Display
        # display_vehicles, simulation_record = simulation.run(is_paused=display.is_paused, is_recording=display.is_recording)
        display_vehicles = []
        display.run_window(display_vehicles)

if __name__ == "__main__":
    main()
