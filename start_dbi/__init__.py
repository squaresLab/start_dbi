"""
This package provides an interface to START's DBI module.
"""
import logging
import collections

import numpy as np
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
        signal_to_value = collections.OrderedDict()
        with open(filename, 'r') as f:
            for line in f:
                name, val_as_string = line.strip().split()
                signal_to_value[name] = float(val_as_string)
        return Trace(signal_to_value)

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


# type: (List[Trace]) -> Model
def train(traces):
    matrix = np.array([t.values for t in traces])
