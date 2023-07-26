import pygame
import os
import pygame
import os

from common.config import window_params

class Window:
    def __init__(self):
        self.width = window_params["window_width"]
        self.height = window_params["window_height"]
        self.fps = window_params['fps']

        self.vehicle_length, = window_params["vehicle_length"]
        self.vehicle_width = window_params["vehicle_width"]
        self.road_length = window_params["road_length"]
        self.lanewidth = window_params["lanewidth"]

        self.road_image = pygame.image.load(window_params["road_image"])
        self.road_border = pygame.image.load(window_params["road_border"])
        self.acc_image = pygame.image.load(window_params["acc_image"])
        self.shc_image = pygame.image.load(window_params["shc_image"])


        # Creating window parameters
        self.win = pygame.display.set_mode(self.width, self.height)
        self.clock = pygame.time.Clock()
        self.is_paused = False
        self.is_recording = False

    def draw_buttons(self):
        # Draw Pause Button
        pygame.draw.rect(self.win, (0, 0, 255), (350, 50, 150, 50))
        font = pygame.font.Font(None, 36)
        pause_text = "Pause"
        if self.is_paused:
            pause_text = "Paused"
        text = font.render(pause_text, True, (255, 255, 255))
        self.win.blit(text, (370, 60))

        # Draw Play Button
        pygame.draw.rect(self.win, (0, 255, 255), (550, 50, 150, 50))
        play_text = "Play"
        if self.is_paused:
            play_text = "Play"
        text = font.render(play_text, True, (255, 255, 255))
        self.win.blit(text, (570, 60))

        # Draw Record Button
        pygame.draw.rect(self.win, (255, 0, 255), (750, 50, 150, 50))
        record_text = "Recording" if self.is_recording else "Record"
        text = font.render(record_text, True, (255, 255, 255))
        self.win.blit(text, (770, 60))

    def handle_button_clicks(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            # Check Pause Button
            if 350 <= mouse_pos[0] <= 500 and 50 <= mouse_pos[1] <= 100:
                if not self.is_paused:
                    self.is_paused = True
                    print("Simulation paused")
            # Check Play Button
            elif 550 <= mouse_pos[0] <= 700 and 50 <= mouse_pos[1] <= 100:
                if self.is_paused:
                    self.is_paused = False
                    print("Simulation unpaused")
            # Check Record Button
            elif 750 <= mouse_pos[0] <= 900 and 50 <= mouse_pos[1] <= 100:
                self.is_recording = not self.is_recording

    def run_window(self):
        acc = pygame.Rect(700, 300, self.vehicle_width, self.vehicle_length)
        shc = pygame.Rect(100, 300, self.vehicle_width, self.vehicle_length)

        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

            self.handle_button_clicks()

            if not self.is_paused:
                # Game logic here
                pass

            self.win.fill(window_params["black"])
            self.draw_buttons()

            pygame.display.update()
            self.clock.tick(self.fps)

        pygame.quit()