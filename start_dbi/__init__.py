"""
This package provides an interface to START's DBI module.
"""
import logging

import numpy as np
from start_core.scenario import Scenario
from start_core.mission import Mission

from .trace import Trace
from .model import Model

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


# type: (Scenario, List[Mission]) -> Model
def learn(scenario, missions):
    raise NotImplementedError


# type: (List[Trace]) -> Model
def train(traces):
    matrix = np.array([t.values for t in traces])
