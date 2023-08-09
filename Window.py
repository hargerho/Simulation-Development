import pygame
import sys
import time

from common.config import window_params, road_params, simulation_params
from Simulation import SimulationManager
from ACC import Convoy
from Visual import Objects, Button

class Window:
    def __init__(self):
        pygame.init()

        # Setting up the Simulation
        self.is_running = True
        self.sim = SimulationManager() # Create the simulation

        # Creating the window
        self.width = window_params["window_width"]
        self.height = window_params["window_height"]
        self.ts = simulation_params["ts"]
        self.speed = simulation_params["playback_speed"]

        self.vehicle_length = window_params["vehicle_length"]
        self.vehicle_width = window_params["vehicle_width"]
        self.road_length = road_params["road_length"]
        self.lanewidth = road_params["lanewidth"]

        # Loading images
        self.road_image = pygame.image.load(window_params["road_image"])
        self.road_border = pygame.image.load(window_params["road_border"])
        self.acc_image = pygame.image.load(window_params["acc_image"])
        self.shc_image = pygame.image.load(window_params["shc_image"])
        self.restart_image = pygame.image.load(window_params["restart_button"])
        self.pause_image = pygame.image.load(window_params["pause_button"])
        self.record_image = pygame.image.load(window_params["record_button"])
        self.play_image = pygame.image.load(window_params["play_button"])

        # Creating window parameters
        self.win = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.is_paused = False
        self.is_recording = simulation_params['record']
        self.restart = False

        self.paused_time = 0
        self.last_pause_start = 0
        self.start_time = pygame.time.get_ticks()  # Record the start time of the simulation

    def create_buttons(self):
        self.pause_button = Button(1100, 100, self.pause_image, 0.05)
        self.play_button = Button(1200, 100, self.play_image, 0.05)

        self.restart_button = Button(1300, 100, self.restart_image, 0.05)
        self.restart = self.restart_button.draw(self.win)

        # self.record_button = Button(1400, 100, self.record_image, 0.05)
        # self.is_recording = self.record_button.draw(self.win)

    def draw_timer(self):
        if self.is_paused:
            elapsed_time = (self.last_pause_start - self.start_time) - self.paused_time
        else:
            elapsed_time = pygame.time.get_ticks() - self.start_time - self.paused_time

        milliseconds = elapsed_time % 1000
        seconds = (elapsed_time // 1000) % 60
        minutes = (elapsed_time // 60000) % 60
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        font = pygame.font.Font(None, 36)
        timer_text = font.render(time_str, True, window_params["black"])
        self.win.blit(timer_text, (10, 10))

    def draw_fixed_objects(self):  # sourcery skip: extract-duplicate-method

        # Fill background
        self.win.fill(window_params["white"])

        # Drawing the onramp
        onrampSurface = pygame.Surface((road_params['onramp_length'], road_params['lanewidth']))
        onrampSurface.fill(window_params['grey'])
        rampRect = onrampSurface.get_rect()
        rampRect.topleft = (road_params['toplane_loc'][0], road_params['toplane_loc'][1] - window_params['vehicle_width'])
        self.win.blit(onrampSurface, rampRect.topleft)

        # Drawing the road
        road_width = road_params['lanewidth'] * (road_params['num_lanes'] - 1) + window_params['vehicle_width']
        roadSurface = pygame.Surface((road_params['road_length'], road_width))
        roadSurface.fill(window_params['black'])
        roadRect = roadSurface.get_rect()
        roadRect.topleft = (road_params['toplane_loc'][0], road_params['toplane_loc'][1] - window_params['vehicle_width'] + road_params['lanewidth'])
        self.win.blit(roadSurface, roadRect.topleft)

        self.create_buttons()

        # Draw speed limit

    def refresh_window(self, vehicle_list):

        # Drawing the vehicles
        for vehicle in vehicle_list:

            if isinstance(vehicle, Convoy):
                for convoy in vehicle.convoy_list:
                    # Indexing the convoy
                    vehicle_id = convoy.vehicle_id()
                    vehicleLoc = vehicle_id['location']

                    # Drawing the convoy
                    carSurface = pygame.Surface((self.vehicle_length,self.vehicle_width))
                    carSurface.fill(window_params['white'])
                    carRect = carSurface.get_rect()
                    carRect.center = vehicleLoc
                    self.win.blit(carSurface, carRect)
            else:
                vehicle_id = vehicle.vehicle_id()
                vehicleLoc = vehicle_id['location']

                carSurface = pygame.Surface((self.vehicle_length,self.vehicle_width))
                carSurface.fill(window_params['green'])
                carRect = carSurface.get_rect()
                carRect.center = vehicleLoc
                self.win.blit(carSurface, carRect)

    def run_window(self): # vehicle_list passed from Simulation
        frame = 0
        while self.is_running:
             # Drawing the landscape
            self.draw_fixed_objects()

             # If window paused, simulation paused, no road updates
            if self.pause_button.draw(self.win):
                self.is_paused = True
                print("Pause")
            if self.play_button.draw(self.win):
                self.is_paused = False
                print("Resume")
            # if self.record_button.draw(self.win):
            #     self.is_recording = True

            # Event check first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_window()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    self.close_window()

            if not self.is_paused:
                # Updates simulation frame
                vehicle_list, self.is_running = self.sim.update_frame(is_recording=self.is_recording, frame=frame)

                # # Display newly updated frame on Window
                if (len(vehicle_list) != 0):
                    self.refresh_window(vehicle_list=vehicle_list)

                pygame.display.update()
                frame += 1
                self.clock.tick(1./self.ts * self.speed)
        time_taken = time.time() - self.start
        print("Time Taken for 500 vehicle to despawnn: ", time_taken)

        # Saves Data
        self.sim.saving_record()
        print("Saving Record")

    def close_window(self):
        self.is_running = False
        pygame.quit()
        sys.exit()