"""http_api调用
"""
from fastapi import APIRouter

from ntchat_client.wechat import get_wechat_client

router = APIRouter()


@router.post("/")
async def _() -> None:
    pass
