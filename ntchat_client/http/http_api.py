"""http_api调用
"""
from fastapi import APIRouter, Response

from ntchat_client.model import HttpParams, HttpRequest, HttpResponse
from ntchat_client.wechat import get_wechat_client

router = APIRouter()


@router.post("/{action}", response_model=HttpResponse)
async def _(action: str, params: HttpParams, response: Response) -> None:
    """处理api调用"""
    # 构造请求体
    http_request = HttpRequest(action=action, params=params.dict())
    wechat_client = get_wechat_client()
    res = wechat_client.handle_api(http_request)
    self_id = wechat_client.self_id
    access_token = wechat_client.config.access_token
    response.headers["X-self-ID"] = self_id
    response.headers["access_token"] = access_token

    return res
