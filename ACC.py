from common.config import simulation_params, driving_params, window_params
from Vehicle import Vehicle
from DriverModel import DriverModel as DM
# class Convoy(Vehicle):
#     def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
#         super().__init__(logic_dict, lead_spawn_loc, vehicle_type)
#         self.ts = simulation_params['ts']
#         self.num_subconvoy = num_subconvoy
#         self.veh_length = self.num_subconvoy * window_params['vehicle_length']

class Convoy:
    def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
        self.ts = simulation_params['ts']

        # # Vehicle params
        # self.v_0 = driving_params['desired_velocity']
        # self.s_0 = driving_params['safety_threshold']
        # self.a = driving_params['max_acceleration']
        # self.b = driving_params['comfortable_deceleration']
        # self.delta = driving_params['acceleration_component']
        # self.T = logic_dict.get('safe_headway')
        # self.left_bias = driving_params['left_bias']
        # self.politeness = logic_dict.get('politeness_factor')
        # self.change_threshold = driving_params['lane_change_threshold']

        # model_params = {
        #     "v_0": self.v_0,
        #     "s_0": self.s_0,
        #     "a": self.a,
        #     "b": self.b,
        #     "delta": self.delta,
        #     "T": self.T,
        #     "left_bias": self.left_bias,
        #     "politeness": self.politeness,
        #     "change_threshold": self.change_threshold
        # }

        # self.driver = DM(model_params=model_params)

        self.convoy_list = [
            Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type)
            for _ in range(num_subconvoy)
        ]

        # Initialize convoy-level params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.loc = lead_spawn_loc
        self.v = self.lead_vehicle.v
        self.veh_length = abs(self.loc_front - self.loc_back)

        self.convoy_dist = logic_dict.get('safe_headway') + driving_params['safety_threshold'] + 20

    def update_convoy_local(self, vehicle_list, vehicle_type):
        for idx, vehicle in enumerate(self.convoy_list):
            if idx == 0: # lead vehicle
                vehicle.update_local(vehicle_list, vehicle_type=vehicle_type)
            elif len(self.convoy_list) > 1: # update subconvoy
                vehicle.local_loc[1] = self.convoy_list[idx-1].local_loc[1]
                vehicle.local_loc[0] = self.convoy_list[idx-1].local_loc[0] - self.convoy_dist
                vehicle.local_v = self.convoy_list[idx-1].local_v
                vehicle.local_accel = self.convoy_list[idx-1].local_accel

    def update_convoy_global(self):
        for idx, vehicle in enumerate(self.convoy_list):
            if idx == 0: # lead vehicle
                vehicle.update_global()
                self.v = vehicle.v
            elif len(self.convoy_list) > 1:
                vehicle.v = vehicle.local_v
                new_x = self.convoy_list[idx-1].local_loc[0] - self.convoy_dist
                new_y = self.convoy_list[idx-1].local_loc[1]
                vehicle.loc = [new_x, new_y]
                vehicle.loc_front = vehicle.loc[0] + (vehicle.veh_length/2)
                vehicle.loc_back = vehicle.loc[0] - (vehicle.veh_length/2)

        # Convoy Level Params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.veh_length = abs(self.loc_front - self.loc_back)
        new_x_convoy = self.loc_front - self.veh_length/2
        new_y_convoy = self.lead_vehicle.loc[1]
        self.loc = [new_x_convoy, new_y_convoy]
        # self.v = self.lead_vehicle.v
