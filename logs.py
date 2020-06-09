import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

INFO = logger.info
DEBUG = logger.debug
ERROR = logger.error
RECOMMENDATION = logger.debug
WARN = logger.warning

