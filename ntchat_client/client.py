import json
import sys
import time

import ntchat
import websocket

from .config import Config
from .log import logger
from .model import Response
from .utils import escape_tag


class Client:

    wechat: ntchat.WeChat
    """微信实例"""
    connect: websocket.WebSocketApp
    """链接实例"""
    config: Config
    """配置"""
    is_connected: bool = False
    """是否已连接"""
    self_id: str
    """微信id"""
    msg_fiter = {
        ntchat.MT_USER_LOGIN_MSG,
        ntchat.MT_USER_LOGOUT_MSG,
        ntchat.MT_RECV_WECHAT_QUIT_MSG,
        ntchat.MT_RECV_LOGIN_QRCODE_MSG,
    }
    """消息过滤列表"""

    def __init__(self, config: Config):
        self.config = config
        self.msg_fiter |= config.msg_filter
        ntchat.set_wechat_exe_path(wechat_version="3.6.0.18")

    def init(self):
        """
        初始化
        """
        self.wechat = ntchat.WeChat()
        logger.info("正在hook微信...")
        self.wechat.open(smart=self.config.smart)
        self.wechat.on(ntchat.MT_USER_LOGIN_MSG, self.login)
        self.wechat.on(ntchat.MT_USER_LOGOUT_MSG, self.logout)
        self.wechat.on(ntchat.MT_RECV_WECHAT_QUIT_MSG, self.quit)
        if not self.config.smart:
            logger.info("未开启smart，正在注入登录事件...")
            self.wechat.on(ntchat.MT_RECV_LOGIN_QRCODE_MSG, self.login_qrcode)

    def login_qrcode(self, _: ntchat.WeChat, message: dict):
        """
        登录二维码
        """
        # 将二维码显示在终端
        pass

    def quit(self, _: ntchat.WeChat, message: dict):
        """
        微信退出
        """
        logger.error("检测到微信退出，终止程序...")
        if self.is_connected:
            self.connect.close()
        ntchat.exit_()
        sys.exit()

    def login(self, _: ntchat.WeChat, message: dict):
        """
        登入hook
        """
        logger.info("hook微信成功！")
        self.self_id = message["data"]["wxid"]
        self.wechat.on(ntchat.MT_ALL, self.hook_message)
        self.connect_ws()

    def logout(self, _: ntchat.WeChat, message: dict):
        """
        登出hook
        """
        logger.error("检测到微信登出，正在想办法重启...")
        self.connect.close()
        ntchat.exit_()
        self.wechat = ntchat.WeChat()
        time.sleep(3)
        self.init()

    def connect_ws(self):
        """链接服务器"""
        header = {"access_token": self.config.access_token, "X-Self-ID": self.self_id}
        self.connect = websocket.WebSocketApp(
            url=self.config.ws_address,
            header=header,
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error,
            on_open=self.on_open,
        )
        try:
            while True:
                logger.info(f"正在链接到：{self.connect.url}")
                if not self.connect.run_forever(
                    ping_interval=10,
                    ping_timeout=5,
                ):
                    break
                time.sleep(2)
        except KeyboardInterrupt:
            ntchat.exit_()
            sys.exit()

    def on_open(self, _: websocket.WebSocketApp):
        """链接成功"""
        logger.info("ws已成功链接！")
        self.is_connected = True

    def on_error(self, _: websocket.WebSocketApp, err):
        """链接出错"""
        logger.error(str(err))

    def on_message(self, _: websocket.WebSocketApp, message: str):
        """接受消息"""
        try:
            logger.debug(f"收到消息：{escape_tag(message)}")
            msg: dict = json.loads(message)
            echo = msg.get("echo")
            action = msg.get("action")
            params = msg.get("params")
            attr = getattr(self.wechat, action, None)
            if not attr:
                # 返回方法不存在错误
                logger.error(f"接口不存在：{action}")
                response = Response(
                    echo=echo, status="failed", msg=f"调用出错，不存在接口：{action}！", data={}
                )
            else:
                try:
                    logger.debug(f"调用接口：{action}，参数：{params}")
                    result = attr(**params)
                    response = Response(
                        echo=echo, status="success", msg="调用成功", data=result
                    )
                except Exception as e:
                    response = Response(
                        echo=echo, status="failed", msg=f"调用出错：{repr(e)}", data={}
                    )
            json_data = json.dumps(response.dict(), ensure_ascii=False)
            logger.info(f"返回结果：{escape_tag(json_data)}")
            self.connect.send(json_data)
        except Exception as e:
            logger.debug(f"接收消息出错:{repr(e)}")

    def on_close(self, _: websocket.WebSocketApp, code: int, msg: str):
        """关闭连接"""
        self.is_connected = False
        if code and code != 1000:
            logger.debug(f"ws关闭code:{code}，msg:{msg}")
            self.connect_ws()

    def hook_message(self, _: ntchat.WeChat, message: dict):
        """hook消息"""
        # 过滤事件
        msgtype = message["type"]
        if msgtype in self.msg_fiter:
            return
        data = json.dumps(message, ensure_ascii=False)
        if self.is_connected:
            wx_id = message["data"].get("from_wxid")
            if wx_id == self.self_id and not self.config.report_self:
                return
            logger.info(f"向ws发送消息：{escape_tag(data)}")
            self.connect.send(data)
        else:
            logger.info(f"未找到ws链接，无法发送：{escape_tag(data)}...")
