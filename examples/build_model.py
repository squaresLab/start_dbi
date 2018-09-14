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
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


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
                        help="Filename to save the model or load the model.")
    parser.add_argument('-t', '--test_patch', type=str,
                        default='no_patch',
                        help="Comma separated list of patches to test.")
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

    scenarios = [os.path.join(scenarios_root, x) for x in
                 args.scenarios.split(',')]

    try:
        logging.debug("Trying to load model from file: %s" % args.filename)
        model = Model.from_file(args.filename)
    except:

        for fn_scenario in scenarios:
            logging.debug("Running scenario %s" % fn_scenario)
            scenario = Scenario.from_file(fn_scenario)
            nominal_traces += run_multiple_times(scenario, args.num_iter)



        model = Model.build(nominal_traces)
        logging.debug("created model: %s" % model)

        model.to_file(args.filename)
        logging.debug("saved model to: %s" % args.filename)


    if args.test_patch != 'no_patch':
        patches = args.test_patch.split(',')
        for patch in patches:
            if os.path.isfile(patch):
                for fn_scenario in scenarios:
                    scenario = Scenario.from_file(fn_scenario)
                    dir_ardupilot = "/usr0/home/dskatz/ardupilot_tmp/ardupilot/"
                    with scenario.build(dir_ardupilot,
                                        filename_patch=patch) as sitl:
                        logging.debug("Testing patch %s with scenario %s" %
                                      (patch, scenario))
                        trace = Trace.generate(sitl,
                                               scenario.mission,
                                               timeout_mission=600,
                                               timeout_connection=2000,
                                               timeout_liveness=30,
                                               attack=scenario.attack)
                        compromised = model.check(trace)
                        logging.debug("Patch %s with scenario %s prediction:"
                                      % (patch, scenario))
                        if compromised:
                            logging.debug("Compromised")
                        else:
                            logging.debug("Not compromised")

if __name__ == '__main__':
    main()
