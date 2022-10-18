import sys
from functools import partial
from pathlib import Path

import ntchat
from apscheduler.schedulers.blocking import BlockingScheduler

from ntchat_client.cache import scheduler_job
from ntchat_client.client import Client
from ntchat_client.config import Config, Env
from ntchat_client.log import default_filter, log_init, logger


def tick():
    logger.trace("心跳tick事件...")


def init():
    """初始化"""

    env = Env()
    config = Config(_common_config=env.dict())
    default_filter.level = config.log_level
    log_init(config.log_days)
    logger.info(f"Current <y><b>Env: {env.environment}</b></y>")
    logger.debug(f"Loaded <y><b>Config</b></y>: {str(config.dict())}")
    logger.info("初始化ntchat_client...")
    Path(config.cache_path).mkdir(parents=True, exist_ok=True)
    ntchat_client = Client(config)
    ntchat_client.init()
    logger.debug("初始化定时器...")
    scheduler = BlockingScheduler()
    job = partial(scheduler_job, config)
    scheduler.add_job(func=job, trigger="cron", hour=0, minute=0)
    scheduler.add_job(func=tick, trigger="interval", seconds=3)
    logger.debug("定时器启动成功...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        ntchat.exit_()
        sys.exit()
