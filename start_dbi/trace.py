__all__ = ['Trace']

import logging
import collections
import tempfile
import os

from start_core.scenario import Scenario
from start_core.mission import Mission

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


class Trace(object):
    """
    Describes a trace for a single execution of ArduPilot.
    """
    # type: (str, Mission) -> Trace
    @staticmethod
    def generate(binary, mission):
        """
        Executes a given mission using a specified ArduPilot binary and
        returns its execution trace.
        """
        logging.debug("obtaining an execution trace for mission [%s] using binary [%s]",  # noqa: pycodestyle
                      binary, mission)

        fn_signals = tempfile.mkstemp('.signal', 'start')
        try:
            # TODO
            sitl_prefix = "TODO"

            # TODO execute mission via `start_core`

            trace = Trace.from_file(fn_signals)
        finally:
            os.remove(fn_signals)

        logging.debug("obtained execution trace for mission [%s] using binary [%s]",  # noqa: pycodestyle
                      binary, mission)
        return trace

    # type: (str) -> Trace
    @staticmethod
    def from_file(filename):
        logging.debug("loading trace from file: %s", filename)
        signal_to_value = collections.OrderedDict()
        try:
            with open(filename, 'r') as f:
                for line in f:
                    name, val_as_string = line.strip().split()
                    signal_to_value[name] = float(val_as_string)
        except IOError:
            logging.exception("failed to open trace file: %s", filename)
            raise
        except Exception:
            logging.exception("an unexpected failure occurred when parsing trace file: %s", filename)  # noqa: pycodestyle
            raise
        trace = Trace(signal_to_value)
        logging.debug("loaded trace from file: %s", filename)
        return trace

    # type: (collections.OrderedDict) -> None
    def __init__(self, signal_to_value):
        self.__signal_to_value = signal_to_value

    # type: () -> List[float]
    @property
    def values(self):
        """
        Returns a list of the values for the signals belonging to this trace,
        in the order that they were reported by Valgrind.
        """
        return list(self.__signal_to_value.values())

    # type: () -> List[str]
    @property
    def signals(self):
        """
        Returns a list of the names of the signals contained within this trace.
        """
        return list(self.__signal_to_value.keys())

    # type: (str) -> None
    def to_file(filename):
        logging.debug("saving trace to file: %s", filename)
        contents = ["{}: {}".format(n, v) for (n, v)
                    in self.__signal_to_value.items()]
        try:
            with open(filename, 'w') as f:
                f.writelines(contents)
        except IOError:
            logging.exception("failed to write trace to file: %s", filename)
            raise
        except Exception:
            logging.exception("an unexpected failure occurred when saving trace file: %s", filename)  # noqa: pycodestyle
            raise
        logging.debug("saved trace to file: %s", filename)

    # type: (str) -> float
    def __getitem__(self, name_signal):
        """
        Fetches the value of a given signal.
        """
        return self.__signal_to_value[name_signal]
