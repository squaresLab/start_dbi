__all__ = ['Model']

import logging

import numpy
from sklearn import svm as svm_module
from sklearn import externals

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
        svm = svm_module.OneClassSVM()
        svm.fit(matrix)
        model = Model(svm)
        logging.debug("built model from provided traces.")
        return model

    @staticmethod
    def from_file(filename):
        # type: (str) -> Model
        logging.debug("loading model from file: %s", filename)
        try:
            svm = svm_module.OneClassSVM()
            svm = externals.joblib.load(model, filename)
            model = Model(svm)
        except Exception:
            logging.exception("an unexpected error occurred whilst loading model from file: %s", filename)
            raise
        logging.debug("loaded model from file: %s", filename)
        return model

    def __init__(self, model):
        # type: (svm.OneClassSVM) -> None
        self.__model = model  # type: svm.OneClassSVM

    def to_file(self, filename):
        # type: (str) -> None
        logging.debug("saving model to file: %s", filename)
        try:
            externals.joblib.dump(self.__model, filename)
        except Exception:
            logging.exception("an unexpected error occurred whilst saving model to file: %s", filename)
            raise
        logger.debug("saved model to file: %s", filename)

    def check(trace):
        # type: (Trace) -> bool
        """
        Determines whether a given execution trace is deemed to have been
        produced by a compromised binary.

        Returns:
            True if trace is believed to belong to a compromised binary, else
            False.
        """
        logging.debug("determining whether execution trace belongs to a compromised binary")  # noqa: pycodestyle
        arr = numpy.array(trace.values).reshape(1, -1)

        if self.__model.predict(arr) == -1:
            logging.debug("execution trace believed to belong to a compromised binary")  # noqa: pycodestyle
            return True

        logging.debug("determined that execution trace does not belong to a compromised binary")  # noqa: pycodestyle
        return False

class Svm(Model):
    def __init__(self, model):
        Model.__init__(self, model)
