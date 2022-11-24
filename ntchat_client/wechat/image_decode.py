from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

from ntchat_client.config import Config
from ntchat_client.log import logger


@dataclass
class FileTypes:
    """文件格式"""

    file_type: str
    """格式后缀"""
    key: int
    """密钥"""


class FileDecoder:
    """文件解密类"""

    file_map: dict[str, tuple[int, int]] = {
        "jpg": (0xFF, 0xD8),
        "png": (0x89, 0x50),
        "gif": (0x47, 0x49),
    }
    out_image_dir: Path
    """输出文件夹"""
    out_image_thumb: Path
    """缩略图输出文件夹"""

    def __init__(self, image_path: str) -> None:
        self.out_image_dir = Path(image_path) / "image"
        self.out_image_thumb = Path(image_path) / "thumb"
        self.out_image_dir.mkdir(parents=True, exist_ok=True)
        self.out_image_thumb.mkdir(parents=True, exist_ok=True)

    def get_file_type(self, byte0: int, byte1: int) -> Optional[FileTypes]:
        """获取文件格式及密钥"""
        for type, value in self.file_map.items():
            result0 = value[0] ^ byte0
            result1 = value[1] ^ byte1
            if result0 == result1:
                return FileTypes(type, result0)
        return None

    def decode_file(self, image_file: Path, is_thumb: bool) -> Optional[str]:
        """
        说明:
            解密微信图片文件，并返回新的文件地址

        参数:
            * `image_file`：dat文件路径
            * `is_thumb`：是否为缩略图

        返回:
            * `str`：解密文件路径
        """
        file_value = np.fromfile(image_file, dtype=np.uint8)
        file_type = self.get_file_type(file_value[0], file_value[1])
        if file_type is None:
            return None
        xor_array = np.full_like(file_value, fill_value=file_type.key)
        out_value = np.bitwise_xor(file_value, xor_array)
        if is_thumb:
            out_file = self.out_image_thumb / f"{image_file.stem}.{file_type.file_type}"
        else:
            out_file = self.out_image_dir / f"{image_file.stem}.{file_type.file_type}"
        with open(out_file, mode="wb") as f:
            f.write(out_value)

        return str(out_file.absolute())


def scheduler_image_job(config: Config) -> None:
    """定时清理"""
    path = Path(config.image_path)
    days = timedelta(days=config.cache_days)
    if days == 0:
        return
    logger.info("<m>wechat</m> - 开始清理解密图片文件...")
    now = datetime.now()
    count = 0
    delete_count = 0
    image_path = path / "image"
    thumb_path = path / "thumb"
    for file in image_path.iterdir():
        count += 1
        file_info = file.stat()
        file_time = datetime.fromtimestamp(file_info.st_ctime)
        if now > file_time + days:
            file.unlink()
            delete_count += 1
    for file in thumb_path.iterdir():
        count += 1
        file_info = file.stat()
        file_time = datetime.fromtimestamp(file_info.st_ctime)
        if now > file_time + days:
            file.unlink()
            delete_count += 1
    logger.debug(f"<m>wechat</m> - 共有解密图片文件 {count} 个，清理 {delete_count} 个...")
    logger.info("<m>wechat</m> - 解密图片文件清理完毕...")
