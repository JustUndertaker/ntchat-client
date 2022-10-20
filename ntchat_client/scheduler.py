"""定时器模块
"""
from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ntchat_client.wechat.cache import scheduler_job

from .config import Config
from .log import logger

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


def scheduler_init(config: Config) -> None:
    """定时器初始化"""
    global scheduler
    if not scheduler.running:
        scheduler.start()
        scheduler.add_job(
            partial(scheduler_job, config), trigger="cron", hour=0, minute=0
        )
        logger.success("<g>定时器模块已开启...</g>")


def scheduler_shutdown() -> None:
    """定时器关闭"""
    logger.info("正在关闭定时器...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    logger.success("<g>定时器关闭成功...</g>")
