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

class Slider():
    def __init__(self, pos, size, start_factor, min, max, offset, slider_name):
        self.pos = pos
        self.size = size
        self.slider_name = slider_name

        self.left_pos = self.pos[0] - (size[0]//2)
        self.right_pos = self.pos[0] + (size[0]//2)
        self.top_pos = self.pos[1] + (size[1]//2)
        self.bottom_pos = self.pos[1] - (size[1]//2)

        self.height = self.top_pos - self.bottom_pos

        self.min = min
        self.max = max
        self.start_factor = (self.right_pos-self.left_pos)*start_factor
        self.offset = offset

        self.rect = self.left_pos + self.start_factor - self.offset, self.top_pos, self.height*1.2, self.size[1]

        self.slide_rect = pygame.Rect(self.left_pos, self.top_pos, self.size[0], self.size[1])
        self.slider_button = pygame.Rect(self.rect)

    def draw_slider(self, surface):
        radius = self.slider_button.width//2
        pygame.draw.rect(surface, window_params['white'], self.slide_rect)
        pygame.draw.circle(surface, window_params['black'], self.slider_button.center, radius)

    def slider_value(self):
        range = self.right_pos - self.left_pos - 1
        value = self.slider_button.centerx - self.left_pos

        flow_value = int((value/range) * (self.max-self.min) + self.min)

        print("sliderx:", flow_value)

        if self.slider_name == "vehicle_inflow":
            road_params["vehicle_inflow"] = flow_value
        if self.slider_name == "onramp_inflow":
            road_params["onramp_inflow"] = flow_value

        return flow_value

    def move_slider(self, mouse_loc):
        pos = mouse_loc[0]
        if pos < self.left_pos:
            pos = self.left_pos
        if pos > self.right_pos:
            pos = self.right_pos
        self.slider_button.centerx = pos

class Minimap(Slider):
    def __init__(self, pos, size, start_factor, min, max, offset, slider_name):
        super().__init__(pos, size, start_factor, min, max, offset, slider_name)

        self.rect = self.left_pos + self.start_factor - self.offset, self.top_pos, self.height, self.size[1]
        self.road_length_custom = self.size[0]+self.height-5
        self.slider_button = pygame.Rect(self.rect)
        self.slide_rect = pygame.Rect(self.left_pos, self.top_pos, self.road_length_custom, self.size[1])

        self.dx = 0

    def load_map(self):
        miniroad = pygame.image.load(window_params['miniroad']).convert_alpha()
        self.miniroad = pygame.transform.scale(miniroad, (self.road_length_custom, self.size[1]))

    def draw_slider(self, surface):
        # Display text
        font = pygame.font.Font(None, 30)
        text_surface = font.render('Mini-Map', True, window_params['black'])
        text_rect = text_surface.get_rect(center=(self.pos[0]+20, self.top_pos-20))
        surface.blit(text_surface, text_rect)

        # Draw minimap
        surface.blit(self.miniroad, self.slide_rect)

        # Draw sliding panel
        pygame.draw.rect(surface, window_params['black'], self.slider_button, width=2)

    def move_slider(self, mouse_loc):
        pos = mouse_loc[0]
        if pos < self.left_pos + self.height/2:
            pos = self.left_pos + self.height/2
        if pos > self.right_pos - self.height/2:
            pos = self.right_pos - self.height/2
        self.slider_button.centerx = pos

    def scroll_slider(self, increment):

        self.dx += increment

        if self.dx >= window_params['scroll_limit']/self.size[0]:
            self.slider_button.centerx += 1
            self.dx = 0
        if self.dx <= -(window_params['scroll_limit']/self.size[0]):
            self.slider_button.centerx -= 1
            self.dx = 0

class Background():
    def __init__(self, surface, screen_width, screen_height, start_file, end_file):
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_pos = 0

        self.bg_images = []
        for panel in range(start_file, end_file):
            bg_panel = pygame.image.load(f"common/assets/background/{panel}.png").convert_alpha()
            bg_image = pygame.transform.scale(bg_panel, (self.screen_width, self.screen_height))
            self.bg_images.append(bg_image)

        self.bg_width = self.bg_images[0].get_width()

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

    def load_signpost(self, signpost_file):
        signpost_image = pygame.image.load(signpost_file).convert_alpha()

        self.signpost_height = signpost_image.get_height()
        self.signpost_width = signpost_image.get_width()
        self.signpost_image = pygame.transform.scale(signpost_image, (self.signpost_width, self.signpost_height))

    def draw_signpost(self):
        font = pygame.font.Font(None, 32)
        box_y = 340

        for interval in range(1,17):
            box_width, box_height = 200, 100
            box_x = interval*window_params['signpost_interval'] - self.scroll_pos * 5
            # Render text
            text_surface = font.render(f"{str(interval)}km", True, window_params['black'])
            text_width, text_height = text_surface.get_size()

            # Calculate text position
            text_x = box_x + (box_width - text_width) // 2
            text_y = box_y + (box_height - text_height) // 2

            # Draw signpost
            self.surface.blit(self.signpost_image, (box_x - 180, 150))

            # Draw text
            self.surface.blit(text_surface, (text_x, text_y))

            if interval == 16:
                # Draw text
                text_surface = font.render(f"{str(interval)}km", True, window_params['black'])
                self.surface.blit(text_surface, (text_x, text_y))

    def draw_vehicle(self, shc_image, veh_length, veh_width, vehicle_loc):
        car_surface = pygame.Surface((veh_length, veh_width))
        car_rect = car_surface.get_rect()
        car_rect.center = vehicle_loc
        x_pos = car_rect.centerx
        y_pos = car_rect.centery

        self.surface.blit(shc_image, (x_pos - self.scroll_pos * 5, y_pos))

    def draw_road(self):

        for x in range(107):
            self.surface.blit(self.road_image, ((x * self.road_width) - self.scroll_pos * 5, self.road_y))
            if x == 0:
                self.surface.blit(self.onramp_image, ((x * self.onramp_width) - self.scroll_pos * 5, self.onramp_y))

    def draw_bg(self):

        self.draw_bg1(num_img=25,bg_speed=1)

        # Trying to work with multiple backgrounds
        # if flag:
        #     print("Reached")
        #     self.draw_bg2(2,1)

    def draw_bg1(self, num_img, bg_speed):
        for x in range(num_img):
            for img in self.bg_images[:3]:
                x_coord = (x * self.bg_width) - bg_speed * self.scroll_pos
                self.surface.blit(img, (x_coord, 0))
                # print(x_coord)

        # return (x_coord <= 0)

    def draw_bg2(self, num_img, bg_speed):
        for x in range(num_img):
            for img in self.bg_images[-4:]:
                self.surface.blit(img, ((x * self.bg_width) - bg_speed * self.scroll_pos, 0))
                # bg_speed += 0.2


