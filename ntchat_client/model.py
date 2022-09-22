from pydantic import BaseModel


class Response(BaseModel):
    """api 响应"""

    echo: str
    """echo值"""
    status: int
    """状态码"""
    msg: str
    """回复消息"""
    data: dict
    """返回数据"""
