import pygame
import sys
import time
import math

from common.config import window_params, road_params, simulation_params
from Simulation import SimulationManager
from ACC import Convoy
from Visual import *

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
        self.road_width = self.lanewidth * (self.num_lanes - 1) + self.vehicle_width

        # Loading images
        acc_image = pygame.image.load(window_params["acc_image"])
        shc_image = pygame.image.load(window_params["shc_image"])
        self.acc_image = pygame.transform.scale(acc_image, (self.vehicle_length, self.vehicle_width))
        self.shc_image = pygame.transform.scale(shc_image, (self.vehicle_length, self.vehicle_width))

        self.restart_image = pygame.image.load(window_params["restart_button"])
        self.record_stop_image = pygame.image.load(window_params["record_stop_button"])
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
        self.bg = Background(surface=self.win, screen_width=self.width, screen_height=self.height, start_file=1, end_file=8)
        self.bg.load_road(road_file=window_params['road_image'], x=0, y=410, road_length=self.width, road_width=self.road_width)
        self.bg.load_onramp(road_file=window_params['onramp_image'], x=0, y=355, onramp_length=self.onramp_length*1.35, onramp_width=self.lanewidth+10)
        self.bg.load_signpost(signpost_file = window_params['signpost_image'])
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
        self.record_stop = Button(self.restart_x_loc - 50, self.restart_y_loc, self.record_stop_image, button_scale, button_scale)
        self.restart_button = Button(self.restart_x_loc, self.restart_y_loc, self.restart_image, button_scale, button_scale)

        # Traffic Buttons
        self.global_buttons = pygame.sprite.Group()
        self.traffic_datumn_x, self.traffic_datumn_y = 200, 200

        vehicle_button_info = [
            (self.traffic_datumn_x+200, self.traffic_datumn_y, self.off_image, 0.2, 0.2, "acc_off"),
            (self.traffic_datumn_x+350, self.traffic_datumn_y, self.normal_image, 0.2, 0.2, "acc_logic_normal"),
            (self.traffic_datumn_x+500, self.traffic_datumn_y, self.cautious_image, 0.2, 0.2, "acc_logic_cautious"),
            (self.traffic_datumn_x+200, self.traffic_datumn_y+50, self.normal_image, 0.2, 0.2, "shc_logic_normal"),
            (self.traffic_datumn_x+350, self.traffic_datumn_y+50, self.irrational_image, 0.2, 0.2, "shc_logic_irrational"),
        ]

        for x, y, image, scalex, scaley, button_name in vehicle_button_info:
            button = UserButton(x, y, image, scalex, scaley, button_name)
            self.global_buttons.add(button)

        self.acc_buttons = [self.global_buttons.sprites()[0], self.global_buttons.sprites()[1], self.global_buttons.sprites()[2]]
        self.shc_buttons = [self.global_buttons.sprites()[3], self.global_buttons.sprites()[4]]

        # Road Buttons
        self.road_buttons = []
        road_button_info = [
            (self.traffic_datumn_x+860, self.traffic_datumn_y+60, self.off_image, 0.2, 0.2, "road_closed_off"),
            (self.traffic_datumn_x+1010, self.traffic_datumn_y+60, self.left_image, 0.2, 0.2, "road_closed_left"),
            (self.traffic_datumn_x+860, self.traffic_datumn_y+100, self.middle_image, 0.2, 0.2, "road_closed_middle"),
            (self.traffic_datumn_x+1010, self.traffic_datumn_y+100, self.right_image, 0.2, 0.2, "road_closed_right")
        ]

        for x, y, image, scalex, scaley, button_name in road_button_info:
            button = UserButton(x, y, image, scalex, scaley, button_name)
            self.global_buttons.add(button)
            self.road_buttons.append(button)

        # Create Slider
        self.inflow_slider = Slider((self.traffic_datumn_x+934,self.traffic_datumn_y-25), (258,15), 4/7, 0, 7000, "vehicle_inflow")
        self.onramp_slider = Slider((self.traffic_datumn_x+934,self.traffic_datumn_y), (258,15), 0, 0, 200, "onramp_inflow")
        self.inflow_value = road_params['vehicle_inflow']
        self.onramp_value = road_params['onramp_inflow']

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
        timer_font = pygame.font.Font(None, 32)
        timer_text = timer_font.render(time_str, True, window_params["black"])
        timer_rect = timer_text.get_rect(center=(220, 41))
        self.win.blit(timer_text, timer_rect)

        timer_surface = timer_font.render("Elapsed Time:", True, window_params['black'])
        timer_rect_text = timer_surface.get_rect(center=(85,40))
        self.win.blit(timer_surface, timer_rect_text)

    def draw_refeshed_objects(self):

        # Scrolling bg
        self.bg.draw_bg()
        self.bg.draw_signpost()
        self.bg.draw_road()
        self.inflow_slider.draw_slider(self.win)
        self.onramp_slider.draw_slider(self.win)

        # Draw the recording toggle
        ellipse_rect = pygame.Rect(self.restart_x_loc - 108, 17, 100, 50)
        pygame.draw.ellipse(self.win, window_params['black'], ellipse_rect, 2)

        # Writing Text
        text_list = [
            ("Driving Logics", (self.traffic_datumn_x+350, self.traffic_datumn_y-50), 30),
            ("AI-Controlled Convoy Vehicle", (self.traffic_datumn_x-5, self.traffic_datumn_y+2), 20),
            ("Simulated Human Controlled Vehicle", (self.traffic_datumn_x+20, self.traffic_datumn_y+50), 20),
            ("Traffic Parameters", (self.traffic_datumn_x+930, self.traffic_datumn_y-50), 30),
            ("Road Closure", (self.traffic_datumn_x+740, self.traffic_datumn_y+80), 20),
            ("Inflow", (self.traffic_datumn_x+717, self.traffic_datumn_y-10), 20),
            ("On-ramp Flow", (self.traffic_datumn_x+742, self.traffic_datumn_y+15), 20),
            (f"{self.inflow_value} veh/h", (self.traffic_datumn_x+1110, self.traffic_datumn_y-13), 20),
            (f"{self.onramp_value} veh/h", (self.traffic_datumn_x+1110, self.traffic_datumn_y+13), 20),
        ]

        text_font = pygame.font.Font(None, 20)

        for text, pos, font_size in text_list:
            text_font = pygame.font.Font(None, font_size)
            text_surface = text_font.render(text, True, window_params['black'])
            text_rect = text_surface.get_rect(center=pos)
            self.win.blit(text_surface, text_rect)

        # Draw speed limit

    def refresh_window(self, vehicle_list):

        # Drawing the vehicles
        for vehicle in vehicle_list:

            if isinstance(vehicle, Convoy):
                for convoy in vehicle.convoy_list:
                    # Indexing the convoy
                    vehicle_id = convoy.vehicle_id()
                    vehicle_loc = vehicle_id['location']

                    self.bg.draw_vehicle(self.acc_image, self.vehicle_length, self.vehicle_width, vehicle_loc=vehicle_loc)
            else:
                vehicle_id = vehicle.vehicle_id()
                vehicle_loc = vehicle_id['location']

                self.bg.draw_vehicle(self.shc_image, self.vehicle_length, self.vehicle_width, vehicle_loc=vehicle_loc)

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

            # Background controls
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT] and self.bg.scroll_speed > 0:
                self.bg.scroll_speed -= 5
            if key[pygame.K_RIGHT] and self.bg.scroll_speed < window_params['scroll_limit']:
                self.bg.scroll_speed += 5
            if key[pygame.K_DOWN] and self.bg.scroll_speed > 0:
                self.bg.scroll_speed -= 20
            if key[pygame.K_UP] and self.bg.scroll_speed < window_params['scroll_limit']:
                self.bg.scroll_speed += 20

            # Event check first
            for event in pygame.event.get():
                # self.bg.scroll_speed = 0
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.is_running = False
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
                elif self.inflow_slider.slide_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.inflow_slider.move_slider(pygame.mouse.get_pos())
                    self.inflow_value = self.inflow_slider.slider_value()
                elif self.onramp_slider.slide_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.onramp_slider.move_slider(pygame.mouse.get_pos())
                    self.onramp_value = self.onramp_slider.slider_value()

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