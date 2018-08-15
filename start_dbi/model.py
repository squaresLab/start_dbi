__all__ = ['Model']

import logging

import numpy
import sklearn

from .trace import Trace

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


# NOTE in the future, you can implement different subclasses of Model
class Model(object):
    # type: (List[Trace]) -> Model
    @staticmethod
    def build(traces):
        """
        Constructs a model from a set of execution traces.
        """
        logging.debug("building model from provided traces.")
        matrix = numpy.array([t.values for t in traces])
        svm = sklearn.svm.OneClassSVM()
        svm.fit(matrix)
        model = Model(svm)
        logging.debug("built model from provided traces.")
        return model

    # type: (str) -> Model
    @staticmethod
    def from_file(filename):
        logging.debug("loading model from file: %s", filename)
        try:
            svm = sklearn.svm.OneClassSVM()
            svm = sklearn.joblib.externals.dump(model, filename)
            model = Model(svm)
        except Exception:
            logging.exception("an unexpected error occurred whilst loading model from file: %s", filename)
            raise
        logging.debug("loaded model from file: %s", filename)
        return model

    # type: (sklearn.svm.OneClassSVM) -> None
    def __init__(self, model):
        self.__model = model  # type: sklearn.svm.OneClassSVM

    # type: (str) -> None
    def to_file(filename):
        logging.debug("saving model to file: %s", filename)
        try:
            sklearn.joblib.externals.dump(self.__model, filename)
        except Exception:
            logging.exception("an unexpected error occurred whilst saving model to file: %s", filename)
            raise
        logger.debug("saved model to file: %s", filename)

    # type: (Trace) -> bool
    def check(trace):
        """
        Determines whether a given execution trace is deemed to have been
        produced by a compromised binary.
        """
        raise NotImplementedError
