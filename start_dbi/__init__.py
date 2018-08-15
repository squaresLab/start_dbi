"""
This package provides an interface to START's DBI module.
"""
import logging
import collections

from start_core.scenario import Scenario
from start_core.mission import Mission

from .model import Model

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


class Trace(object):
    """
    Describes a trace for a single execution of ArduPilot.
    """
    # type: (str) -> Trace
    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as f:
            signals = {line.strip().split() for line in f}

    # type: (collections.OrderedDict) -> None
    def __init__(self, signal_to_value):
        self.__signal_to_value = signal_to_value

    # type: (str) -> None
    def to_file(filename):
        contents = ["{}: {}".format(n, v) for (n, v)
                    in self.__signal_to_value.items()]
        with open(filename, 'w') as f:
            f.writelines(contents)

    # type: (str) -> float
    def __getitem__(self, name_signal):
        """
        Fetches the value of a given signal.
        """
        return self.__signal_to_value[name_signal]


# type: (Scenario, List[Mission]) -> Model
def learn(scenario, missions):
    raise NotImplementedError
