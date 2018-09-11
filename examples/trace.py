import os.path
from start_core.test import execute
from start_core.scenario import Scenario
from start_dbi.trace import Trace

scenarios_root='/usr0/home/dskatz/Documents/umich_demo/start/start-scenarios/'

def get_trace():
    scenario_tail = 'AIS-Scenario1/scenario.config'
    fn_scenario = os.path.join(scenarios_root, scenario_tail)
    scenario = Scenario.from_file(fn_scenario)
    trace = Trace.generate(scenario.sitl,
                           scenario.mission,
                           timeout_mission=600,
                           timeout_connection=2000,
                           timeout_liveness=30)
    print(trace)


def test_mission():
    scenario_tail = 'AIS-Scenario1/scenario.config'
    fn_scenario = os.path.join(scenarios_root, scenario_tail)
    scenario = Scenario.from_file(fn_scenario)
    execute(scenario.sitl,
            scenario.mission,
            timeout_liveness=10)


if __name__ == '__main__':
    get_trace()
