SCALE = 10 # 1m:SCALE px

def length_conversion(value: int) -> float:

    """
    The function converts a length value from meters to pixels using a scaling factor.

    Args:
      value (float): The value parameter represents the length in meters that you want to convert to pixels.

    Returns:
      the value multiplied by the SCALE.
    """

    return value*SCALE

def speed_conversion(value: int) -> float:

    """
    The function speed_conversion converts a speed value from miles per hour to pixels per second.
    1mph = 1.60934kmh

    Args:
      value: The value parameter represents the speed in miles per hour (mph) that you want to convert.

    Returns:
      the value of speed in pixels per second.
    """

    return float((value*1.60934*length_conversion(1000))/3600)


# Main Params
window_params = {
    "window_width": 1500,
    "window_height": 600,
    "black": (0,0,0),
    "white": (255,255,255),
    "blue": (0, 0, 255),
    "green": (0,255,0),
    "grey": (128, 128, 128),
    "yellow": (255,255,0),
    "vehicle_length": length_conversion(5), #5m
    "vehicle_width": length_conversion(2), #2m
    "scroll_limit": 31760,
    "signpost_interval": length_conversion(1000),
    "onramp_image": 'common/assets/onramp-new.png',
    "road_image": 'common/assets/roadtile.png',
    "miniroad": 'common/assets/miniroad.png',
    "acc_image": 'common/assets/acc.png',
    "shc_image": 'common/assets/shc.png',
    "restart_button": 'common/assets/restart.png',
    "pause_button": 'common/assets/pause_button.png',
    "play_button": 'common/assets/play_button.png',
    "record_button": 'common/assets/record_button.png',
    "record_stop_button": 'common/assets/record_stop_button.png',
    "normal_button": 'common/assets/normal.png',
    "cautious_button": 'common/assets/cautious.png',
    "irrational_button": 'common/assets/irrational.png',
    "off_button": 'common/assets/off.png',
    "left_button": 'common/assets/left.png',
    "middle_button": 'common/assets/middle.png',
    "right_button": 'common/assets/right.png',
    "signpost_image": 'common/assets/signpost.png',
    "speed_limit": 'common/assets/70.png'
}

road_params = {
    "toplane_loc": (0,380), #(x, y)
    "road_length": length_conversion(16000), #16000m
    "onramp_length": length_conversion(140), #140m
    "onramp_offset": length_conversion(2050),
    "num_lanes": 4, # including onramp
    "lanewidth": length_conversion(5), # arbitary
    "vehicle_inflow": 4000,
    "onramp_inflow": 0,
    "num_convoy_vehicles": 3,
    "road_closed": None,
}

# Safety threshold = 1.5m
# Max Acceleration = 0.73m/s2
# Comfortable deceleration = 1.67m/s2
# Left bias = 0.3m/s
# Lane change threshold = 0.1m/s
driving_params = {
    "desired_velocity": speed_conversion(70),
    "safety_threshold": length_conversion(1.5),
    "max_acceleration": length_conversion(0.73), # IDM Paper
    "comfortable_deceleration": length_conversion(1.67), # IDM Paper
    "acceleration_component": 4, # IDM Paper
    "left_bias": length_conversion(0.3), # MOBIL Paper
    "lane_change_threshold": length_conversion(0.1), # MOBIL Paper
    "acc_logic": "normal", # toggle normal/irrational
    "shc_logic": "normal", # toggle normal/cautious
}

shc_params = {
    "normal": {"safe_headway": 3.1, "speed_variation": length_conversion(5), "politeness_factor": 0.25},
    "irrational": {"safe_headway": 1.5, "speed_variation": length_conversion(10), "politeness_factor": 0.15},
}

acc_params = {
    "acc_spawnrate": 0.2, # Init 0.2
    "normal": {"safe_headway": 3.1, "speed_variation": 0, "politeness_factor": 0.5},
    "cautious": {"safe_headway": 4, "speed_variation": 0, "politeness_factor": 0.8},
}

vehicle_models = [shc_params, acc_params]

# Max Real time FPS = 70
# Min ts = 0.01, playback_speed = 1
simulation_params = {
    "ts": 0.1,
    "playback_speed": 2,
    "folderpath": "data",
    "num_vehicles": 100,
    "filename": f"ACC{driving_params['acc_logic']}_SHC{driving_params['shc_logic']}_RoadNo_RampIn{road_params['onramp_inflow']}_VehIn{road_params['vehicle_inflow']}",
    "record": True, # Default False
    "testing": True # Default False
}