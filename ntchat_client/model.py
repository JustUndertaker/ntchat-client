from typing import Any

from pydantic import BaseModel


class WsRequest(BaseModel):
    """websocket api 请求"""

    echo: str
    """echo值"""
    action: str
    """请求方法"""
    params: dict
    """请求参数"""


class WsResponse(BaseModel):
    """websocket api 响应"""

    echo: str
    """echo值"""
    status: str
    """状态值"""
    msg: str
    """回复消息"""
    data: Any
    """返回数据"""
