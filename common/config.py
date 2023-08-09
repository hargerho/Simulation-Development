# Scale -> 1m:2px

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
    "road_image": 'common/assets/road.png',
    "road_border": 'common/assets/road_mask.png',
    "acc_image": 'common/assets/acc.png',
    "shc_image": 'common/assets/shc.png',
    "restart_button": 'common/assets/restart.png',
    "pause_button": 'common/assets/pause_button.png',
    "play_button": 'common/assets/play_button.png',
    "record_button": 'common/assets/record_button.png',
    "record_stop_button": 'common/assets/record_stop_button.png'
}

# List = [ACC Logic, SHC Logic, Road Closure, On-ramp Flow, Vehicle Inflow]
testing_params = {
    "Baseline":['normal', 'normal', None, 0, 4000],
    "1": ['cautious', 'normal', None, 0, 4000],
    "2": ['cautious', 'irrational', None, 0, 4000],
    "3": ['noraml', 'normal', None, 0, 4000],
    "4": ['noraml', 'irrational', None, 0, 4000],
    "5": ['noraml', 'normal', "left", 0, 4000],
    "6": ['noraml', 'normal', "middle", 0, 4000],
    "7": ['noraml', 'normal', "right", 0, 4000],
    "8": ['noraml', 'normal', None, range(200), 4000], # Manual testing
    "9": ['noraml', 'normal', None, 0, range(1000,7000)], # Manual testing
}

# Change here
testing_list = testing_params.get("Baseline")

road_params = {
    "toplane_loc": (0,500), #(x, y)
    "road_length": 32000, #16000m 32000
    "onramp_length": 280, # 140m
    "num_lanes": 4, # including an onramp
    "lanewidth": 10,
    "vehicle_inflow": testing_list[4], # 1000 approx 1veh/3.6sec testing: 10000
    "onramp_inflow": testing_list[3],
    "num_convoy_vehicles": 3,
    "road_closed": testing_list[2]
}

# Safety threshold = 1.5m = 3px
# Max Acceleration = 0.73m/s2 = 1.46px/s2
# Comfortable deceleration = 1.67m/s2 = 3.34px/s2
# Left bias = 0.3m/s = 0.6px/s
# Lane change threshold = 0.1m/s = 0.2px/s
driving_params = {
    "desired_velocity": 140, # testing: 16.6
    "safety_threshold": 3, # testing: 20px
    "max_acceleration": 1.46, # IDM Paper # was 0.73 # Testing:50
    "comfortable_deceleration": 3.34, # IDM Paper # was 1.67 # Testing: 4.61
    "acceleration_component": 4, # IDM Paper
    "left_bias": 0.6, # MOBIL Paper
    "lane_change_threshold": 0.2, # MOBIL Paper
    "acc_logic": testing_list[0], # toggle normal/irrational
    "shc_logic": testing_list[1], # toggle normal/cautious
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
    "ts": 0.1, # was 0.001  testing: 1/60 # Ts < 0.5 same results
    "playback_speed": 10, # realtime = 1
    "folderpath": "data",
    "filename": baseline,
    "record": False,
    "num_vehicles": 500
}