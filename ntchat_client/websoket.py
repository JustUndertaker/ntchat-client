import asyncio
import json
import sys
from typing import Optional

import ntchat
import websockets
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.legacy.client import WebSocketClientProtocol

from .client import Client
from .config import Config
from .log import logger


class Message(BaseModel):
    type: str
    """api名称"""
    data: dict
    """api参数"""


class WebSoketManager:
    """ws管理端"""

    connect: Optional[WebSocketClientProtocol] = None
    """ws链接"""
    wechat: Optional[Client] = None
    """微信客户端"""
    ws_address: str
    access_token: str

    def __init__(self, config: Config):
        self.ws_address = config.ws_address
        self.access_token = config.access_token
        self.wechat = Client(config.smart)
        self.wechat.on_message(self.get_post_message)
        asyncio.run(self.connect())

    async def connect(self):
        """连接到ws"""
        headers = {"access_token": self.access_token}
        while True:
            try:
                logger.debug(f"正在连接到：{self.ws_address}")
                self.connect = await websockets.connect(
                    uri=self.ws_address,
                    extra_headers=headers,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=10,
                )
                asyncio.create_task(self.task())
            except Exception as e:
                logger.error(f"连接到 {self.ws_address} 发生错误：{str(e)}")
                await asyncio.sleep(3)

            except KeyboardInterrupt:
                ntchat.exit_()
                sys.exit()

    async def task(self):
        """
        说明:
            循环等待ws接受并分发任务
        """
        try:
            while True:
                msg = await self.connect.recv()
                asyncio.create_task(self.handle_msg(msg))

        except ConnectionClosedOK | ConnectionClosedError:
            logger.debug("ws远程服务器已关闭！")
            self.connect = None
            await self.connect()

    async def handle_msg(self, msg: str):
        """处理ws消息"""
        try:
            message = Message.parse_obj(json.loads(msg))
            logger.debug(f"ws接收消息：{msg}")
            self.wechat.call_api(api=message.type, **message.data)

        except ValidationError:
            logger.error(f"收到未知消息：{msg}")
        except Exception as e:
            logger.error(str(e))

    def get_post_message(self, _: ntchat.WeChat, message: dict):
        """接收消息回调"""
        asyncio.create_task(self.post_message(json.dumps(message)))

    async def post_message(self, message: str):
        """发送消息"""
        if self.connect:
            logger.debug(f"ws推送消息：{message}")
            await self.connect.send(message)
