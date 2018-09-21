import argparse
import logging
import os
import uuid
import traceback
from start_core.test import execute
from start_core.scenario import Scenario
from start_dbi.trace import Trace
from start_dbi.model import Model

scenarios_root='/usr0/home/dskatz/Documents/umich_demo/start/start-scenarios/'
output_root='/usr0/home/dskatz/Documents/umich_demo/start_stack/start_dbi/cached_traces/'
patches_root='/usr0/home/dskatz/Documents/umich_demo/start_stack/patches'
dir_ardupilot = "/usr0/home/dskatz/ardupilot_tmp/ardupilot/"

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
###############################################################################
#
# run_multiple_times
#
################################################################################
# Run the binary a few times
def run_multiple_times(scenario, num_iter, to_attack, filename_base,
                       patch=None):

    if to_attack:
        attack = scenario.attack
    else:
        attack = None
    filenames = []
    for i in range(num_iter):
        logging.debug("Running iteration %d of %d" % (i, num_iter))
        uuid_tmp = (uuid.uuid4()).hex
        filename = os.path.join(output_root,
                                "%s_%s.trace" % (filename_base, uuid_tmp))
        print("Filename: %s" % filename)
        if patch:
            with scenario.build(dir_ardupilot, filename_patch=patch) as sitl:
                print("Testing patch %s with scenario %s" % (patch, scenario))
                trace = Trace.generate(sitl,
                                       scenario.mission,
                                       timeout_mission=600,
                                       timeout_connection=2000,
                                       timeout_liveness=30,
                                       attack=attack)
        else:
            trace = Trace.generate(scenario.sitl,
                                   scenario.mission,
                                   timeout_mission=600,
                                   timeout_connection=2000,
                                   timeout_liveness=30,
                                   attack=attack)
        trace.to_file(filename)
        filenames.append(filename)
    return filenames

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
    parser.add_argument('-m', '--missions', type=str,
                        help="Comma separated list of missions.")
    parser.add_argument('-p', '--patch', type=str,
                        default='no_patch',
                        help="Comma separated list of patches to test.")
    args = parser.parse_args()
    return args


################################################################################
#
# get_patches
#
################################################################################
def get_patches(scenario_name):
    patch_dir = os.path.join(patches_root, scenario_name)
    if not os.path.isdir(patch_dir):
        print("%s is not a directory" % patch_dir)
        return []
    patch_fns = [ os.path.join(patch_dir, x) for x in os.listdir(patch_dir)
                  if x.endswith(".diff")]
    return patch_fns

################################################################################
#
# main
#
################################################################################
def main():
    args = parse_arguments()
    scenarios = [os.path.join(scenarios_root, x) for x in
                 args.scenarios.split(',')]
    if not os.path.isdir(output_root):
        os.makedirs(output_root)

    for fn_scenario in scenarios:
        try:
            scenario = Scenario.from_file(fn_scenario)
            scenario_name = (fn_scenario.split('/'))[-2]
            print(scenario_name)
            # Temporary till we get more missions
            missions = [scenario.mission]

            patches = get_patches(scenario_name)
            print("Patches: %s" % patches)
            for mission in missions:
                mission_fn = (mission.filename).split('/')[-2]
                print("**********MISSION_FN: %s*****************" % mission_fn)
                for to_attack in "attack", "noattack":
                    filename_base = "scenario%s_mission%s_%s" % (scenario_name,
                                                                 mission_fn,
                                                                 to_attack)
                    attack = True if to_attack == "attack" else False

                    run_multiple_times(scenario, args.num_iter, attack,
                                       filename_base)

                for patch in patches:
                    filename_base = ("scenario%s_missions%s_%s_patch%s" %
                                     (scenario_name, mission_fn, "attack"))
                    run_multiple_times(scenario, 1, True, filename_base,
                                       patch)


        except Exception as e:
            print("Failed to get the scenario for %s." % fn_scenario)
            print(traceback.format_exc())

if __name__ == '__main__':
    main()
