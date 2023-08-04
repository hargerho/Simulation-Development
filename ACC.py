from common.config import simulation_params
from Vehicle import Vehicle

class Convoy:
    def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
        self.ts = simulation_params['ts']
        self.convoy_list = [
            Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type)
            for _ in range(num_subconvoy)
        ]
        self.convoy_dist = logic_dict.get('safe_headway')

        # Initialize initial positions
        self.lead_vehicle = self.convoy_list[0]
        self.tail_vehicle = self.convoy_list[-1]

        self.convoy_front = self.lead_vehicle.loc_front
        self.convoy_back = self.tail_vehicle.loc_back
        self.convoy_loc = self.convoy_back + (self.convoy_front - self.convoy_back)/2
        self.convoy_v = self.lead_vehicle.v

    def update_convoy(self, global_list, vehicle_type):

        self.lead_vehicle = self.convoy_list[0]

        # Update the lead_vehicle
        self.lead_vehicle.update_local(global_list, vehicle_type=vehicle_type)
        self.lead_vehicle.update_global()

        # Updating the subconvoy local params
        if len(self.convoy_list) > 1:
            for i in range(1, len(self.convoy_list)):

                current_vehicle = self.convoy_list[i]
                front_vehicle = self.convoy_list[i-1]

                # Update road traverse
                current_vehicle.local_loc[0] = front_vehicle.local_loc[0] -  self.convoy_dist - 15 # place holder distance

                # If lead car change lanes
                current_vehicle.local_loc[1] = self.lead_vehicle.local_loc[1]

                current_vehicle.local_v = front_vehicle.local_v
                current_vehicle.local_accel = front_vehicle.local_accel

                # Update the sub-convoy_vehicle's global position
                current_vehicle.update_global()

        # Update convoy level position
        self.convoy_front = self.convoy_list[0].loc_front
        self.convoy_back = self.convoy_list[-1].loc_back
        self.convoy_loc = self.convoy_back + (self.convoy_front - self.convoy_back)/2
        self.convoy_v = self.lead_vehicle.v
