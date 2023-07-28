import pygame

from common.config import window_params

class Objects:
    def __init__(self, x, y, image, scale):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (int(self.width * scale), int(self.height * scale)))
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
        self.win = pygame.display.set_mode((self.width, self.height))
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

    def create_vehicle(self):
        self.shc_vehicle = Objects(10, 450, self.shc_image, 0.05)
        self.acc_vehicle = Objects(10, 400, self.acc_image, 0.05)

    def create_objects(self):
        self.create_buttons()
        self.create_vehicle()

    def run_window(self, display_vehicles):

        self.create_objects()

        display_vehicles = display_vehicles

        while self.is_running:
            self.win.fill(window_params["white"])
            self.shc_vehicle.draw(self.win)
            self.acc_vehicle.draw(self.win)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

            self.draw_timer()  # Draw the timer
            if self.pause_button.draw(self.win):
                # Simulation paused
                # TODO
                if not self.is_paused:
                    self.is_paused = True
                    self.last_pause_start = pygame.time.get_ticks()
                    print("Simulation Paused")
            if self.play_button.draw(self.win):
                # Simulation Resumed
                # TODO
                if self.is_paused:
                    self.is_paused = False
                    self.paused_time += pygame.time.get_ticks() - self.last_pause_start
                    print("Simulation Play")
            if self.record_button.draw(self.win):
                # Records Simulation
                # TODO
                print("Simulation Recording")

            pygame.display.update()
            self.clock.tick(self.fps)

        pygame.quit()