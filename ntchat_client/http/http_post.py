"""http_post上报
"""
from httpx import AsyncClient

from ntchat_client.config import Config
from ntchat_client.log import logger
from ntchat_client.wechat import get_wechat_client

post_manager: "PostManager"
"""全局post管理器"""


def post_init(config: Config) -> None:
    """初始化"""
    global post_manager
    logger.info("正在初始化http_post...")
    wechat_client = get_wechat_client()
    self_id = wechat_client.self_id
    post_manager = PostManager(self_id, config)
    wechat_client.http_post_handler = post_manager.post_respone
    logger.success("<m>http_post</m> - <g>http_post初始化完成...</g>")


class PostManager:
    """用于处理http_post"""

    client: AsyncClient
    """客户端"""
    url: str
    """post地址"""

    def __init__(self, self_id: str, config: Config) -> None:
        headers = {
            "X-Self-ID": self_id,
            "access_token": config.access_token,
            "Content-Type": "application/json",
        }
        self.client = AsyncClient(headers=headers)
        self.url = config.http_post_url

    async def post_respone(self, data: dict) -> None:
        """
        上报消息
        """
        if self.url == "":
            return

        try:
            logger.debug(f"<m>http_post</m> - <e>向http_post上报消息：</e>{data}")
            response = await self.client.post(url=self.url, json=data)
            logger.debug(
                f"<m>http_post</m> - <e>向http_post上报结果：</e>{response.status_code}"
            )
        except Exception as e:
            logger.error(f"<m>http_post</m> - http_post上报消息出错：<r>{str(e)}</r>")
