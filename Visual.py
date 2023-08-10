import pygame
from common.config import window_params, road_params, simulation_params

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
        self.clicked = False
        self.prev_state = False

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