import logging

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


class Model(object):
    # type: (str) -> Model
    @staticmethod
    def from_file(filename):
        # NOTE this may require mode 'rb' if the file is in a binary format
        with open(filename, 'r') as f:
            # TODO unpack
            raise NotImplementedError

    # type: (str) -> None
    def to_file(filename):
        raise NotImplementedError
