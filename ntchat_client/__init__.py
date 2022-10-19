from functools import partial

from ntchat_client.config import Config, Env
from ntchat_client.driver import Driver
from ntchat_client.http import router
from ntchat_client.log import default_filter, log_init, logger
from ntchat_client.scheduler import scheduler_init, scheduler_shutdown
from ntchat_client.utils import notify
from ntchat_client.websocket import websocket_init, websocket_shutdown
from ntchat_client.wechat import get_wechat_client, wechat_init, wechat_shutdown

_Driver: Driver = None
"""全局后端"""


def init() -> None:
    """初始化"""
    global _Driver

    env = Env()
    config = Config(_common_config=env.dict())
    default_filter.level = config.log_level
    log_init(config.log_days)
    logger.info(f"Current <y><b>Env: {env.environment}</b></y>")
    logger.debug(f"Loaded <y><b>Config</b></y>: {str(config.dict())}")
    # 登录微信
    wechat_init(config)
    wait_for_login()
    # 添加api
    _Driver = Driver(config)
    app = _Driver.server_app
    app.include_router(router)
    # 添加定时清理任务
    _Driver.on_startup(partial(scheduler_init, config))
    # 添加websocket连接任务
    _Driver.on_startup(partial(websocket_init, config))
    # 添加关闭任务
    _Driver.on_shutdown(scheduler_shutdown)
    _Driver.on_shutdown(websocket_shutdown)
    _Driver.on_shutdown(wechat_shutdown)

    # 启动进程
    _Driver.run()


def wait_for_login() -> None:
    """等待登录成功"""
    if notify.acquire():
        wechat_client = get_wechat_client()
        if wechat_client.wechat.login_status:
            notify.release()
            return
        notify.wait()
