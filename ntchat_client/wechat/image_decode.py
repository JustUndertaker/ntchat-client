from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


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

        return out_file.absolute()
