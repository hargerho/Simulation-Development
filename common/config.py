# Scale -> 1m:2px, 1km:2000px

# Helper Functions
def length_conversion(value):
    # Convert meters to pixels
    return value*2

def speed_conversion(value):
    # 1mph = 1.60934kmh
    # Converts mph -> pixel/seconds
    return float((value*1.60934*2000)/3600)

# Main Params
window_params = {
    "window_width": 1500,
    "window_height": 600,
    "black": (0,0,0),
    "white": (255,255,255),
    "blue": (0, 0, 255),
    "green": (0,255,0),
    "grey": (128, 128, 128),
    "red": (255,0,0),
    "vehicle_length": 10, #5m
    "vehicle_width": 5, #2+m
    "background_image": 'common/assets/grassbackground.png',
    "onramp_image": 'common/assets/onramp.png',
    "road_image": 'common/assets/roadtile.png',
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
}

road_params = {
    "toplane_loc": (0,500), #(x, y)
    "road_length": length_conversion(500), #16000m
    "onramp_length": length_conversion(140), # 140m
    "num_lanes": 4, # including an onramp
    "lanewidth": 10, # arbitary
    "vehicle_inflow": 4000, # 1000 approx 1veh/3.6sec testing: 10000
    "onramp_inflow": 0,
    "num_convoy_vehicles": 3,
    "road_closed": None
}

# Safety threshold = 1.5m = 3px
# Max Acceleration = 0.73m/s2 = 1.46px/s2
# Comfortable deceleration = 1.67m/s2 = 3.34px/s2
# Left bias = 0.3m/s = 0.6px/s
# Lane change threshold = 0.1m/s = 0.2px/s
driving_params = {
    "desired_velocity": speed_conversion(70), # testing: 16.6
    "safety_threshold": length_conversion(1.5), # testing: 20px
    "max_acceleration": 1.46, # IDM Paper # was 0.73 # Testing:50
    "comfortable_deceleration": 3.34, # IDM Paper # was 1.67 # Testing: 4.61
    "acceleration_component": 4, # IDM Paper
    "left_bias": 0.6, # MOBIL Paper
    "lane_change_threshold": 0.2, # MOBIL Paper
    "acc_logic": "normal", # toggle normal/irrational
    "shc_logic": "normal", # toggle normal/cautious
}

# Noraml Speed Variation = 5m/s = 10px/s
# Irratinal Speed Variation = 10m/s = 20px/s
# Headway in seconds
shc_params = {
    "normal": {"safe_headway": 3.1, "speed_variation": 10, "politeness_factor": 0.25},
    "irrational": {"safe_headway": 1.5, "speed_variation": 20, "politeness_factor": 0.15},
}

acc_params = {
    "acc_spawnrate": 0, # Init 0.2
    "normal": {"safe_headway": 3.1, "speed_variation": 0, "politeness_factor": 0.5},
    "cautious": {"safe_headway": 4, "speed_variation": 0, "politeness_factor": 0.8},
}

vehicle_models = [shc_params, acc_params]

filename = f"ACC{driving_params['acc_logic']}_SHC{driving_params['shc_logic']}_RoadNo_RampIn{road_params['onramp_inflow']}_VehIn{road_params['vehicle_inflow']}"
baseline = f"ACCNo_SHC{driving_params['shc_logic']}_RoadNo_RampIn{road_params['onramp_inflow']}_VehIn{road_params['vehicle_inflow']}"

simulation_params = {
    "ts": 0.2, # was 0.001  testing: 1/60 # Ts < 0.5 same results
    "playback_speed": 5, # realtime = 1
    "folderpath": "data",
    "filename": f"ACC{driving_params['acc_logic']}_SHC{driving_params['shc_logic']}_RoadNo_RampIn{road_params['onramp_inflow']}_VehIn{road_params['vehicle_inflow']}",
    "record": False, # Default False
    "num_vehicles": 1000,
    "testing": False # Default False
}