
from common.config import road_params, driving_params, vehicle_params, vehicle_models, simulation_params
from Vehicle import Vehicle

class Convoy:
    def __init__(self, logic_dict, lead_spawn_loc, num_subconvoy):
        self.lead_car = Vehicle(logic_dict, lead_spawn_loc, "Lead Car")
        self.subconvoy_cars = [Vehicle(logic_dict, lead_spawn_loc, "Sub-Convoy Car") for i in range(num_subconvoy)]

        self.fixed_intra_distance = 50  # Adjust this distance as needed

    def update_convoy(self, ts):
        # Update the lead car
        self.lead_car.update_local(ts, [self.lead_car] + self.subconvoy_cars)
        self.lead_car.update_global()

        # Update the sub-convoy cars
        for car in self.subconvoy_cars:
            # Get the position of the vehicle in front (lead car or the previous sub-convoy car)
            if car == self.subconvoy_cars[0]:  # If the car is the first sub-convoy car
                front_car = self.lead_car
            else:
                front_car = self.subconvoy_cars[self.subconvoy_cars.index(car) - 1]

            # Calculate the desired position based on the fixed intra-convoy distance
            desired_x = front_car.loc_front - self.fixed_intra_distance

            # Update the sub-convoy car's local position
            car.local_loc[0] = desired_x
            car.local_v = front_car.local_v
            car.local_accel = front_car.local_accel

            # Apply lane change decisions made by the lead car to the sub-convoy cars
            car.local_loc[1] = self.lead_car.local_loc[1]

            # Update the sub-convoy car's global position
            car.update_global()

# Example usage:
logic_params = {
    "safe_headyway": 1.0,
    "speed_variation": 5.0,
    "politeness_factor": 0.5
}

lead_spawn_location = [100, 2]  # Example spawn location for the lead car
subconvoy_spawn_locations = [[100, 1], [100, 3]]  # Example spawn locations for the sub-convoy cars

# Create a convoy with the lead car and two sub-convoy cars
convoy = Convoy(logic_params, lead_spawn_location, subconvoy_spawn_locations)

# Perform convoy updates with a time step (ts) as needed
time_step = 0.1
convoy.update_convoy(time_step)
