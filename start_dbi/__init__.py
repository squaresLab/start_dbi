"""
This package provides an interface to START's DBI module.
"""
import logging

from start_core.scenario import Scenario

from .model import Model

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


# type: (Scenario) -> Model
def learn(scenario):
    raise NotImplementedError
