"""Application Logger module

Good practice reminder:
    CRITICAL to log and halt the rest of the flow, specially to prevent data or security loss (i.e.: offline database)
    ERROR to log if parts of the app stop its current operation (i.e.: a transient API or DB connection error)
    WARNING to log abnormal conditions that are not errors but need attention (i.e: a delay in storing data)
    INFO to log high-level decisions, or significant steps in normal execution (i.e: refusing an invalid input)
    DEBUG are for system flow traceability and specially dev trace and checkpoints in the flow
"""
import logging
from json import dumps
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from pathlib import Path
from tempfile import gettempdir
from time import gmtime


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):  # noqa: D102
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=Singleton):
    """The Logger class

    This class uses Singleton pattern.
    """

    def __init__(
            self,
            name: str = 'project', log_level: str = 'INFO', logs_dir: Path = f'/{gettempdir()}/project',
            rotated_files: int = 9, rotation_mb: float = 9,
            cid: str = None, enable_stdout_logs: bool = True,
    ):
        name = name.replace(' ', '-').lower()

        logs_dir.mkdir(parents=True, exist_ok=True)
        log_filepath = logs_dir / f'{name}.log'

        rotation_bytes = int(1024 * 1024 * rotation_mb)

        self.cid = cid

        _logger = logging.getLogger(name)
        _logger.setLevel(log_level)

        fh = RotatingFileHandler(log_filepath, maxBytes=rotation_bytes, backupCount=rotated_files)
        fh.namer = self._namer
        _logger.addHandler(fh)

        if enable_stdout_logs:
            sh = StreamHandler()
            _logger.addHandler(sh)

        self._logger = None
        self.logger = _logger

        self._level = None
        self.level = log_level

        if enable_stdout_logs:
            log_int = logging.getLevelName(self.level)
            self.logger.log(
                log_int + 10, 'Logs{} will be stored in UTC timezone at {}'.format(
                    f' for cid #{cid}' if cid else '', log_filepath,
                ),
            )

        self.logger.log(10, 'I will rotate {} log files, at {} bytes'.format(rotated_files, rotation_bytes))

    @property
    def logger(self) -> logging:
        """The actual logging property to be used all around."""
        return self._logger

    @logger.setter
    def logger(self, logger: logging):
        self._logger = logger

    @property
    def level(self) -> str:
        """Fetch current log level"""
        return self._level

    @level.setter
    def level(self, log_level):
        """Set a log level

        Args:
            log_level (str): One of "DEBUG", "INFO", or "WARNING"

        Notes:
            DEBUG and ERROR are minimum and maximum levels.
            Values not "DEBUG", "INFO", or "WARNING" will be ignored.
            Fallback level is fetched from config, .env and env vars.
        """
        log_int = logging.getLevelName(log_level)
        if not isinstance(log_int, int):
            log_int = logging.getLevelName(self.level)

        log_int = min(max(logging.DEBUG, log_int), logging.WARNING)
        self._level = logging.getLevelName(log_int)

        for handler in self.logger.handlers:
            handler.setLevel((log_int + 10) if type(handler) is StreamHandler else log_int)
            self._apply_log_format(handler, self.cid)

        for handler in self.logger.handlers:
            self.logger.log(
                log_int, '{} logs set to log from the {} level'.format(
                    type(handler).__name__, logging.getLevelName(handler.level),
                ),
            )

    @staticmethod
    def _apply_log_format(handler, cid=None):
        if type(handler) is StreamHandler:
            formatter = logging.Formatter('%(name)s [%(levelname)s] %(message)s')

        else:
            log_format = {'cid': cid, 'ts': '%(asctime)s', 'log': '%(levelname)s', 'msg': '%(message)s'}
            log_format = dumps(log_format)
            formatter = logging.Formatter(f'{log_format},')
            formatter.converter = gmtime

        handler.setFormatter(formatter)

    @staticmethod
    def _namer(name) -> str:  # noqa: D102, D205
        """Set log (and rotated log files) to have *.N.log as suffix, instead of *.log.N.
        i.e.: project-name.log.1 (logging standard) becomes project-name.1.log
        """
        return name.replace('.log', '') + '.log'
