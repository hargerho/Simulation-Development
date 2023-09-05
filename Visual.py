import pygame

from common.config import window_params, road_params, driving_params, acc_params, simulation_params
from typing import Any, Tuple, List


class Objects:

    """Creating an Object instance
    """

    def __init__(self, x: float, y: float, image: Any, scale_x: float, scale_y: float) -> None:
        """Initializing Object parameters

        Args:
            x (float): x-coordinate
            y (float): y-coordinate
            image (Any): loaded image
            scale_x (float): x-scale
            scale_y (float): y-scale
        """

        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (int(self.width * scale_x), int(self.height * scale_y)))
        self.rect = self.image.get_rect()

        # x,y = topleft corner coord
        self.x, self.y = x, y
        self.rect.topleft = (self.x, self.y)


    def draw(self, surface: pygame.Surface) -> None:

        """Draw the object

        Args:
            surface (pygame.Surface): pygame surface
        """

        center_x = self.rect.x + self.image.get_width()/2
        center_y = self.rect.y + self.image.get_height()/2
        surface.blit(self.image, (center_x, center_y))


    def draw_special(self, surface: pygame.Surface) -> None:

        """Drawing a type of object position about its center

        Args:
            surface (pygame.Surface): pygame surface
        """

        surface.blit(self.image, (self.x, self.y))

class Button(Objects):

    """Creating a Button class, child of Object class
    """

    def __init__ (self, x: float, y: float, image: Any, scale_x: float, scale_y: float) -> None:
        super().__init__(x, y, image, scale_x, scale_y)
        self.image = pygame.transform.scale(image, (int(self.width * scale_x), int(self.height * scale_y)))

        # Setting the interaction flags
        self.clicked = False
        self.prev_state = False
        self.is_selected = False


    def draw(self, surface: pygame.Surface) -> None:

        """Drawing buttons

        Args:
            surface (pygame.Surface): pygame Surface
        """

        flag = False

		#Get mouse position
        mouse_loc = pygame.mouse.get_pos()
        curr_mouse_state = pygame.mouse.get_pressed()[0]

		#Check mouseover and clicked conditions
        if self.rect.collidepoint(mouse_loc) and curr_mouse_state and not self.prev_state:
            self.clicked = not self.clicked
            flag = True

        self.prev_state = curr_mouse_state

        #Draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return flag


class UserButton(pygame.sprite.Sprite):

    """Creating driving logic buttons, child of Sprite class
    """

    def __init__ (self, x: float, y: float, image: Any, scale_x: float, scale_y: float, button_name: str) -> None:
        super().__init__()
        self.button_name = button_name
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale_x), int(height * scale_y)))
        self.rect = self.image.get_rect(center=(x,y))

        # Setting default road closure params
        if self.button_name == "road_closed_off":
            self.is_selected = True
        elif self.button_name == "acc_logic_normal":
            self.is_selected = True
        elif self.button_name == "shc_logic_normal":
            self.is_selected = True
        else:
            self.is_selected = False


    def update(self) -> None:

        """Updating user-interactable parameters
        """

        if self.is_selected:
            pygame.draw.rect(self.image, window_params['black'], self.image.get_rect(), 4)

            # Road closure update
            if self.button_name == "road_closed_off":
                road_params["road_closed"] = None
            elif self.button_name == "road_closed_left":
                road_params["road_closed"] = "left"
            elif self.button_name == "road_closed_middle":
                road_params["road_closed"] = "middle"
            elif self.button_name == "road_closed_right":
                road_params["road_closed"] = "right"

            # ACC driving logic update
            if self.button_name == "acc_logic_normal":
                driving_params["acc_logic"] = "normal"
                acc_params["acc_spawnrate"] = 0.2
            elif self.button_name == "acc_logic_cautious":
                driving_params["acc_logic"] = "cautious"
                acc_params["acc_spawnrate"] = 0.2
            elif self.button_name == "acc_off":
                acc_params["acc_spawnrate"] = 0

            # SHC driving logic update
            if self.button_name == "shc_logic_normal":
                driving_params["shc_logic"] = "normal"
            elif self.button_name == "shc_logic_irrational":
                driving_params["shc_logic"] = "irrational"
        else:
            pygame.draw.rect(self.image, window_params['green'], self.image.get_rect(), 4)


class Slider():

    """Creating a Slider class
    """

    def __init__(self, pos: Tuple[float, float], size: Tuple[float, float], start_factor: float,
                min: float, max: float, offset: float, slider_name: str) -> None:

        """Initializing slider parameters

        Args:
            pos (Tuple[float, float]): slider position
            size (Tuple[float, float]): slider size
            start_factor (float): initial starting value
            min (float): min slider value
            max (float): max slider value
            offset (float): slider button offset
            slider_name (str): name of the slider
        """

        self.pos = pos
        self.size = size
        self.slider_name = slider_name

        # Setting slider boundaries
        self.left_pos = self.pos[0] - (size[0]//2)
        self.right_pos = self.pos[0] + (size[0]//2)
        self.top_pos = self.pos[1] + (size[1]//2)
        self.bottom_pos = self.pos[1] - (size[1]//2)
        self.height = self.top_pos - self.bottom_pos

        # Setting slider value range
        self.min = min
        self.max = max
        self.start_factor = (self.right_pos-self.left_pos)*start_factor
        self.offset = offset

        # Setting slider dimensions
        self.rect = self.left_pos + self.start_factor - self.offset, self.top_pos, self.height*1.2, self.size[1]
        self.slide_rect = pygame.Rect(self.left_pos, self.top_pos, self.size[0], self.size[1])
        self.slider_button = pygame.Rect(self.rect)


    def draw_slider(self, surface: pygame.Surface) -> None:

        """Drawing the slider

        Args:
            surface (pygame.Surface): pygame Surface
        """

        radius = self.slider_button.width//2
        pygame.draw.rect(surface, window_params['white'], self.slide_rect)
        pygame.draw.circle(surface, window_params['black'], self.slider_button.center, radius)


    def slider_value(self) -> float:

        """Gets the value of the slider button position

        Returns:
            float: slider value
        """

        value_range = self.right_pos - self.left_pos - 1
        value = self.slider_button.centerx - self.left_pos

        value = int((value/value_range) * (self.max-self.min) + self.min)

        if self.slider_name == "vehicle_inflow":
            road_params["vehicle_inflow"] = value
        if self.slider_name == "onramp_inflow":
            road_params["onramp_inflow"] = value
        if self.slider_name == "playback_speed":
            simulation_params["playback_speed"] = value

        return value


    def move_slider(self, mouse_loc: Tuple[float, float]) -> None:

        """Updates the slider position depending on the mouse location

        Args:
            mouse_loc (Tuple[float, float]): mouse location on the screen
        """

        pos = mouse_loc[0]

        # Setting left value boundary
        pos = max(pos, self.left_pos)

        # Setting right value boundary
        pos = min(pos, self.right_pos)

        # Positioning the slider
        self.slider_button.centerx = pos


class Minimap(Slider):

    """Creating a Minimap class, child of Slider
    """

    def __init__(self, pos: Tuple[float, float], size: float, start_factor: float, min: float, max: float, offset: float, slider_name: str):
        super().__init__(pos, size, start_factor, min, max, offset, slider_name)

        # Setting minimap dimensions
        self.slider_width = self.height/2
        self.rect = self.left_pos + self.start_factor - self.offset, self.top_pos, self.slider_width, self.size[1]
        self.road_length_custom = self.size[0]+self.slider_width - 2
        self.slider_button = pygame.Rect(self.rect)
        self.slide_rect = pygame.Rect(self.left_pos, self.top_pos, self.road_length_custom, self.size[1])

        # Relative offset
        self.dx = 0


    def load_map(self) -> None:

        """Loads the minimap image
        """

        miniroad = pygame.image.load(window_params['miniroad']).convert_alpha()
        self.miniroad = pygame.transform.scale(miniroad, (self.road_length_custom, self.size[1]))


    def draw_slider(self, surface: pygame.Surface) -> None:

        """Draw the slider

        Args:
            surface (pygame.Surface): pygame Surface
        """

        # Display text
        font = pygame.font.Font(None, 30)
        text_surface = font.render('Mini-Map', True, window_params['black'])
        text_rect = text_surface.get_rect(center=(self.pos[0]+20, self.top_pos-12))
        surface.blit(text_surface, text_rect)

        # Draw minimap
        surface.blit(self.miniroad, self.slide_rect)

        # Draw sliding panel
        pygame.draw.rect(surface, window_params['black'], self.slider_button, width=2)


    def move_slider(self, mouse_loc: Tuple[float, float]) -> None:

        """Moving the slider box based on mouse position

        Args:
            mouse_loc (Tuple[float, float]): mouse position on the screen
        """

        pos = mouse_loc[0]

        # Setting left boundary
        if pos < self.left_pos + self.slider_width/2:
            pos = self.left_pos + self.slider_width/2 - 1

        # Setting right boundary
        if pos > self.right_pos + self.slider_width/2:
            pos = self.right_pos + self.slider_width/2 - 1

        # Positioning slider
        self.slider_button.centerx = pos


    def scroll_slider(self, increment: float) -> None:

        """Moves the slider box in relation to the background

        Args:
            increment (float): background offset
        """

        self.dx += increment

        # Right scroll
        if self.dx >=(window_params['scroll_limit']/self.size[0]):
            self.slider_button.centerx += 1
            self.dx = 0

        # Left scroll
        if self.dx <= -(window_params['scroll_limit']/self.size[0]):
            self.slider_button.centerx -= 1
            self.dx = 0

class Background():

    """Creates a Background class
    """

    def __init__(self, surface: pygame.Surface, screen_width: int, screen_height: int, start_file: str, end_file: str) -> None:

        """Initializing Backgroud params

        Args:
            surface (pygame.Surface): pygame Surfance
            screen_width (int): width of the display screen
            screen_height (int): height of the display screen
            start_file (str): start file of parallax backgorund
            end_file (str): end file of parallax backgorund
        """

        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_pos = 0
        self.onramp_offset = road_params['onramp_offset']

        # Loading parallax background images
        self.bg_images = []
        for panel in range(start_file, end_file):
            bg_panel = pygame.image.load(f"common/assets/background/{panel}.png").convert_alpha()
            bg_image = pygame.transform.scale(bg_panel, (self.screen_width, self.screen_height))
            self.bg_images.append(bg_image)

        self.bg_width = self.bg_images[0].get_width()


    def load_road(self, road_file: Any, x: float, y: float, road_length: float, road_width: int, crop_y: int) -> None:

        """Loading the road image

        Args:
            road_file (Any): road image filename
            x (float): x-coordinate of display road image
            y (float): y-coordinate of display road image
            road_length (float): width of road image
            road_width (int): height of road image
            crop_y (int): cropped road height
        """

        road_image = pygame.image.load(road_file).convert_alpha()
        self.road_image = pygame.transform.scale(road_image, (road_length, road_width))
        self.road_width = self.road_image.get_width()
        self.road_height = self.road_image.get_height()
        self.road_rect = self.road_image.get_rect()
        self.road_y = y

        # Road around onramp
        crop_rect = pygame.Rect(0, 10, self.road_width - 488, self.road_height - 10)
        self.cropped_road = self.road_image.subsurface(crop_rect)
        self.crop_width = self.cropped_road.get_width()
        self.crop_height = self.cropped_road.get_height()
        self.crop_y = crop_y


    def load_onramp(self, road_file: str, x: float, y: float, onramp_length: float, onramp_width: float) -> None:

        """Loading onramp iamge

        Args:
            road_file (str): road image filename
            x (float): x-coordinate of display road image
            y (float): y-coordinate of display road image
            onramp_length (float): width of onramp image
            onramp_width (float): height of onramp image
        """

        onramp_image = pygame.image.load(road_file).convert_alpha()
        self.onramp_height = onramp_image.get_height()
        self.onramp_image = pygame.transform.scale(onramp_image, (onramp_length, onramp_width))
        self.onramp_width = self.onramp_image.get_width()
        self.onramp_rect = self.onramp_image.get_rect()
        self.onramp_x = x
        self.onramp_y = y


    def load_signpost(self, signpost_file: str, speed_limit_file: str) -> None:

        """Loading signposting assets

        Args:
            signpost_file (str): filename of signpost tree image
            speed_limit_file (str): filename of speed limit image
        """

        # Signpost trees
        signpost_image = pygame.image.load(signpost_file).convert_alpha()
        speed_image = pygame.image.load(speed_limit_file).convert_alpha()
        self.signpost_height = signpost_image.get_height()
        self.signpost_width = signpost_image.get_width()
        self.signpost_image = pygame.transform.scale(signpost_image, (self.signpost_width, self.signpost_height))

        # Speed limit image
        self.speed_height = signpost_image.get_height()
        self.speed_width = signpost_image.get_width()
        scalex = 0.15
        scaley = 0.2
        self.speed_image = pygame.transform.scale(speed_image, (int(self.speed_width*scalex), int(self.speed_height*scaley)))


    def draw_signpost(self) -> None:

        """Drawing the signpost at 1km intervals
        """

        font = pygame.font.Font(None, 32)
        box_y = 340

        for interval in range(17):
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

            if interval == 0:
                self.surface.blit(self.speed_image, (box_x + 100, 352))

            # Draw text
            self.surface.blit(text_surface, (text_x, text_y))

            # End of motorway
            if interval == 16:
                # Draw text
                text_surface = font.render(f"{str(interval)}km", True, window_params['black'])
                self.surface.blit(text_surface, (text_x, text_y))


    def draw_metric(self, flow_list: List[float], metric_loc: List[Tuple[int, int]], mini_loc: List[Tuple[int, int]]) -> None:

        """Drawing the metric on the screen

        Args:
            flow_list (List[float]): average flow of at each of the 4 measured locations
            metric_loc (List[Tuple[int, int]]): position of the 4 measured locations
            mini_loc (List[Tuple[int, int]]): position on minimap of the 4 measured locations
        """

        font = pygame.font.Font(None, 30)
        fontmini = pygame.font.Font(None, 15)
        line_length = 65

        for idx, loc in enumerate(metric_loc):
            flow = 0 if flow_list is None or not flow_list else flow_list[idx]

            # Draw near minimap
            text_surface_mini = fontmini.render(f"{flow}", True, window_params['black'])
            text_rect_mini = text_surface_mini.get_rect(center=(mini_loc[idx][0], mini_loc[idx][1]+line_length+10))
            text_surface_mini_fixed = fontmini.render(
                "veh/h", True, window_params['black']
            )
            text_rect_mini_fixed = text_surface_mini.get_rect(center=(mini_loc[idx][0]-3, mini_loc[idx][1]+line_length+18))
            self.surface.blit(text_surface_mini, text_rect_mini)
            self.surface.blit(text_surface_mini_fixed, text_rect_mini_fixed)
            pygame.draw.line(self.surface, window_params['black'], mini_loc[idx], (mini_loc[idx][0], mini_loc[idx][1]+line_length), 1)

            # Draw near the road
            text_surface = font.render(f"{flow} veh/h", True, window_params['black'])
            text_rect = text_surface.get_rect(center=(loc[0] - self.scroll_pos * 5, loc[1]))
            self.surface.blit(text_surface, text_rect)


    def draw_vehicle(self, img: Any, veh_length: float, veh_width: float, vehicle_loc: Tuple[float, float]) -> None:

        """Drawing vehicle on screen

        Args:
            img (Any): vehicle image
            veh_length (float): vehicle length
            veh_width (float): vehicle width
            vehicle_loc (Tuple[float, float]): location of the vehicle on screen
        """

        # Drawing detailed vehicle
        car_surface = pygame.Surface((veh_length, veh_width))
        car_rect = car_surface.get_rect()
        car_rect.center = vehicle_loc
        x_pos = car_rect.centerx
        y_pos = car_rect.centery
        self.surface.blit(img, (x_pos - self.scroll_pos * 5, y_pos))

        # Drawing minivehicle
        scale = 0.3
        mini_surface = pygame.Surface((veh_length*scale, veh_width*scale))
        mini_img = pygame.transform.scale(img,(veh_length*scale*0.3, veh_width*scale*0.8))
        mini_rect = mini_surface.get_rect()
        mini_x = int((vehicle_loc[0]/(800/7)) + 30)
        mini_y = int((vehicle_loc[1]/2.5) - 90)
        mini_rect.center = [mini_x, mini_y]
        x_pos = mini_rect.centerx
        y_pos = mini_rect.centery
        self.surface.blit(mini_img, (x_pos, y_pos))


    def draw_road(self):

        """Drawing the road as part of the background
        """

        for x in range(108):
            if x <= 10:
                self.surface.blit(self.road_image, ((x * self.road_width) - self.scroll_pos * 5, self.road_y))
            # Positioning road before onramp
            if x == 11:
                self.surface.blit(self.road_image, ((x * self.road_width) - self.scroll_pos * 5, self.road_y))
                self.surface.blit(self.road_image, (2500+(x * self.road_width) - self.scroll_pos * 5, self.road_y))
            # Road below onramp
            elif x == 12:
                self.surface.blit(self.road_image, ((x * self.road_width) - self.scroll_pos * 5, self.road_y))
                self.surface.blit(self.road_image, (3500+(x * self.road_width) - self.scroll_pos * 5, self.road_y))
                self.surface.blit(self.cropped_road, (8356+(x * self.crop_width) - self.scroll_pos * 5, self.crop_y))
                self.surface.blit(self.onramp_image, (340+(x * self.onramp_width) - self.scroll_pos * 5, self.onramp_y))
            # Road after onramp
            elif x == 15:
                 self.surface.blit(self.road_image, ((x * self.road_width) - self.scroll_pos * 5, self.road_y))
            # Road after onramp drawn
            elif x > 12 and x < 15:
                pass
            else:
                self.surface.blit(self.road_image, ((x * self.road_width) - self.scroll_pos * 5, self.road_y))


    def draw_bg(self):

        """Drawing the parallax background
        """

        for x in range(25):
            for img in self.bg_images[:3]:
                x_coord = (x * self.bg_width) - 1 * self.scroll_pos
                self.surface.blit(img, (x_coord, 0))