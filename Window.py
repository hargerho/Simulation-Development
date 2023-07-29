import pygame
import sys

from common.config import window_params, road_params
from Simulation import Simulation

class Objects:
    def __init__(self, x, y, image, scale):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (window_params['vehicle_length'], window_params['vehicle_width']))
        # self.image = pygame.transform.scale(image, (int(self.width * scale), int(self.height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # x,y = topleft corner coord

    def draw(self, surface):
        center_x = self.rect.x + self.image.get_width()/2
        center_y = self.rect.y + self.image.get_height()/2
        surface.blit(self.image, (center_x, center_y))

class Button(Objects):
    def __init__ (self, x, y, image, scale):
        super().__init__(x, y, image, scale)
        self.clicked = False

    def draw(self, surface):
        flag = False
		#get mouse position
        mouse_loc = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
        if self.rect.collidepoint(mouse_loc):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                flag = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return flag

class Window:
    def __init__(self):
        pygame.init()
        # self.sim = Simulation()
        self.width = window_params["window_width"]
        self.height = window_params["window_height"]
        self.fps = window_params['fps']

        self.vehicle_length = window_params["vehicle_length"]
        self.vehicle_width = window_params["vehicle_width"]
        self.road_length = window_params["road_length"]
        self.lanewidth = window_params["lanewidth"]

        # Loading images
        self.road_image = pygame.image.load(window_params["road_image"])
        self.road_border = pygame.image.load(window_params["road_border"])
        self.acc_image = pygame.image.load(window_params["acc_image"])
        self.shc_image = pygame.image.load(window_params["shc_image"])
        self.play_image = pygame.image.load(window_params["play_button"])
        self.pause_image = pygame.image.load(window_params["pause_button"])
        self.record_image = pygame.image.load(window_params["record_button"])

        # Creating window parameters
        self.win = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.is_paused = False
        self.is_recording = False

        self.paused_time = 0
        self.last_pause_start = 0
        self.start_time = pygame.time.get_ticks()  # Record the start time of the simulation

        self.is_running = True

    def create_buttons(self):
        self.pause_button = Button(750, 10, self.pause_image, 0.05)
        self.play_button = Button(800, 10, self.play_image, 0.05)
        self.record_button = Button(850, 10, self.record_image, 0.05)

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

    def create_vehicle(self, shc_x, shc_y, acc_x, acc_y):
        self.shc_vehicle = Objects(shc_x, shc_y, self.shc_image, 0.05)
        self.acc_vehicle = Objects(acc_x, acc_y, self.acc_image, 0.05)

    def run_window(self, filteredDict):

        self.create_buttons()

        for frame, vehicleList in filteredDict.items():
            # Event check first
            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                        sys.exit()

            # Fill background
            self.win.fill(window_params["white"])

            # Drawing the road
            road_width = road_params['lanewidth'] * road_params['num_lanes'] + 2
            roadSurface = pygame.Surface((road_params['road_length'], road_width))
            roadSurface.fill(window_params['black'])
            roadRect = roadSurface.get_rect()
            roadRect.topleft = road_params['toplane_loc']
            self.win.blit(roadSurface, roadRect.topleft)

            # Drawing the vehicles
            # Iterating through the value-list per frame
            for vehicle in vehicleList:
                vehicleType = vehicle['vehicle_type']
                vehicleLoc = vehicle['location']
                # vehicle_x = vehicleLoc[0]
                # vehicle_y = vehicleLoc[1]

                # if vehicleType == 'shc':
                #     self.shc_vehicle = Objects(vehicle_x, vehicle_y, self.shc_image, 0.05)
                #     self.shc_vehicle.draw(self.win)
                # else:
                #     self.acc_vehicle = Objects(vehicle_x, vehicle_y, self.acc_image, 0.05)
                #     self.acc_vehicle.draw(self.win)
                if vehicleType == 'shc':
                    carSurface = pygame.Surface((10,5))
                    carSurface.fill(window_params['green'])
                    carRect = carSurface.get_rect()
                    carRect.center = vehicleLoc
                    self.win.blit(carSurface, carRect)
                else:
                    carSurface = pygame.Surface((10,5))
                    carSurface.fill(window_params['white'])
                    carRect = carSurface.get_rect()
                    carRect.center = vehicleLoc
                    self.win.blit(carSurface, carRect)

                pygame.display.update()
                self.clock.tick(120)

        pygame.quit()