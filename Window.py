import pygame
import sys
import time
import math

from common.config import window_params, road_params, simulation_params
from Simulation import SimulationManager
from ACC import Convoy
from Visual import Objects, Button, UserButton, Background

class Window:
    def __init__(self):

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

        # Creating window parameters
        pygame.init()
        self.win = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.start = time.time()

        # Getting road y-coordinates
        self.toplane_loc = road_params['toplane_loc']
        self.onramp = self.toplane_loc[1]
        self.leftlane = self.toplane_loc[1] + self.lanewidth
        self.middlelane = self.toplane_loc[1] + (self.lanewidth * 2)
        self.rightlane = self.toplane_loc[1] + self.lanewidth * (self.num_lanes - 1)

        # Loading images
        acc_image = pygame.image.load(window_params["acc_image"])
        shc_image = pygame.image.load(window_params["shc_image"])
        self.acc_image = pygame.transform.scale(acc_image, (self.vehicle_length, self.vehicle_width))
        self.shc_image = pygame.transform.scale(shc_image, (self.vehicle_length, self.vehicle_width))

        self.restart_image = pygame.image.load(window_params["restart_button"])
        self.restart_stop_image = pygame.image.load(window_params["record_stop_button"])
        self.pause_image = pygame.image.load(window_params["pause_button"])
        self.record_image = pygame.image.load(window_params["record_button"])
        self.play_image = pygame.image.load(window_params["play_button"])

        self.normal_image = pygame.image.load(window_params["normal_button"])
        self.cautious_image = pygame.image.load(window_params["cautious_button"])
        self.irrational_image = pygame.image.load(window_params["irrational_button"])
        self.off_image = pygame.image.load(window_params["off_button"])
        self.left_image = pygame.image.load(window_params["left_button"])
        self.middle_image = pygame.image.load(window_params["middle_button"])
        self.right_image = pygame.image.load(window_params["right_button"])

        # Background params
        self.road_image = pygame.image.load(window_params["road_image"])
        background_image = pygame.image.load(window_params["background_image"])
        self.background_image = pygame.transform.scale(background_image, (self.width + 10, self.height))
        background_list = [self.background_image]
        self.background = Background(surface=self.win, image_list=background_list, screen_width=self.width)

        # Recording params
        self.is_recording = simulation_params['record']
        self.has_recorded = False

        # Pause/Unpause params
        self.is_paused = False
        self.paused_time = 0
        self.last_pause_start = 0
        self.start_time = pygame.time.get_ticks()  # Record the start time of the simulation

        # Setting up the Simulation
        self.is_running = True
        self.sim = SimulationManager() # Create the simulation

    def create_buttons(self):
        # Simulation Buttons
        self.restart_x_loc = 1440
        self.restart_y_loc = 25
        button_scale = 0.065
        self.pause_button = Button(self.restart_x_loc - 200, self.restart_y_loc, self.pause_image, button_scale, button_scale)
        self.play_button = Button(self.restart_x_loc - 150, self.restart_y_loc, self.play_image, button_scale, button_scale)
        self.record_button = Button(self.restart_x_loc - 100, self.restart_y_loc, self.record_image, button_scale, button_scale)
        self.record_stop = Button(self.restart_x_loc - 50, self.restart_y_loc, self.restart_stop_image, button_scale, button_scale)
        self.restart_button = Button(self.restart_x_loc, self.restart_y_loc, self.restart_image, button_scale, button_scale)

        # Traffic Buttons
        self.global_buttons = pygame.sprite.Group()

        vehicle_button_info = [
            (300, 200, self.off_image, 0.2, 0.2, "acc_off"),
            (450, 200, self.normal_image, 0.2, 0.2, "acc_logic_normal"),
            (600, 200, self.cautious_image, 0.2, 0.2, "acc_logic_cautious"),
            (300, 250, self.normal_image, 0.2, 0.2, "shc_logic_normal"),
            (450, 250, self.irrational_image, 0.2, 0.2, "shc_logic_irrational"),
        ]

        for x, y, image, scalex, scaley, button_name in vehicle_button_info:
            button = UserButton(x, y, image, scalex, scaley, button_name)
            self.global_buttons.add(button)

        self.acc_buttons = [self.global_buttons.sprites()[0], self.global_buttons.sprites()[1], self.global_buttons.sprites()[2]]
        self.shc_buttons = [self.global_buttons.sprites()[3], self.global_buttons.sprites()[4]]

        # Road Buttons
        self.road_buttons = []
        road_button_info = [
            (900, 200, self.off_image, 0.2, 0.2, "road_closed_off"),
            (1050, 200, self.left_image, 0.2, 0.2, "road_closed_left"),
            (900, 250, self.middle_image, 0.2, 0.2, "road_closed_middle"),
            (1050, 250, self.right_image, 0.2, 0.2, "road_closed_right")
        ]

        for x, y, image, scalex, scaley, button_name in road_button_info:
            button = UserButton(x, y, image, scalex, scaley, button_name)
            self.global_buttons.add(button)
            self.road_buttons.append(button)

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
        timer_font = pygame.font.Font(None, 30)
        timer_text = timer_font.render(time_str, True, window_params["black"])
        self.win.blit(timer_text, (155,11))

        timer_surface = timer_font.render("Elapsed Time:", True, window_params['black'])
        timer_rect_text = timer_surface.get_rect(center=(80,20))
        self.win.blit(timer_surface, timer_rect_text)

    def draw_refeshed_objects(self):

        self.background.scroll_bg()

        # Draw the recording toggle
        ellipse_rect = pygame.Rect(self.restart_x_loc - 108, 17, 100, 50)
        pygame.draw.ellipse(self.win, window_params['black'], ellipse_rect, 2)

        # Writing Text
        text_list = [
            ("Driving Logics", (450, 150), 30),
            ("AI-Controlled Convoy Vehicle", (100, 200), 20),
            ("Simulated Human Controlled Vehicle", (120, 250), 20),
            ("Traffic Parameters", (980, 150), 30),
            ("Road Closure", (780 ,225), 20),
        ]

        text_font = pygame.font.Font(None, 20)

        for text, pos, font_size in text_list:
            text_font = pygame.font.Font(None, font_size)
            text_surface = text_font.render(text, True, window_params['black'])
            text_rect = text_surface.get_rect(center=pos)
            self.win.blit(text_surface, text_rect)

        # Drawing the onramp
        onrampSurface = pygame.Surface((self.onramp_length, self.lanewidth))
        onrampSurface.fill(window_params['grey'])
        rampRect = onrampSurface.get_rect()
        rampRect.topleft = (self.toplane_loc[0], self.toplane_loc[1] - self.vehicle_width)
        self.win.blit(onrampSurface, rampRect.topleft)

        # Drawing the road
        road_width = self.lanewidth * (self.num_lanes - 1) + self.vehicle_width
        roadSurface = pygame.Surface((self.road_length, road_width))
        roadSurface.fill(window_params['black'])
        roadRect = roadSurface.get_rect()
        roadRect.topleft = (self.toplane_loc[0], self.toplane_loc[1] - self.vehicle_width + self.lanewidth)
        self.win.blit(roadSurface, roadRect.topleft)

        # Overlay the road image
        road = Objects(rampRect.topleft[0], rampRect.topleft[1], self.road_image, 0.2, 0.136)
        road.draw_special(self.win)

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
                    # carSurface.fill(window_params['white'])
                    carRect = carSurface.get_rect()
                    carRect.center = vehicleLoc
                    # self.win.blit(carSurface, carRect)
                    self.win.blit(self.acc_image, carRect)
            else:
                vehicle_id = vehicle.vehicle_id()
                vehicleLoc = vehicle_id['location']

                carSurface = pygame.Surface((self.vehicle_length,self.vehicle_width))
                # carSurface.fill(window_params['green'])
                carRect = carSurface.get_rect()
                carRect.center = vehicleLoc
                # self.win.blit(carSurface, carRect)
                self.win.blit(self.shc_image, carRect)

    def run_window(self):
        frame = 0
        restarted_time = 0
        self.create_buttons()

        while self.is_running:
            restart = False

            self.draw_refeshed_objects()

            # Simulation Button Presses
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
            elif self.record_stop.draw(self.win):
                self.is_recording = not self.is_recording
                self.has_recorded = True
                print("Stopped Recording")

            self.draw_timer(restart=restart)

            # Event check first
            for event in pygame.event.get():
                self.background.scroll_direction, self.background.scroll_direction = 0, 0
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.is_running = False
                    if event.key == pygame.K_RIGHT:
                        self.background.scroll_direction = -1
                        self.background.scroll_speed = 5
                    if event.key == pygame.K_LEFT:
                        self.background.scroll_direction = 1
                        self.background.scroll_speed = 5
                    if event.key == pygame.K_UP:
                        self.background.scroll_direction = -1
                        self.background.scroll_speed = 20
                    if event.key == pygame.K_DOWN:
                        self.background.scroll_direction = 1
                        self.background.scroll_speed = 20
                    # if event.key == pygame.K_RIGHT:
                    #     self.background.scroll(-5, 0)
                    # if event.key == pygame.K_LEFT:
                    #     self.background.scroll(0, -5)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        for button in self.global_buttons:
                            if button.rect.collidepoint(event.pos):
                                if button in self.acc_buttons:
                                    for acc_button in self.acc_buttons:
                                        acc_button.is_selected = (acc_button == button)
                                elif button in self.shc_buttons:
                                    for shc_button in self.shc_buttons:
                                        shc_button.is_selected = (shc_button == button)
                                elif button in self.road_buttons:
                                    for road_button in self.road_buttons:
                                        road_button.is_selected = (road_button == button)

            self.global_buttons.update()
            self.global_buttons.draw(self.win)

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