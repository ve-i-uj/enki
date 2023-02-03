"""
Сервер для прослушиваня 255.255.255.255:20086 и храния онлайн статистики
компонентов.
"""

import logging


from tools.supervisor import settings
from enki.misc import log

logger = logging.getLogger(__name__)


def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    logger.info('Done')


if __name__ == '__main__':
    main()
