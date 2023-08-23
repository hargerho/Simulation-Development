from common.config import simulation_params, driving_params, window_params
from Vehicle import Vehicle
from DriverModel import DriverModel as DM
# class Convoy(Vehicle):
#     def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
#         super().__init__(logic_dict, lead_spawn_loc, vehicle_type)
#         self.ts = simulation_params['ts']
#         self.num_subconvoy = num_subconvoy
#         self.veh_length = self.num_subconvoy * window_params['vehicle_length']

class ConvoyMetrics:
    def __init__(self, convoy_list):
        self.convoy_list = convoy_list
        self.name = 'metrics'
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.veh_length = abs(self.loc_front - self.loc_back)
        new_x_convoy = self.loc_front - self.veh_length/2
        new_y_convoy = self.lead_vehicle.loc[1]
        self.loc = [new_x_convoy, new_y_convoy]
        self.v = self.lead_vehicle.v

    def update_convoy_params(self):
        # Convoy Level Params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.veh_length = abs(self.loc_front - self.loc_back)
        new_x_convoy = self.loc_front - self.veh_length/2
        new_y_convoy = self.lead_vehicle.loc[1]
        self.loc = [new_x_convoy, new_y_convoy]
        self.v = self.lead_vehicle.v

class Convoy:
    def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
        self.ts = simulation_params['ts']

        self.convoy_list = [
            Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type)
            for _ in range(num_subconvoy)
        ]

        self.convoy_metrics = ConvoyMetrics(self.convoy_list)

        # Initialize convoy-level params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.loc = lead_spawn_loc
        self.v = self.lead_vehicle.v
        self.veh_length = abs(self.loc_front - self.loc_back)

        self.convoy_dist = logic_dict.get('safe_headway') + driving_params['safety_threshold'] + window_params['vehicle_length']/2

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

        self.convoy_metrics.update_convoy_params()

        # # Convoy Level Params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.veh_length = abs(self.loc_front - self.loc_back)
        new_x_convoy = self.loc_front - self.veh_length/2
        new_y_convoy = self.lead_vehicle.loc[1]
        self.loc = [new_x_convoy, new_y_convoy]
