import argparse
import logging
import os.path
from start_core.test import execute
from start_core.scenario import Scenario
from start_dbi.trace import Trace
from start_dbi.model import Model

scenarios_root='/usr0/home/dskatz/Documents/umich_demo/start/start-scenarios/'

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)

################################################################################
#
# run_multiple_times
#
################################################################################
# Run the binary a few times
def run_multiple_times(scenario, num_iter):
    traces = []
    for i in range(num_iter):
        logging.debug("Running iteration %d of %d" % (i, num_iter))
        trace = Trace.generate(scenario.sitl,
                               scenario.mission,
                               timeout_mission=600,
                               timeout_connection=2000,
                               timeout_liveness=30)
        traces.append(trace)
    return traces

################################################################################
#
# parse_arguments
#
################################################################################
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_iter', type=int, default=1,
                        help='Number of times to run each scenario')
    parser.add_argument('-s', '--scenarios', type=str,
                        default='AIS-Scenario1/scenario.config',
                        help="Comma separated list of scenario tails.")
    parser.add_argument('-f', '--filename', type=str,
                        default='saved.model',
                        help="Filename to save the model to.")
    args = parser.parse_args()
    return args

################################################################################
#
# main
#
################################################################################
def main():
    args = parse_arguments()
    nominal_traces = []
    print("filename: %s" % args.filename)
    print("type(filename): %s" % type(args.filename))

    scenarios = args.scenarios.split(',')

    for scenario_tail in scenarios:
        fn_scenario = os.path.join(scenarios_root, scenario_tail)
        logging.debug("Running scenario %s" % fn_scenario)
        scenario = Scenario.from_file(fn_scenario)
        nominal_traces += run_multiple_times(scenario, args.num_iter)
    model = Model.build(nominal_traces)
    logging.debug("created model: %s" % model)

    model.to_file(args.filename)
    logging.debug("saved model to: %s" % args.filename)

if __name__ == '__main__':
    main()
