from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    """api 响应"""

    echo: str
    """echo值"""
    status: str
    """状态值"""
    msg: str
    """回复消息"""
    data: Any
    """返回数据"""
