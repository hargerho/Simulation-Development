from common.config import *
from Vehicle import Vehicle
from DriverModel import DriverModel as DM
import math
class Convoy:
    def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
        self.ts = simulation_params['ts']
        self.road_length = road_params['road_length']

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
        self.sub_length = window_params['vehicle_length']

        self.convoy_dist = driving_params['convoy_dist']

        for idx, vehicle in enumerate(self.convoy_list):
            if idx == 0:
                pass
            else:
                vehicle.local_loc[0] = self.convoy_list[idx-1].local_loc[0] - self.convoy_dist - 10

    def update_convoy_local(self, vehicle_list, vehicle_type):
        for idx, vehicle in enumerate(self.convoy_list):
            if idx == 0: # lead vehicle
                vehicle.update_local(vehicle_list, vehicle_type=vehicle_type, lead_flag=True)
            elif len(self.convoy_list) > 1: # update subconvoy
                vehicle.local_loc[1] = self.convoy_list[idx-1].local_loc[1]
                # vehicle.local_loc[0] = self.convoy_list[idx-1].local_loc[0] - self.convoy_dist
                # vehicle.local_v = self.convoy_list[idx-1].local_v
                # vehicle.local_accel = self.convoy_list[idx-1].local_accel

                # vehicle.update_local(self.convoy_list, vehicle_type, lead_flag=False)
                vehicle.update_acc_driving_params(surrounding=self.convoy_list[idx-1])

        # # Convoy Level Params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        loc_front = self.lead_vehicle.loc[0] + (self.sub_length/2)
        loc_back = self.tail_vehicle.loc[0] - (self.sub_length/2)
        self.veh_length = abs(loc_front - loc_back)
        new_x_convoy = self.loc_front - self.veh_length/2
        new_y_convoy = self.lead_vehicle.loc[1]
        self.local_loc = [new_x_convoy, new_y_convoy]

    def update_convoy_global(self):
        for idx, vehicle in enumerate(self.convoy_list):
            # if idx == 0: # lead vehicle
            #     vehicle.update_global()
            #     self.v = vehicle.v
            # elif len(self.convoy_list) > 1:
                # vehicle.v = vehicle.local_v
                # new_x = self.convoy_list[idx-1].local_loc[0] - self.convoy_dist
                # new_y = self.convoy_list[idx-1].local_loc[1]
                # vehicle.loc = [new_x, new_y]
                # vehicle.loc_front = vehicle.loc[0] + (vehicle.veh_length/2)
                # vehicle.loc_back = vehicle.loc[0] - (vehicle.veh_length/2)
            vehicle.update_global()

        # # Convoy Level Params
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]
        self.loc_front = self.lead_vehicle.loc_front
        self.loc_back = self.tail_vehicle.loc_back
        self.veh_length = abs(self.loc_front - self.loc_back)
        new_x_convoy = self.loc_front - self.veh_length/2
        new_y_convoy = self.lead_vehicle.loc[1]
        self.loc = [new_x_convoy, new_y_convoy]