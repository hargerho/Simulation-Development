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
        self.onramp_length = road_params['onramp_length']
        self.num_lanes = road_params['num_lanes']

        # Getting road y-coordinates
        self.toplane_loc = road_params['toplane_loc']
        self.onramp_x = self.toplane_loc[0] + road_params['onramp_offset']
        self.onramp = self.toplane_loc[1]
        self.leftlane = self.toplane_loc[1] + self.lanewidth
        self.middlelane = self.toplane_loc[1] + (self.lanewidth * 2)
        self.rightlane = self.toplane_loc[1] + self.lanewidth * (self.num_lanes - 1)

        # Loading images
        self.road_image = pygame.image.load(window_params["road_image"])
        self.road_border = pygame.image.load(window_params["road_border"])
        self.acc_image = pygame.image.load(window_params["acc_image"])
        self.shc_image = pygame.image.load(window_params["shc_image"])
        self.restart_image = pygame.image.load(window_params["restart_button"])
        # self.restart_stop_image = pygame.image.load(window_params["record_stop_button"])
        self.pause_image = pygame.image.load(window_params["pause_button"])
        self.record_image = pygame.image.load(window_params["record_button"])
        self.play_image = pygame.image.load(window_params["play_button"])

        # Creating window parameters
        self.win = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.start = time.time()

        # Recording params
        self.is_recording = simulation_params['record']
        self.has_recorded = False

        # Pause/Unpause params
        self.is_paused = False
        self.paused_time = 0
        self.last_pause_start = 0
        self.start_time = pygame.time.get_ticks()  # Record the start time of the simulation

    def create_buttons(self):
        self.pause_button = Button(1200, 100, self.pause_image, 0.05, 0.05)
        self.play_button = Button(1250, 100, self.play_image, 0.05, 0.05)

        self.record_button = Button(1300, 100, self.record_image, 0.05, 0.05)
        # self.record_stop = Button(1350, 100, self.restart_stop_image, 0.05, 0.05)

        self.restart_button = Button(1400, 100, self.restart_image, 0.05, 0.05)

    def draw_timer(self, restart):
        if restart:
            self.start_time = pygame.time.get_ticks()
            self.paused_time = 0
            self.last_pause_start = 0

        if self.is_paused:
            elapsed_time = self.paused_time
        else:
            elapsed_time = pygame.time.get_ticks() - self.start_time

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

        # Drawing recording recording toggle
        pygame.draw.ellipse(self.win, window_params["white"], (1293, 94, 90, 40))
        pygame.draw.ellipse(self.win, window_params["black"], (1293, 94, 90, 40), 2)

        # Drawing the onramp
        onrampSurface = pygame.Surface((self.onramp_length, self.lanewidth))
        onrampSurface.fill(window_params['grey'])
        rampRect = onrampSurface.get_rect()
        rampRect.topleft = (self.onramp_x - self.vehicle_length, self.toplane_loc[1] - self.vehicle_width)
        self.win.blit(onrampSurface, rampRect.topleft)

        # Drawing the road
        road_width = self.lanewidth * (self.num_lanes - 1) + self.vehicle_width
        roadSurface = pygame.Surface((self.road_length, road_width))
        roadSurface.fill(window_params['black'])
        roadRect = roadSurface.get_rect()
        roadRect.topleft = (self.toplane_loc[0], self.toplane_loc[1] - self.vehicle_width + self.lanewidth)
        self.win.blit(roadSurface, roadRect.topleft)

        # Overlay the road image
        # road = Objects(rampRect.topleft[0], rampRect.topleft[1], self.road_image, 0.2, 0.136)
        # road.draw_special(self.win)

        # Draw speed limit

        self.create_buttons()

    def refresh_window(self, vehicle_list):

        # Drawing the vehicles
        for vehicle in vehicle_list:

            if isinstance(vehicle, Convoy):
                for convoy in vehicle.convoy_list:
                #     # Indexing the convoy
                    vehicle_id = convoy.vehicle_id()
                    vehicleLoc = vehicle_id['location']

                #     # Drawing the convoy
                    carSurface = pygame.Surface((self.vehicle_length,self.vehicle_width))
                    carSurface.fill(window_params['white'])
                    carRect = carSurface.get_rect()
                    carRect.center = vehicleLoc
                    self.win.blit(carSurface, carRect)
                # Drawing the convoy
                # carSurface = pygame.Surface((3 * window_params['vehicle_length'],self.vehicle_width))
                # carSurface.fill(window_params['white'])
                # carRect = carSurface.get_rect()
                # carRect.center = vehicleLoc
                # self.win.blit(carSurface, carRect)
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
        restarted_time = 0
        while self.is_running:
            restart = False

            self.draw_fixed_objects()

            # Button Presses
            if self.pause_button.draw(self.win):
                self.is_paused = True
                self.paused_time = pygame.time.get_ticks() - self.start_time

            if self.play_button.draw(self.win):
                self.is_paused = False
                self.start_time = pygame.time.get_ticks() - self.paused_time

            if self.restart_button.draw(self.win):
                restart = True

            if not self.is_recording:
                if self.record_button.draw(self.win):
                    self.is_recording = not self.is_recording
                    print(" Start Recording")
            # elif self.record_stop.draw(self.win):
            #     self.is_recording = not self.is_recording
            #     self.has_recorded = True
            #     print("Stopped Recording")

            self.draw_timer(restart=restart)

            # Event check first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    self.is_running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    road_params["vehicle_inflow"] = 0
                    road_params['onramp_inflow'] = 0

            if not self.is_paused:
                # Updates simulation frame
                vehicle_list, _ = self.sim.update_frame(is_recording=self.is_recording, frame=frame, restart=restart)

                # Display newly updated frame on Window
                if (len(vehicle_list) != 0):
                    self.refresh_window(vehicle_list=vehicle_list)

                frame += 1

                pygame.display.update()
                self.clock.tick(1./self.ts * self.speed)

            if restart:
                # Updates simulation frame
                vehicle_list, _ = self.sim.update_frame(is_recording=self.is_recording, frame=frame, restart=restart)

                # Display newly updated frame on Window
                if (len(vehicle_list) != 0):
                    self.refresh_window(vehicle_list=vehicle_list)

                frame = 0

                pygame.display.update()
                self.clock.tick(1./self.ts * self.speed)

        end_time = time.time() - restarted_time
        time_taken = end_time - self.start

        print(f"Time taken to despawn {simulation_params['num_vehicles']} vehicles: {time_taken}")

        # Saves Data
        if simulation_params['testing']:
            self.sim.saving_record()
            print("Saving Record")
        elif self.has_recorded:
            self.sim.saving_record()
            print("Saving Record")

        pygame.quit()
        sys.exit()