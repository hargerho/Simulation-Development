window_params = {
    "window_width": 1300,
    "window_height": 500,
    "fps": 120,
    "black": (0,0,0),
    "white": (255,255,255),
    "blue": (0, 0, 255),
    "green": (0,255,0),
    "grey": (128, 128, 128),
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
    "ts": 1/60, # was 0.001  testing: 1/60
    "playback_speed": 8, # realtime = 1
    "folderpath": "data",
    "filename": "recordedSimulation"
}

road_params = {
    "toplane_loc": (0,100), #(x, y)
    "road_length": 1200,
    "onramp_length": 600,
    "num_lanes": 4, # including an onramp
    "lanewidth": 10,
    "vehicle_inflow": 8000, # 1000 approx 1veh/3.6sec testing: 10000
    "onramp_inflow": 1000,
    "onramp_switch": False, # Toggles onramp on/off
    "num_convoy_vehicles": 3
}

driving_params = {
    "desired_velocity": 20, # Initially 70 testing:16.6
    "safety_threshold": 20, # estimation
    "max_acceleration": 50, # IDM Paper # was 0.73
    "comfortable_deceleration": 4.61, # IDM Paper # was 1.67
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
    "acc_spawnrate": 1, # Init 0.2
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