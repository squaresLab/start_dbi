from start_core.test import execute
from start_core.scenario import Scenario
from start_dbi.trace import Trace


def get_trace():
    fn_scenario = '/home/chris/start/scenarios/AIS-Scenario1/scenario.config'
    scenario = Scenario.from_file(fn_scenario)
    trace = Trace.generate(scenario.sitl,
                           scenario.mission,
                           timeout_mission=600)
    print(trace)


def test_mission():
    fn_scenario = '/home/chris/start/scenarios/AIS-Scenario1/scenario.config'
    scenario = Scenario.from_file(fn_scenario)
    execute(scenario.sitl,
            scenario.mission,
            timeout_liveness=10)


if __name__ == '__main__':
    get_trace()
