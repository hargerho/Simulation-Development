import time

from src.Window import Window
from src.Test import Test
from common.config import *
from typing import List, Dict, Union

TESTING_FLAG = False

# List = [ACC Logic, SHC Logic, Road Closure, On-ramp Flow, Vehicle Inflow]
TESTING_PARAMS = {
    0: ['normal', 'normal', None, 0, 4000],
    1: ['cautious', 'normal', None, 0, 4000],
    2: ['cautious', 'irrational', None, 0, 4000],
    3: ['normal', 'normal', None, 0, 4000],
    4: ['normal', 'irrational', None, 0, 4000],
    5: ['normal', 'normal', "left", 0, 4000],
    6: ['normal', 'normal', "middle", 0, 4000],
    7: ['normal', 'normal', "right", 0, 4000],
    8: ['normal', 'normal', None, 50, 4000],
    9: ['normal', 'normal', None, 100, 4000],
    10: ['normal', 'normal', None, 150, 4000],
    11: ['normal', 'normal', None, 200, 4000],
    12: ['normal', 'normal', None, 0, 1000],
    13: ['normal', 'normal', None, 0, 2000],
    14: ['normal', 'normal', None, 0, 3000],
    15: ['normal', 'normal', None, 0, 5000],
    16: ['normal', 'normal', None, 0, 6000],
    17: ['normal', 'normal', None, 0, 7000],
}


def load_testing(testing_params: Dict[int, List[Union[str, int, None]]]) -> None:

    """Loads a series of tests with different combinations of parameters

    Args:
        testing_params (Dict[int, List[Union[str, int, None]]]): contains different
        combinations of parameters for testing.
        The key represents the combination number,
        and the value is a list of parameters for that combination.
    """

    start = time.time()

    for combination, testing_list in testing_params.items():
        print("----------------------")
        print("Testing Combination:", combination)

        start_time = time.time()
        road_params["vehicle_inflow"] = testing_list[4]
        road_params["onramp_inflow"] = testing_list[3]
        road_params["road_closed"] = testing_list[2]
        driving_params["shc_logic"] = testing_list[1]
        driving_params["acc_logic"] = testing_list[0]
        acc_params["acc_spawnrate"] = 0 if combination == 0 else 0.2
        simulation_params["filename"] = f"ACC{driving_params['acc_logic']}_SHC{driving_params['shc_logic']}_RoadNo_RampIn{road_params['onramp_inflow']}_VehIn{road_params['vehicle_inflow']}"

        test = Test()
        test.run_test()

        end_time = time.time()
        print(f"Combination {combination} took {end_time-start_time}")

    end = time.time()
    print("============================")
    print(f"Simulation Ended: {end-start}")
    print("============================")


def main() -> None:

    """
    The main function runs a simulation with different testing parameters
    without the user interface if the TESTING_FLAG is set,
    otherwise it runs the simulation normally with the user interface.
    """

    simulation_params['record'] = TESTING_FLAG
    simulation_params['testing'] = TESTING_FLAG

    # Run the simulation for the various testing parameters
    if TESTING_FLAG:
        load_testing(testing_params=TESTING_PARAMS)
    else:
        # Just run the simulation
        win = Window()
        win.run_window()


if __name__ == "__main__":
    main()