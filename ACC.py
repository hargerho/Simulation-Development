
from Vehicle import Vehicle

class Convoy:
    def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
        self.lead_vehicle = Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type)
        self.subconvoy_vehicle = [Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type) for i in range(num_subconvoy)]
        self.convoy_list = [self.lead_vehicle] + self.subconvoy_vehicle
    def __init__(self, logic_dict, lead_spawn_loc, vehicle_type, num_subconvoy):
        self.lead_vehicle = Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type)
        self.subconvoy_vehicle = [Vehicle(logic_dict, lead_spawn_loc, vehicle_type=vehicle_type) for i in range(num_subconvoy)]
        self.convoy_list = [self.lead_vehicle] + self.subconvoy_vehicle

    def update_convoy(self, ts):

        # Getting the lead vehicle
        # for vehicle in self.convoy_list:
        #     if vehicle == self.convoy_list[0]:
        #         self.lead_vehicle = vehicle
        #     else:
        #         self.lead_vehicle = self.convoy_list[self.subconvoy_vehicle.index(vehicle) - 1]

        self.lead_vehicle = self.convoy_list[0]

        # Update the lead_vehicle
        self.lead_vehicle.update_local(ts, self.convoy_list)
        self.lead_vehicle.update_global()

        # Update the sub-convoy_vehicles
        if len(self.subconvoy_vehicle) > 1: # if there is more than one vehicle in convoy
            for vehicle in self.subconvoy_vehicle:
                # Get the front vehicle (lead_vehicle or the previous sub-convoy_vehicle)
                if vehicle == self.subconvoy_vehicle[0]:  # If the_vehicle is the first sub-convoy_vehicle
                    front_vehicle = self.lead_vehicle
                else:
                    front_vehicle = self.subconvoy_vehicle[self.subconvoy_vehicle.index(vehicle) - 1]

            # Calculate the desired position based on the fixed intra-convoy distance
            desired_x = front_vehicle.loc_front - self.fixed_intra_distance

        if len(self.convoy_list) > 1:
            for i in range(1, len(self.convoy_list)):
                pass


        # Update the sub-convoy_vehicle's local position
        vehicle.local_loc[0] = desired_x
        vehicle.local_v = front_vehicle.local_v
        vehicle.local_accel = front_vehicle.local_accel

        # Apply lane change decisions made by the lead_vehicle to the sub-convoy_vehicles
        vehicle.local_loc[1] = self.lead_vehicle.local_loc[1]

            # Update the sub-convoy_vehicle's global position
        vehicle.update_global()

    def update_subconvoy(self, subconvoy):
        # Update road traverse
        self.local_loc[0] += (self.v * ts)

        # Updating local dist
        if surrounding['front'] is not None:
            dist = surrounding['front'].loc_back - self.loc_front
            # Ensure dist is non-zero
            if dist <= 0:
                dist = 1e-9
        else:
            dist = self.road_length

        if surrounding['front'] is not None:
            front_v = surrounding['front'].v
        else:
            front_v = self.v

        # Update local driving parameters
        self.local_v = self.v
        self.local_accel = self.driver.calc_acceleration(v=self.v, surrounding_v=front_v, s=dist) * ts
        self.local_v += self.local_accel
        self.local_v = max(self.local_v, 0)

    # def update_local(self, ts, convoy_list):
