from Window import Window
from Test import Test
import time

from common.config import *
testing = False

def get_params(combination):

    # List = [ACC Logic, SHC Logic, Road Closure, On-ramp Flow, Vehicle Inflow]
    testing_params = {
        0: ['normal', 'normal', None, 0, 4000],
        1: ['cautious', 'normal', None, 0, 4000],
        2: ['cautious', 'irrational', None, 0, 4000],
        3: ['normal', 'normal', None, 0, 4000],
        4: ['normal', 'irrational', None, 0, 4000],
        5: ['normal', 'normal', "left", 0, 4000],
        6: ['normal', 'normal', "middle", 0, 4000],
        7: ['normal', 'normal', "right", 0, 4000],
        8: ['normal', 'normal', None, range(200), 4000], # Manual testing range(200)
        9: ['normal', 'normal', None, 0, range(1000,7000)], # Manual testing
    }

    # range_testing = {
    #     0: ['normal', 'normal', None, 50, 4000],
    #     1: ['normal', 'normal', None, 100, 4000],
    #     2: ['normal', 'normal', None, 150, 4000],
    #     3: ['normal', 'normal', None, 200, 4000],
    #     4: ['normal', 'normal', None, 0, 1000], # Redo Simulation [checkbox] Redo Plots [checkbox]
    #     5: ['normal', 'normal', None, 0, 2000],
    #     6: ['normal', 'normal', None, 0, 3000],
    #     7: ['normal', 'normal', None, 0, 5000],
    #     8: ['normal', 'normal', None, 0, 6000],
    #     9: ['normal', 'normal', None, 0, 7000],
    # }

    range_testing = {
        4: ['normal', 'normal', None, 0, 1000],
    }

    # Change here
    return testing_params.get(combination)

def main():
    if testing:
        simulation_params['record'] = testing
        simulation_params['testing'] = testing

        start = time.time()

        for i in range(10):
            print("----------------------")
            print("Testing Combination:", i)
            startite = time.time()
            testing_list = get_params(i)
            road_params["vehicle_inflow"] = testing_list[4]
            road_params["onramp_inflow"] = testing_list[3]
            road_params["road_closed"] = testing_list[2]
            driving_params["shc_logic"] = testing_list[1]
            driving_params["acc_logic"] = testing_list[0]
            acc_params["acc_spawnrate"] = 0 if i == 0 else 0.2
            simulation_params["filename"] = f"ACC{driving_params['acc_logic']}_SHC{driving_params['shc_logic']}_RoadNo_RampIn{road_params['onramp_inflow']}_VehIn{road_params['vehicle_inflow']}"
            simulation_params['testing'] = testing
            simulation_params['record'] = testing
            test = Test()
            test.run_test()
            endite = time.time()
            print(f"Combination {i} took {endite-startite}")

        end = time.time()
        print("============================")
        print(f"Simulation Ended: {end-start}")
        print("============================")
    else:
        # Just run the simulation
        simulation_params['record'] = testing
        simulation_params['testing'] = testing
        win = Window()
        win.run_window()

if __name__ == "__main__":
    main()