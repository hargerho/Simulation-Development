import pygame
import math
from common.config import window_params, road_params, driving_params, acc_params

class Objects:
    def __init__(self, x, y, image, scale_x, scale_y):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (int(self.width * scale_x), int(self.height * scale_y)))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)

        # x,y = topleft corner coord

    def draw(self, surface):
        center_x = self.rect.x + self.image.get_width()/2
        center_y = self.rect.y + self.image.get_height()/2
        surface.blit(self.image, (center_x, center_y))

    def draw_special(self, surface):
        surface.blit(self.image, (self.x, self.y))

class Button(Objects):
    def __init__ (self, x, y, image, scale_x, scale_y):
        super().__init__(x, y, image, scale_x, scale_y)
        self.image = pygame.transform.scale(image, (int(self.width * scale_x), int(self.height * scale_y)))
        self.clicked = False
        self.prev_state = False
        self.is_selected = False

    def draw(self, surface):
        flag = False
		#get mouse position
        mouse_loc = pygame.mouse.get_pos()
        curr_mouse_state = pygame.mouse.get_pressed()[0]

		#check mouseover and clicked conditions
        if self.rect.collidepoint(mouse_loc) and curr_mouse_state and not self.prev_state:
            self.clicked = not self.clicked
            flag = True

        self.prev_state = curr_mouse_state

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return flag

class UserButton(pygame.sprite.Sprite):
    def __init__ (self, x, y, image, scale_x, scale_y, button_name):
        super().__init__()
        self.button_name = button_name
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale_x), int(height * scale_y)))
        self.rect = self.image.get_rect(center=(x,y))
        self.is_selected = False

    def update(self):  # sourcery skip: switch
        if self.is_selected:
            pygame.draw.rect(self.image, window_params['black'], self.image.get_rect(), 4)
            if self.button_name == "road_closed_off":
                road_params["road_closed"] = 'off'
            elif self.button_name == "road_closed_left":
                road_params["road_closed"] = 'left'
            elif self.button_name == "road_closed_middle":
                road_params["road_closed"] = 'middle'
            elif self.button_name == "road_closed_right":
                road_params["road_closed"] = 'right'

            if self.button_name == "acc_logic_normal":
                driving_params["acc_logic"] = 'normal'
                acc_params["acc_spawnrate"] = 0.2
            elif self.button_name == "acc_logic_cautious":
                driving_params["acc_logic"] = 'cautious'
                acc_params["acc_spawnrate"] = 0.2
            elif self.button_name == "acc_off":
                acc_params["acc_spawnrate"] = 0

            if self.button_name == "shc_logic_normal":
                driving_params["shc_logic"] = 'normal'
            elif self.button_name == "shc_logic_irrational":
                driving_params["shc_logic"] = 'irrational'
        else:
            pygame.draw.rect(self.image, window_params['green'], self.image.get_rect(), 4)

class Background():
    def __init__(self, surface, screen_width, screen_height, start_file, end_file):
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_speed = 0

        self.bg_images = []
        for panel in range(start_file, end_file):
            bg_panel = pygame.image.load(f"common/assets/background/{panel}.png").convert_alpha()
            bg_image = pygame.transform.scale(bg_panel, (self.screen_width, self.screen_height))
            self.bg_images.append(bg_image)

        self.bg_width = self.bg_images[0].get_width()

        print(len(self.bg_images))

    def load_road(self, road_file, x, y, road_length, road_width):
        road_image = pygame.image.load(road_file).convert_alpha()

        self.road_image = pygame.transform.scale(road_image, (road_length, road_width))
        self.road_width = self.road_image.get_width()
        self.road_rect = self.road_image.get_rect()
        self.road_y = y

    def load_onramp(self, road_file, x, y, onramp_length, onramp_width):
        onramp_image = pygame.image.load(road_file).convert_alpha()

        self.onramp_height = onramp_image.get_height()

        self.onramp_image = pygame.transform.scale(onramp_image, (onramp_length, onramp_width))
        self.onramp_width = self.onramp_image.get_width()
        self.onramp_rect = self.onramp_image.get_rect()
        self.onramp_x = x
        self.onramp_y = y

    def draw_vehicle(self, shc_image, veh_length, veh_width, vehicle_loc):
        car_surface = pygame.Surface((veh_length, veh_width))
        car_rect = car_surface.get_rect()
        car_rect.center = vehicle_loc
        x_pos = car_rect.centerx
        y_pos = car_rect.centery

        self.surface.blit(shc_image, (x_pos - self.scroll_speed * 5, y_pos))

    def draw_road(self):

        for x in range(6):
            self.surface.blit(self.road_image, ((x * self.road_width) - self.scroll_speed * 5, self.road_y))
            if x == 0:
                self.surface.blit(self.onramp_image, ((x * self.onramp_width) - self.scroll_speed * 5, self.onramp_y))

    def draw_bg(self):

        self.draw_bg1(num_img=4,bg_speed=1)

        # Trying to work with multiple backgrounds
        # if flag:
        #     print("Reached")
        #     self.draw_bg2(2,1)


    def draw_bg1(self, num_img, bg_speed):
        for x in range(num_img):
            for img in self.bg_images[:3]:
                x_coord = (x * self.bg_width) - bg_speed * self.scroll_speed
                self.surface.blit(img, (x_coord, 0))
                # print(x_coord)

        # return (x_coord <= 0)

    def draw_bg2(self, num_img, bg_speed):
        for x in range(num_img):
            for img in self.bg_images[-4:]:
                self.surface.blit(img, ((x * self.bg_width) - bg_speed * self.scroll_speed, 0))
                # bg_speed += 0.2


