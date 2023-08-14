import time

from common.config import window_params, road_params, simulation_params
from Simulation import SimulationManager
from ACC import Convoy
from Visual import Objects, Button

class Test:
    def __init__(self):
        self.is_recording = True
        self.sim = SimulationManager()
        self.is_running = True
        self.start = time.time()

    def run_test(self):
        frame = 0
        restart = False
        while self.is_running:
            # Updates simulation frame
                _, self.is_running = self.sim.update_frame(is_recording=self.is_recording, frame=frame, restart=restart)
                frame += 1

        print("\nTime Taken for 1000 vehicle to despawnn:", time.time() - self.start)

        # Saves Data
        self.sim.saving_record()
