import sys
from functools import partial
from pathlib import Path

import ntchat
from apscheduler.schedulers.blocking import BlockingScheduler

from ntchat_client.cache import scheduler_job
from ntchat_client.client import Client
from ntchat_client.config import Config, Env
from ntchat_client.log import default_filter, logger

_manager: Client = None
"""全局管理器"""


def init():
    """初始化"""
    global _manager
    if not _manager:
        env = Env()
        config = Config(_common_config=env.dict())
        default_filter.level = config.log_level
        logger.info(f"Current <y><b>Env: {env.environment}</b></y>")
        logger.debug(f"Loaded <y><b>Config</b></y>: {str(config.dict())}")
        logger.info("初始化ntchat_client...")
        Path(config.cache_path).mkdir(parents=True, exist_ok=True)
        _manager = Client(config)
        _manager.init()
        logger.debug("初始化定时器...")
        scheduler = BlockingScheduler()
        job = partial(scheduler_job, config)
        scheduler.add_job(func=job, trigger="cron", hour=0, minute=0)
        try:
            scheduler.start()
            logger.debug("定时器启动成功...")
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            ntchat.exit_()
            sys.exit()
