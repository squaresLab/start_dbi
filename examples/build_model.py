import argparse
import logging
import os.path
import uuid

import matplotlib.pyplot as plt
import numpy as np

from start_core.test import execute
from start_core.scenario import Scenario
from start_dbi.trace import Trace
from start_dbi.model import Model, LOF
from sklearn.decomposition import PCA
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MaxAbsScaler

patch_root='/usr0/home/dskatz/Documents/umich_demo/start_stack/patches/'
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
# plot
#
################################################################################
def plot(X, y_pred, clf, indexes=[]):
    print("indexes: %s" % indexes)
    pca = PCA(n_components=2)

    scaler = MaxAbsScaler()
    X_scaled = scaler.fit_transform(X)

    def fullprint(*args, **kwargs):
        from pprint import pprint
        import numpy
        opt = numpy.get_printoptions()
        numpy.set_printoptions(threshold='nan')
        pprint(*args, **kwargs)
        numpy.set_printoptions(**opt)

    #print("*"*80)
    #print("*"*80)
    #print("X before transformation:")
    #fullprint(X_scaled)
    #print("*"*80)
    #print("*"*80)
    #print("*"*80)

    X = pca.fit_transform(X_scaled)

    #print("X after transformation:")
    #print(X)
    #print("*"*80)
    #print("*"*80)
    #print("*"*80)


    np.random.seed(42)

    # Generate train data
    #X = 0.3 * np.random.randn(100, 2)
    # Generate some abnormal novel observations
    #X_outliers = np.random.uniform(low=-4, high=4, size=(20, 2))
    #X = np.r_[X + 2, X - 2, X_outliers]

    # fit the model
    clf = LocalOutlierFactor(n_neighbors=20)
    # re-fitting a new model on the 2d data
    y_pred = clf.fit_predict(X)
    assert(len(X) == len(y_pred))
    zipped = zip(X, y_pred)

    inliers = np.array([ i[0] for i in zipped if i[1] == 1])
    outliers = np.array([ i[0] for i in zipped if i[1] == -1 ])
    assert(len(y_pred) == len(inliers) + len(outliers))

    call_outs = []
    if len(indexes) > 0:
        assert(all([len(i) == len(X) for i in indexes]))

        for index in indexes:
            zip_index = zip(X, index)
            call_out = np.array([ i[0] for i in zip_index if i[1] == 1 ])
            call_outs.append(call_out)

    call_outs = np.array(call_outs)
    print("call_outs:")
    print(call_outs)

    # plot the level sets of the decision function
    xx, yy = np.meshgrid(np.linspace(-1, 1, 50), np.linspace(-1, 1, 50))
    Z = clf._decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    print("*"*80)
    print("Z:")
    print(Z.shape)
    print(Z)
    print("*"*80)

    plt.title("Local Outlier Factor (LOF) for AIS-Scenario16")
    plt.contourf(xx, yy, Z, cmap=plt.cm.Blues_r)

    if len(call_outs) > 0:
        legend = []
        for call_out, color in zip(call_outs, ["green", "purple", "orange"]) :
            c = plt.scatter(call_out[:, 0], call_out[:, 1], c=color,
#                            marker=".", alpha=0.1,
                            s=20)
            legend.append(c)
        plt.legend(legend,
                   ["removes r = x/ y", "removes long switch statement"],
                   loc="upper left")
    else:
        a = plt.scatter(inliers[:,0], inliers[:,1], c='white',
                        edgecolor='k', s=20)
        b = plt.scatter(outliers[:, 0], outliers[:, 1], c='red',
                        edgecolor='k', s=20)
        plt.legend([a, b],
                   ["typical behavior",
                    "outliers"],
                   loc="upper left")

    plt.axis('tight')
    max_x = max([i[0] for i in X])
    min_x = min([i[0] for i in X])
    max_y = max([i[1] for i in X])
    min_y = min([i[1] for i in X])
    plt.autoscale()
    #plt.xlim((min_x - 0.01, max_x + 0.01))
    #plt.ylim((min_y - 0.01, max_y + 0.01))
    #plt.xlim((-.2,.1))
    #plt.ylim((-.2,.2))

    plt.savefig("visualization1.png")
    plt.show()


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
    parser.add_argument('-p', '--test_patch', type=str,
                        default='no_patch',
                        help="Comma separated list of patches to test.")
    parser.add_argument('--use_existing_traces', type=bool)
    parser.add_argument('--trace_dir', type=str)
    parser.add_argument('--lof', action='store_true', default=False)
    parser.add_argument('--plot', action='store_true', default=False)
    parser.add_argument('--patch_name_set', type=str, action="append")
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
        print("Trying to load model from file: %s" % args.filename)
        model = Model.from_file(args.filename)
    except:
        print("building model")
        if args.use_existing_traces:
            if (os.path.isdir(args.trace_dir)):
                trace_fns = [os.path.join(args.trace_dir, x) for x in
                             os.listdir(args.trace_dir) if x.endswith('.trace')]
                nominal_traces = [Trace.from_file(x) for x in trace_fns]
                print("nominal_traces: %s" % nominal_traces)
            else:
                print("trace_dir %s is not a dir. exiting")
                exit()

        else:
            for fn_scenario in scenarios:
                logging.debug("Running scenario %s" % fn_scenario)
                scenario = Scenario.from_file(fn_scenario)
                nominal_traces += run_multiple_times(scenario, args.num_iter)


        if args.lof:
            lof = LOF()
            predictions = lof.build(nominal_traces, neighbors=5)
            assert(len(predictions) == len(nominal_traces))
            assert(len(trace_fns) == len(predictions))
            zipped = zip(trace_fns, predictions)
            print("*"*80)
            print("Predictions")
            print("*"*80)
            zipped.sort(key=lambda x: x[0])

            def patch_name(fn):
                scenario_name = fn.partition("scenario")[2]
                scenario_name = scenario_name.partition("_mission")[0]
                shorter = fn.rpartition(".diff")[0]
                shorter = shorter.rpartition("_")[2]
                return "%s_%s" % (scenario_name, shorter)
            for trace_fn, pred in zipped:
                pred_word = "Compromised" if pred == -1 else "Not-Compromised"
                print("trace file: %s\nprediction: %s" %
                      (patch_name(trace_fn), pred_word))

            compromised_list = [ x for x in zipped if x[1] == -1]
            not_compromised_list = [ x for x in zipped if x[1] == 1]
            assert(len(compromised_list) + len(not_compromised_list) ==
                   len(zipped))
            print("Compromised: %s" % [ patch_name(x[0]) for x
                                        in compromised_list])
            print("Not compromised: %s" % [patch_name(x[0]) for x in
                                           not_compromised_list])


            #print("nominal traces shape: %s" % np.array(nominal_traces).shape)
            #print(nominal_traces)
            #print("predictions shape: %s" % np.array(predictions).shape)
            #print(predictions)


            if args.plot:
                indexes = []
                if args.patch_name_set:
                    patch_name_sets = [x.split(',') for x in
                                       args.patch_name_set]

                    for patch_name_set in patch_name_sets:
                        indexes_one = [ 1 if patch_name(x) in
                                        patch_name_set else 0
                                        for x in trace_fns ]
                        indexes.append(indexes_one)
                plot(np.array([ x.values for x in nominal_traces]),
                     np.array(predictions),
                     lof.get_model(), indexes=indexes)


        else:
            model = Model.build(nominal_traces)
            logging.debug("created model: %s" % model)

            model.to_file(args.filename)
            logging.debug("saved model to: %s" % args.filename)


    if args.test_patch != 'no_patch':
        patches = [ os.path.join(patch_root, x) for x in
                    args.test_patch.split(',')]
        print("patches: %s" % patches)
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
                        print("VALUE OF COMPROMISED for %s: %s" %
                              (patch, compromised))
                        uuid_loc = (uuid.uuid4()).hex
                        trace.to_file("%s_%s.trace" % (patch, uuid_loc))

                        logging.debug("Patch %s with scenario %s prediction:"
                                      % (patch, scenario))
                        if compromised:
                            logging.debug("Compromised")
                        else:
                            logging.debug("Not compromised")

if __name__ == '__main__':
    main()
