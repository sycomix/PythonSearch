import logging
import sys


def setup_inference_logger():
    logger = logging.getLogger("inference_logger")

    # fh = logging.FileHandler("/tmp/inference.txt")
    # fh.setLevel(logging.WARNING)
    # logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    logger.setLevel(logging.INFO)

    return logger


def setup_preview_logger():
    """
    Only writes to file
    """
    logger = logging.getLogger("preview")
    fh = logging.FileHandler("/tmp/preview.txt")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger


def setup_run_key_logger():
    """
    Code has to be fast
    """
    logger = logging.getLogger("run-key")
    # fh = logging.FileHandler("/tmp/run_key.txt")
    # fh.setLevel(logging.DEBUG)
    # logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    logger.addHandler(ch)

    logger.setLevel(logging.INFO)

    return logger


def setup_generic_stdout_logger():
    logger = logging.getLogger("stdoutlogger")

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    logger.setLevel(logging.INFO)

    return logger


def interpreter_logger():
    logger = logging.getLogger("interpeter_logger")
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    logger.addHandler(ch)

    fh = logging.FileHandler(f"/tmp/debug_interpreter")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    return logger


def setup_data_writter_logger(event_name):
    logger = logging.getLogger(f"data-writer_{event_name}")

    fh = logging.FileHandler(f"/tmp/data-writer_event_{event_name}")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    logger.setLevel(logging.WARNING)

    return logger


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass
