"""Configures logging of python scripts."""

import logging
import re

from assetsapi.kbeapi.baseapp import KBEngine

__all__ = ['setup', 'set_module_log_level']


# time and level will set by logger of KBEngine
_FORMAT = '[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
_DEFAULT_LOG_LEVEL = logging.DEBUG


class _Py2KBELogHandler(logging.Handler):
    """
    Handler for transferring log messages from the python log system
    to the KBE log system.

    If you send messages to logging.StreamHandler (sys.stdout)
    then the process fails. Therefore, it is simply passed to print
    """

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)

        self._KBE_LOG_FUNC_MAP = {
            logging.NOTSET: self._trace_msg,
            logging.DEBUG: self._debug_msg,
            logging.INFO: self._info_msg,
            logging.WARNING: self._warning_msg,
            logging.ERROR: self._error_msg,
            logging.CRITICAL: self._error_msg
        }

    def emit(self, record):
        msg = self.format(record)
        kbe_log_func = self._KBE_LOG_FUNC_MAP[record.levelno]
        kbe_log_func(msg)

    @staticmethod
    def _trace_msg(msg):
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_NORMAL)
        print(msg)

    @staticmethod
    def _debug_msg(msg):
        if KBEngine.component == 'bots' or KBEngine.publish() == 0:
            KBEngine.scriptLogType(KBEngine.LOG_TYPE_DBG)
            print(msg)

    @staticmethod
    def _info_msg(msg):
        if KBEngine.component == 'bots' or KBEngine.publish() <= 1:
            KBEngine.scriptLogType(KBEngine.LOG_TYPE_INFO)
            print(msg)

    @staticmethod
    def _warning_msg(msg):
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_WAR)
        print(msg)

    @staticmethod
    def _error_msg(msg):
        KBEngine.scriptLogType(KBEngine.LOG_TYPE_ERR)
        print(msg)


def set_module_log_level(pack_or_module_name, level):
    """Set the logging level for a module or a package.

    The path is passed in the format npc.module_name or npc.package_name
    relative to cell or base component.
    """
    root_logger = logging.getLogger()
    patt = re.compile(f'^{pack_or_module_name}(\.|$)')
    for name, logger in logging.root.manager.loggerDict.items():
        if not isinstance(logger, logging.Logger):
            continue
        if patt.match(name) is not None:
            logger.setLevel(level)
            root_logger.info('The logger of the module `%s` was set level `%s`',
                             logger, logging.getLevelName(level))


def setup():
    """Configures the log system.

    Should be run from kbemain.py when app starts.
    """
    handler = _Py2KBELogHandler()
    formatter = logging.Formatter(_FORMAT)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(_DEFAULT_LOG_LEVEL)

    root_logger.info('Root logger has configured (level = %s)',
                     logging.getLevelName(root_logger.level))
