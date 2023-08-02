window_params = {
    "window_width": 800,
    "window_height": 300,
    "fps": 120,
    "black": (0,0,0),
    "white": (255,255,255),
    "blue": (0, 0, 255),
    "green": (0,255,0),
    "red": (255,0,0),
    "vehicle_length": 10,
    "vehicle_width": 5,
    "road_image": 'common/assets/road.png',
    "road_border": 'common/assets/road_mask.png',
    "acc_image": 'common/assets/acc.png',
    "shc_image": 'common/assets/shc.png',
    "play_button": 'common/assets/play_button.png',
    "pause_button": 'common/assets/pause_button.png',
    "record_button": 'common/assets/record_button.png'
}

simulation_params = {
    "ts": 0.001,
    "playback_speed": 5, # realtime = 1
    "folderpath": "data",
    "filename": "recordedSimulation"
}

road_params = {
    "toplane_loc": (70,100), #(x, y)
    "road_length": 500,
    "num_lanes": 2,
    "lanewidth": 10,
    "vehicle_inflow": 4000, # 1000 approx 1veh/3.6sec
    "num_convoy_vehicles": 3
}

driving_params = {
    "desired_velocity": 60, # Initially 70
    "safety_threshold": 1.5,
    "max_acceleration": 0.73, # IDM Paper
    "comfortable_deceleration": 1.67, # IDM Paper
    "acceleration_component": 4, # IDM Paper
    "left_bias": 0.3, # MOBIL Paper
    "lane_change_threshold": 0.1, # MOBIL Paper
    "acc_logic": 'normal', # toggle normal/irrational
    "shc_logic": 'normal', # toggle normal/cautious
}

shc_params = {
    "normal": {"safe_headway": 3.1, "speed_variation": 5, "politeness_factor": 0.25},
    "irrational": {"safe_headway": 1.5, "speed_variation": 10, "politeness_factor": 0.15},
}

acc_params = {
    "acc_spawnrate": 0.2, # Init 0.2
    "normal": {"safe_headway": 3.1, "speed_variation": 0, "politeness_factor": 0.5},
    "cautious": {"safe_headway": 4, "speed_variation": 0, "politeness_factor": 0.8},
}

vehicle_models = [shc_params, acc_params]

# default_params = {
#     'max_velocity': 70,
#     'ACC_logic': 'normal',
#     'SHC_logic': 'normal',
#     'vehicle_inflow': 4000,
#     'safety_threshold': 1.5
# }