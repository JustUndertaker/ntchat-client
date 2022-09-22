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
        _manager = Client(config)
        _manager.init()
