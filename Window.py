import sys
import time
import pygame

from Visual import *
from ACC import Convoy
from Simulation import SimulationManager
from statistics import harmonic_mean
from common.config import window_params, road_params, simulation_params

SCALE = 10

class Window:

    """Creating a WIndow class display
    """

    def __init__(self) -> None:

        """Initializing the Window parameters
        """

        # Creating the window
        self.width = window_params["window_width"]
        self.height = window_params["window_height"]
        self.ts = simulation_params["ts"]

        self.vehicle_length = window_params["vehicle_length"]
        self.vehicle_width = window_params["vehicle_width"]
        self.road_length = road_params["road_length"]
        self.lanewidth = road_params["lanewidth"]
        self.onramp_length = road_params['onramp_length']
        self.num_lanes = road_params['num_lanes']

        # Creating window parameters
        pygame.init()
        self.win = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.start = time.time()

        # Getting road y-coordinates
        self.toplane_loc = road_params['toplane_loc']
        self.onramp_x = self.toplane_loc[0] + road_params['onramp_offset']
        self.onramp = self.toplane_loc[1]
        self.leftlane = self.toplane_loc[1] + self.lanewidth
        self.middlelane = self.toplane_loc[1] + (self.lanewidth * 2)
        self.rightlane = self.toplane_loc[1] + self.lanewidth * (self.num_lanes - 1)
        self.road_width = self.lanewidth * (self.num_lanes - 1) + self.vehicle_width

        # Loading vehicle images
        acc_image = pygame.image.load(window_params["acc_image"])
        shc_image = pygame.image.load(window_params["shc_image"])
        self.acc_image = pygame.transform.scale(acc_image, (self.vehicle_length, self.vehicle_width))
        self.shc_image = pygame.transform.scale(shc_image, (self.vehicle_length, self.vehicle_width))

        # Loading simulation control button images
        self.restart_image = pygame.image.load(window_params["restart_button"])
        self.record_stop_image = pygame.image.load(window_params["record_stop_button"])
        self.pause_image = pygame.image.load(window_params["pause_button"])
        self.record_image = pygame.image.load(window_params["record_button"])
        self.play_image = pygame.image.load(window_params["play_button"])

        # Loading driving control button images
        self.normal_image = pygame.image.load(window_params["normal_button"])
        self.cautious_image = pygame.image.load(window_params["cautious_button"])
        self.irrational_image = pygame.image.load(window_params["irrational_button"])

        # Loading road closure button images
        self.off_image = pygame.image.load(window_params["off_button"])
        self.left_image = pygame.image.load(window_params["left_button"])
        self.middle_image = pygame.image.load(window_params["middle_button"])
        self.right_image = pygame.image.load(window_params["right_button"])

        # Background params
        self.road_image = pygame.image.load(window_params["road_image"])
        self.bg = Background(surface=self.win, screen_width=self.width, screen_height=self.height, start_file=1, end_file=8)
        self.bg.load_road(road_file=window_params['road_image'], x=0, y=410, road_length=self.width, road_width=self.road_width, crop_y=420)
        self.bg.load_onramp(road_file=window_params['onramp_image'], x=0, y=360, onramp_length=self.onramp_length*1.2, onramp_width=self.lanewidth+10)
        self.bg.load_signpost(signpost_file = window_params['signpost_image'], speed_limit_file = window_params['speed_limit'])

        # Minimap
        self.minimap = Minimap(pos=(self.width/2-20,28), size=(1400,70), start_factor=0, min=0, max=31783, offset=0, slider_name='minimap')
        self.minimap.load_map()

        # Recording params
        self.is_recording = simulation_params['record']
        self.has_recorded = False

        # Pause/Unpause params
        self.is_paused = False
        self.paused_time = 0
        self.start_time = pygame.time.get_ticks()  # Record the start time of the simulation

        # Creating Real Time Metric Display
        self.realtime_flow = [[], [], [], []]
        self.mean_flow = []
        self.metric_list = [(10000,390), (30000,390), (80000,390), (159980, 390)] # 1st, 2nd, middle, last
        self.miniloc_list = [(128,75), (306,75), (745,75), (1438, 75)] # 1st, 2nd, middle, last

        # Setting up the Simulation
        self.is_running = True
        self.sim = SimulationManager() # Create the simulation


    def create_buttons(self) -> None:

        """Creating Button instances
        """

        # Simulation buttons
        self.restart_x_loc = 1440
        self.restart_y_loc = 25
        button_scale = 0.065
        self.pause_button = Button(self.restart_x_loc - 192, self.restart_y_loc, self.pause_image, button_scale, button_scale)
        self.play_button = Button(self.restart_x_loc - 150, self.restart_y_loc, self.play_image, button_scale, button_scale)
        self.record_button = Button(self.restart_x_loc - 100, self.restart_y_loc, self.record_image, button_scale, button_scale)
        self.record_stop = Button(self.restart_x_loc - 50, self.restart_y_loc, self.record_stop_image, button_scale, button_scale)
        self.restart_button = Button(self.restart_x_loc, self.restart_y_loc, self.restart_image, button_scale, button_scale)

        # Traffic buttons
        self.global_buttons = pygame.sprite.Group()
        self.traffic_datumn_x, self.traffic_datumn_y = 200, 210

        # Driving logic buttons
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

        # Toggle driving logics
        self.acc_buttons = [self.global_buttons.sprites()[0], self.global_buttons.sprites()[1], self.global_buttons.sprites()[2]]
        self.shc_buttons = [self.global_buttons.sprites()[3], self.global_buttons.sprites()[4]]

        # Road closure buttons
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

        # Create Sliders
        self.inflow_slider = Slider((self.traffic_datumn_x+934,self.traffic_datumn_y-25), (258,15), 4/7, 0, 7000, 10, "vehicle_inflow")
        self.onramp_slider = Slider((self.traffic_datumn_x+934,self.traffic_datumn_y), (258,15), 0, 0, 200, 10, "onramp_inflow")
        self.speed_slider = Slider((158, 43), (80,10), 2/7, 1, 7, 5, "playback_speed")
        self.inflow_value = road_params['vehicle_inflow']
        self.onramp_value = road_params['onramp_inflow']


    def draw_timer(self, restart: bool) -> None:

        """Drawing the timer display

        Args:
            restart (bool): restart flag
        """

        if restart:
            self.start_time = pygame.time.get_ticks()
            self.paused_time = 0

        if self.is_paused:
            elapsed_time = self.paused_time
        else:
            elapsed_time = pygame.time.get_ticks() - self.start_time

        # Timer conversion
        milliseconds = int((elapsed_time % 1000) // 10)
        seconds = int((elapsed_time // 1000) % 60)
        minutes = int((elapsed_time // 60000) % 60)
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        timer_font = pygame.font.Font(None, 32)
        timer_text = timer_font.render(time_str, True, window_params["black"])
        timer_rect = timer_text.get_rect(center=(210, 27))
        self.win.blit(timer_text, timer_rect)

        # Timer text
        timer_surface = timer_font.render("Elapsed Time:", True, window_params['black'])
        timer_rect_text = timer_surface.get_rect(center=(85,25))
        self.win.blit(timer_surface, timer_rect_text)


    def draw_refeshed_objects(self) -> None:

        """Drawing objects that are refreshed every frame
        """

        # Scrolling bg
        self.bg.draw_bg()
        self.bg.draw_signpost()
        self.bg.draw_road()

        # Drawing minimap
        self.minimap.draw_slider(self.win)

        # Draw metrics
        self.bg.draw_metric(flow_list=self.mean_flow, metric_loc=self.metric_list, mini_loc=self.miniloc_list)

        # Drawing sliders
        self.inflow_slider.draw_slider(self.win)
        self.onramp_slider.draw_slider(self.win)
        self.speed_slider.draw_slider(self.win)

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
            ("Playback Speed", (60,52), 20),
            (f"{simulation_params['playback_speed']} times", (230,52), 20),
        ]

        text_font = pygame.font.Font(None, 20)

        for text, pos, font_size in text_list:
            text_font = pygame.font.Font(None, font_size)
            text_surface = text_font.render(text, True, window_params['black'])
            text_rect = text_surface.get_rect(center=pos)
            self.win.blit(text_surface, text_rect)


    def speed_conversion(self, value: float) -> float:

        """Converts pixel/s to km/h

        Args:
            value (float): pixel/s  speed

        Returns:
            float: km/h speed
        """

        # 1m = 10px
        return float(value * (3600/(SCALE*1000)))


    def density_conversion(self, value: float, dist: float) -> float:

        """Computes vehicle density

        Args:
            value (float): pixel length
            dist (float): km conversion

        Returns:
            float: number of vehicles/km
        """

        # Interval of 400 px
        # 1m = 10px
        return float(value * ((SCALE*1000)/dist))


    def length_conversion(self, value: float) -> float:

        """convert pixel to metres

        Args:
            value (float): pixel length

        Returns:
            float: scaled length in metres
        """

        return value * SCALE


    def assign_section(self, loc: Tuple[float, float], speed: float, vehicle_metrics: List[List[float]]) -> None:

        """Assigning vehicles to the 4 measured section and get their speed

        Args:
            loc (Tuple[float, float]): vehicle position
            speed (float): vehicle speed
            vehicle_metrics (List[List[float]]): collated vehicle speeds in the sections
        """

        for idx, metric_loc in enumerate(self.metric_list):
            # Vehicles within 1km of the measured location
            if loc[0] >= metric_loc[0] - self.length_conversion(500) and loc[0] <= metric_loc[0] + self.length_conversion(500):
                vehicle_metrics[idx].append((speed, self.length_conversion(1000)))


    def compute_metrics(self, vehicle_metric: List[List[float]], realtime_metrics: List[List[float]]) -> List[List[float]]:
        """Computing the realtime metrics

        Args:
            vehicle_metric (List[List[float]]): collated vehicle speeds in the sections of each frame
            realtime_metrics (List[List[float]]): computed traffic flow in each section of each frame

        Returns:
            List[List[float]]: updated computed traffic flow in each section of each frame
        """

        for idx, sections in enumerate(vehicle_metric):
            num_vehicles = len(sections)
            if num_vehicles > 0:
                space_mean_speed = harmonic_mean([speed[0] for speed in sections])
                flow = int(self.density_conversion(num_vehicles,sections[0][1]) * self.speed_conversion(space_mean_speed))
                realtime_metrics[idx].append(flow)
            else:
                realtime_metrics[idx] = []

        return realtime_metrics


    def average_metrics(self, realtime_metrics: List[List[float]]) -> List[float]:

        """Averaged metrics for each section

        Args:
            realtime_metrics (List[List[float]]): computed traffic flow in each section of each frame

        Returns:
            List[float]: averaged traffic flow of 10 frames
        """

        mean_flow = []

        for section in realtime_metrics:
            section_mean = int(sum(section) / len(section)) if len(section) > 0 else 0
            mean_flow.append(section_mean)

        return mean_flow


    def refresh_window(self, vehicle_list: List[Any], frame: int) -> None:

        """Refreshes window per frame

        Args:
            vehicle_list (List[Any]): list of Vehicle or Convoy instances
            frame (int): frame counter
        """

        vehicle_metrics = [[], [], [], []]

        # Drawing the vehicles
        for vehicle in vehicle_list:

            if isinstance(vehicle, Convoy):
                for convoy in vehicle.convoy_list:
                    # Indexing the convoy
                    vehicle_id = convoy.vehicle_id()
                    self.assign_section(loc=vehicle_id['location'], speed=vehicle_id['speed'], vehicle_metrics=vehicle_metrics)
                    self.bg.draw_vehicle(self.acc_image, self.vehicle_length, self.vehicle_width, vehicle_loc=vehicle_id['location'])

            else:
                vehicle_id = vehicle.vehicle_id()
                self.assign_section(loc=vehicle_id['location'], speed=vehicle_id['speed'], vehicle_metrics=vehicle_metrics)
                self.bg.draw_vehicle(self.shc_image, self.vehicle_length, self.vehicle_width, vehicle_loc=vehicle_id['location'])

        self.realtime_flow = self.compute_metrics(vehicle_metrics, self.realtime_flow)

        # Average for every 10 frames
        if (frame%10 == 0):
            self.mean_flow = self.average_metrics(realtime_metrics=self.realtime_flow)


    def out_bound_check(self, loc: float, diff: float) -> float:

        """Checks if the background reaches out of bounds

        Args:
            loc (float): background offset
            diff (float): out of bound limit

        Returns:
            float: value to keep background within display range
        """

        tmp = loc - diff
        return max(tmp, 0)


    def sim_button_press(self) -> bool:

        """Checking for simulation control button press

        Returns:
            bool: restart flag
        """

        if self.pause_button.draw(self.win):
            self.is_paused = True
            self.paused_time = pygame.time.get_ticks() - self.start_time

        if self.play_button.draw(self.win):
            self.is_paused = False
            self.start_time = pygame.time.get_ticks() - self.paused_time

        restart = bool(self.restart_button.draw(self.win))

        if not self.is_recording:
            if self.record_button.draw(self.win):
                self.is_recording = not self.is_recording
                print(" Start Recording")
        elif self.record_stop.draw(self.win):
            self.is_recording = not self.is_recording
            self.has_recorded = True
            print("Stopped Recording")

        return restart


    def background_controls(self) -> None:

        """Checks for background control keypress and mouse position
        """

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.bg.scroll_pos > 0:
            self.bg.scroll_pos -= 5
            self.minimap.scroll_slider(-5)
        if key[pygame.K_RIGHT] and self.bg.scroll_pos < window_params['scroll_limit']:
            self.bg.scroll_pos += 5
            self.minimap.scroll_slider(5)
        if key[pygame.K_DOWN] and self.bg.scroll_pos > 0:
            self.bg.scroll_pos = self.out_bound_check(self.bg.scroll_pos, 20)
            self.minimap.scroll_slider(-20)
        if key[pygame.K_UP] and self.bg.scroll_pos < window_params['scroll_limit']:
            self.bg.scroll_pos += 20
            self.minimap.scroll_slider(20)
        if self.minimap.slide_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.minimap.move_slider(pygame.mouse.get_pos())
            x = self.minimap.slider_value()
            self.bg.scroll_pos = x - 385


    def run_window(self) -> None:

        """Execute the window display
        """

        clock = pygame.time.Clock()
        frame = 0
        self.minimap_value = 0
        self.create_buttons()

        while self.is_running:
            restart = False

            # Background controls
            self.background_controls()

            self.draw_refeshed_objects()

            # Road closure and logic buttons buttons
            self.global_buttons.draw(self.win)
            self.global_buttons.update()

            # Simulation Button Presses
            restart = self.sim_button_press()
            self.draw_timer(restart=restart)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.is_running = False
                    if event.key == pygame.K_d:
                        simulation_params['playback_speed'] = min(simulation_params['playback_speed'] + 1, 7)
                    if event.key == pygame.K_a:
                        simulation_params['playback_speed'] = max(1, simulation_params['playback_speed'] - 1)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        # Checking for logic button press
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
                # Checking for slider interactions
                elif self.inflow_slider.slide_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.inflow_slider.move_slider(pygame.mouse.get_pos())
                    self.inflow_value = self.inflow_slider.slider_value()
                elif self.onramp_slider.slide_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.onramp_slider.move_slider(pygame.mouse.get_pos())
                    self.onramp_value = self.onramp_slider.slider_value()
                elif self.speed_slider.slide_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.speed_slider.move_slider(pygame.mouse.get_pos())
                    simulation_params['playback_speed'] = self.speed_slider.slider_value()

            if not self.is_paused:
                # Updates simulation frame
                vehicle_list, _ = self.sim.update_frame(is_recording=self.is_recording, frame=frame, restart=restart)

                # Display newly updated frame on Window
                self.refresh_window(vehicle_list=vehicle_list, frame=frame)
                frame += 1
                pygame.display.update()
                clock.tick(1./self.ts * simulation_params['playback_speed'])
            else:
                self.refresh_window(vehicle_list=vehicle_list, frame=frame)
                pygame.display.update()

            # Resets simulation parameters
            if restart:
                frame = 0
                self.realtime_flow = [[], [], [], []]
                vehicle_list, _ = self.sim.update_frame(is_recording=self.is_recording, frame=frame, restart=restart)
                self.refresh_window(vehicle_list=vehicle_list, frame=frame)
                pygame.display.update()
                clock.tick(1./self.ts * simulation_params['playback_speed'])

        # Saves Data
        if simulation_params['testing']:
            self.sim.saving_record()
            print("Saving Record")
        elif self.has_recorded:
            self.sim.saving_record()
            print("Saving Record")

        pygame.quit()
        sys.exit()