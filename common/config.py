import os

window_params = {
    "window_width": 900,
    "window_height": 500,
    "fps": 30,
    "black": (0,0,0),
    "white": (255,255,255),
    "vehicle_length": 80,
    "vehicle_width": 40,
    "road_length": 900,
    "lanewidth": 100,
    "num_road": 2,
    "road_image": 'common/assets/road.png',
    "road_border": 'common/assets/road_mask.png',
    "acc_image": 'common/assets/acc.png',
    "shc_image": 'common/assets/shc.png',
    "play_button": 'common/assets/play_button.png',
    "pause_button": 'common/assets/pause_button.png',
    "record_button": 'common/assets/record_button.png'
}

simulation_params = {
    "ts": 0.1,
}

road_params = {
    "vehicle_models": ['shc', 'acc'],
    "toplane_loc": (0,0),
    "road_length": 600,
    "num_lanes": 2,
    "lanewidth": 60,
    "vehicle_inflow": 4000,
}

driving_params = {
    "desired_velocity": 70,
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
    "normal": {"safe_headyway": 3.1, "speed_variation": 5, "politeness_factor": 0.25},
    "irrational": {"safe_headyway": 1.5, "speed_variation": 10, "politeness_factor": 0.15},
}

acc_params = {
    "acc_spawnrate": 0.2,
    "normal": {"safe_headyway": 3.1, "speed_variation": 0, "politeness_factor": 0.5},
    "cautious": {"safe_headyway": 4, "speed_variation": 0, "politeness_factor": 0.8},
}

vehicle_models = [shc_params, acc_params]

# default_params = {
#     'max_velocity': 70,
#     'ACC_logic': 'normal',
#     'SHC_logic': 'normal',
#     'vehicle_inflow': 4000,
#     'safety_threshold': 1.5
# }