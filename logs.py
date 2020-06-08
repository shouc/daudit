import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

WARN = logger.warning
INFO = logger.info
DEBUG = logger.debug
ERROR = logger.error
