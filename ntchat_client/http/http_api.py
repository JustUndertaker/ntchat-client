"""http_api调用
"""
from fastapi import APIRouter

from ntchat_client.wechat import wechat_client

router = APIRouter()


@router.post("/")
async def _() -> None:
    pass
