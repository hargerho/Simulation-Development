import pygame
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
    def __init__(self, surface):
        self.surface = surface
        self.panels = []

    def load_bg(self, file):
        return pygame.image.load(file)

    def bg_panels(self, image_list):
        if type(image_list) is str:
            self.panels = [[self.load_bg(image_list)]]
        elif type(image_list[0]) is str:
            self.panels = [[self.load_bg(i) for i in image_list]]
        else:
            self.panels = [[self.load_bg(i) for i in row] for row in image_list]
        self.camera_x = 0
        self.camera_y = 0
        self.bg_width = self.panels[0][0].get_width()
        self.bg_height = self.panels[0][0].get_height()
        self.surface.blit(self.panels[0][0], (0,0))

    def scroll(self, x, y):
        self.camera_x -= x
        self.camera_y -= y
        col = (self.camera_x % (self.bg_width * len(self.panels[0]))) // self.bg_width
        row = (self.camera_y % (self.bg_height * len(self.panels))) // self.bg_height
        col2 = ((self.camera_x + self.bg_width) % (self.bg_width * len(self.panels[0]))) // self.bg_width
        row2 = ((self.camera_y + self.bg_height) % (self.bg_height * len(self.panels))) // self.bg_height
        xOff = (0 - self.camera_x % self.bg_width)
        yOff = (0 - self.camera_y % self.bg_height)

        self.surface.blit(self.panels[row][col], [xOff, yOff])
        self.surface.blit(self.panels[row][col2], [xOff + self.bg_width, yOff])
        self.surface.blit(self.panels[row2][col], [xOff, yOff + self.bg_height])
        self.surface.blit(self.panels[row2][col2], [xOff + self.bg_width, yOff + self.bg_height])