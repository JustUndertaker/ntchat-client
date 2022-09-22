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

    def __init__(self, config: Config):
        self.config = config
        # ntchat.set_wechat_exe_path(wechat_version="3.6.0.18")
        self.wechat = ntchat.WeChat()
        logger.info("正在hook微信...")
        self.wechat.open(smart=self.config.smart)

    def init(self):
        """初始化"""
        count = 0
        while not self.wechat.login_status:
            count += 1
            if count > 100:
                raise RuntimeError("hook微信失败！")
            time.sleep(1)
        logger.info("hook微信成功！")
        message = self.wechat.get_self_info()
        self.self_id = message["wxid"]
        self.wechat.on(ntchat.MT_ALL, self.hook_message)
        self.connect_ws()

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
                response = Response(echo=echo, status=404, msg="该接口不存在！", data={})
            else:
                try:
                    result: dict = attr(params)
                    response = Response(
                        echo=echo, status=200, msg="调用成功", data=result["data"]
                    )
                except Exception as e:
                    response = Response(
                        echo=echo, status=405, msg=f"调用出错{repr(e)}", data={}
                    )
            json_data = json.dumps(response.dict())
            self.connect.send(json_data)
        except Exception as e:
            logger.debug(f"接收消息出错:{repr(e)}")

    def on_close(self, _: websocket.WebSocketApp, code: int, msg: str):
        """关闭连接"""
        self.is_connected = False
        if code:
            logger.debug(f"ws关闭code:{code}，msg:{msg}")
            self.connect_ws()

    def hook_message(self, _: ntchat.WeChat, message: dict):
        """hook消息"""
        data = json.dumps(message)
        if self.is_connected:
            wx_id = message["data"].get("from_wxid")
            if wx_id == self.self_id and not self.config.report_self:
                return
            logger.info(f"向ws发送消息：{escape_tag(data)}")
            data = json.dumps(message)
            self.connect.send(data)
        else:
            logger.info(f"未找到ws链接，无法发送：{escape_tag(data)}...")
