from typing import NoReturn

import ntchat

from ntchat_client.config import Config
from ntchat_client.log import logger
from ntchat_client.utils import notify

from .cache import FileCache
from .qrcode import draw_qrcode

wechat_client: "WeChatManager" = None
"""全局微信客户端"""


def get_wechat_client() -> "WeChatManager":
    """获取微信客户端"""
    if wechat_client is None:
        raise RuntimeError("客户端不存在！")
    return wechat_client


def wechat_init(config: Config) -> None:
    """微信初始化"""
    global wechat_client
    wechat_client = WeChatManager(config)
    wechat_client.init()


def wechat_shutdown() -> None:
    """关闭微信模块"""
    if wechat_client:
        logger.info("正在关闭微信注入...")
        ntchat.exit_()
        logger.info("微信注入已关闭...")


class WeChatManager:
    """微信封装类"""

    client: ntchat.WeChat
    """客户端"""
    self_id: str
    """自身id"""
    file_cache: FileCache
    """文件缓存管理器"""
    msg_fiter = {
        ntchat.MT_USER_LOGIN_MSG,
        ntchat.MT_USER_LOGOUT_MSG,
        ntchat.MT_RECV_WECHAT_QUIT_MSG,
        ntchat.MT_RECV_LOGIN_QRCODE_MSG,
    }
    """消息过滤列表"""

    def __new__(cls, *args, **kwargs):
        """单例"""
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(
                cls,
            )
        return cls._instance

    def __init__(self, config: Config) -> None:
        self.config = config
        self.file_cache = FileCache(config.cache_path)
        self.msg_fiter |= config.msg_filter
        ntchat.set_wechat_exe_path(wechat_version="3.6.0.18")

    def init(self) -> None:
        """初始化"""
        self.wechat = ntchat.WeChat()
        logger.info("正在hook微信...")
        self.wechat.open(smart=self.config.smart)
        self.wechat.on(ntchat.MT_USER_LOGIN_MSG, self.login)
        self.wechat.on(ntchat.MT_USER_LOGOUT_MSG, self.logout)
        self.wechat.on(ntchat.MT_RECV_WECHAT_QUIT_MSG, self.quit)
        self.wechat.on(ntchat.MT_RECV_LOGIN_QRCODE_MSG, self.login_qrcode)

    def login(self, _: ntchat.WeChat, message: dict) -> None:
        """
        登入hook
        """
        notify.acquire()
        logger.info("hook微信成功！")
        self.self_id = message["data"]["wxid"]
        notify.notify_all()
        notify.release()

    def logout(self, _: ntchat.WeChat, message: dict) -> None:
        """
        登出hook
        """
        logger.error("检测到微信登出...")

    def quit(self, _: ntchat.WeChat) -> NoReturn:
        """
        微信退出
        """
        logger.error("检测到微信退出，终止程序...")
        raise SystemExit()

    def login_qrcode(self, _: ntchat.WeChat, message: dict) -> None:
        """
        登录二维码
        """
        # 将二维码显示在终端
        url = message["data"]["code"]
        logger.info("检测到登录二维码...")
        draw_qrcode(url)
