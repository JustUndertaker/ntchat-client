from .client import Client
from .config import Config, Env
from .log import logger

_manager: Client = None
"""全局管理器"""


def init():
    """初始化"""
    global _manager
    if not _manager:
        env = Env()
        config = Config(_common_config=env.dict())
        logger.info(f"Current <y><b>Env: {env.environment}</b></y>")
        logger.debug(f"Loaded <y><b>Config</b></y>: {str(config.dict())}")
        logger.info("初始化ntchat...")
        _manager = Client(config)
        _manager.init()
