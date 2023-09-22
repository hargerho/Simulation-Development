from src.Simulation import SimulationManager


class Test:

    """class to manage testing
    """

    def __init__(self):

        """Initializing variables for testing class
        """

        self.sim = SimulationManager()
        self.is_recording = True
        self.is_running = True


    def run_test(self):

        """Runs the test
        """

        frame = 0
        restart = False
        while self.is_running:
            # Updates simulation frame
                _, self.is_running = self.sim.update_frame(is_recording=self.is_recording, frame=frame, restart=restart)
                frame += 1

        # Saves Data
        self.sim.saving_record()
