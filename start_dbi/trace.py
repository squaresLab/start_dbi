__all__ = ['Trace']

from typing import Optional
import logging
import collections
import tempfile
import os

from start_core.attack import Attack
from start_core.sitl import SITL
from start_core.scenario import Scenario
from start_core.mission import Mission
from start_core.test import execute as execute_mission

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)

VALGRIND_FLAGS_DEFAULT = \
    '--verbose --trace-children=yes --trace-children-skip=which,mavproxy,arduplane --tool=debgrind'
# VALGRIND_FLAGS_DEFAULT = \
#     '--tool=debgrind'
VALGRIND_BINARY_DEFAULT = '/opt/debgrind/bin/valgrind'


class Trace(object):
    """
    Describes a trace for a single execution of ArduPilot.
    """
    @staticmethod
    def generate(sitl,                                      # type: SITL
                 mission,                                   # type: Mission
                 timeout_mission,                           # type: int
                 timeout_connection=60,                     # type: int
                 timeout_liveness=15,                       # type: int
                 valgrind_binary=VALGRIND_BINARY_DEFAULT,   # type: str
                 valgrind_flags=VALGRIND_FLAGS_DEFAULT,     # type: str
                 attack=None                                # type: Optional[Attack]
                 ):                                         # type: (...) -> Trace
        """
        Executes a given mission using a specified ArduPilot binary and
        returns its execution trace.

        Parameters:
            binary: the ArduPilot binary that should be used.
            mission: the mission that should be executed.
            valgrind_binary: the path to the Valgrind binary.
            valgrind_flags: the Valgrind flags that should be passed to the SITL.
        """
        logger.debug("obtaining an execution trace for mission [%s]", mission)

        # NOTE this problem was with START, right?
        # The system was stripping off the initial slash, causing it not to
        # find the valgrind binary. This is a workaround.
        # if valgrind_binary.startswith('/'):
        #     valgrind_binary_old = valgrind_binary
        #     valgrind_binary = '/' + valgrind_binary
        #     logger.debug("adding leading slash to valgrind binary: %s -> %s",
        #                   valgrind_binary_old, valgrind_binary)

        # TODO optionally, allow a signal file to specified.
        fh_signals, fn_signals = tempfile.mkstemp('.signal', 'start')
        try:
            sitl_prefix = "{} --log-file='/tmp/valgrind.out' {} --output-file='{}'"
            sitl_prefix = sitl_prefix.format(valgrind_binary,
                                             valgrind_flags,
                                             fn_signals)
            logger.debug("using SITL prefix: %s", sitl_prefix)

            logger.debug("executing mission")
            (passed, reason) = execute_mission(sitl,
                                               mission,
                                               attack,
                                               speedup=1,
                                               prefix=sitl_prefix,
                                               timeout_mission=timeout_mission,
                                               timeout_liveness=timeout_liveness,
                                               timeout_connection=timeout_connection)
            logger.debug("finished executing mission")

            logger.debug("attempting to read signals file")
            trace = Trace.from_file(fn_signals)
            logger.debug("successfully read signals file")
        finally:
            os.remove(fn_signals)

        logger.debug("obtained execution trace for mission [%s]", mission)
        return trace

    # type: (str) -> Trace
    @staticmethod
    def from_file(filename):
        logger.debug("loading trace from file: %s", filename)
        signal_to_value = collections.OrderedDict()
        try:
            with open(filename, 'r') as f:
                for line in f:
                    name, val_as_string = line.strip().split()
                    signal_to_value[name] = float(val_as_string)
        except IOError:
            logger.exception("failed to open trace file: %s", filename)
            raise
        except Exception:
            logger.exception("an unexpected failure occurred when parsing trace file: %s", filename)  # noqa: pycodestyle
            raise
        trace = Trace(signal_to_value)
        logger.debug("loaded trace from file: %s", filename)
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
        logger.debug("saving trace to file: %s", filename)
        contents = ["{}: {}".format(n, v) for (n, v)
                    in self.__signal_to_value.items()]
        try:
            with open(filename, 'w') as f:
                f.writelines(contents)
        except IOError:
            logger.exception("failed to write trace to file: %s", filename)
            raise
        except Exception:
            logger.exception("an unexpected failure occurred when saving trace file: %s", filename)  # noqa: pycodestyle
            raise
        logger.debug("saved trace to file: %s", filename)

    # type: (str) -> float
    def __getitem__(self, name_signal):
        """
        Fetches the value of a given signal.
        """
        return self.__signal_to_value[name_signal]
