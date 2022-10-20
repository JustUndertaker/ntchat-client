"""配置模块
"""
import os
from ipaddress import IPv4Address
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Optional, Set, Tuple, Union

from pydantic import BaseSettings, IPvAnyAddress
from pydantic.env_settings import (
    EnvSettingsSource,
    InitSettingsSource,
    SettingsError,
    SettingsSourceCallable,
    env_file_sentinel,
    read_env_file,
)

from .log import logger


class CustomEnvSettings(EnvSettingsSource):
    def __call__(self, settings: BaseSettings) -> dict[str, Any]:
        """
        Build environment variables suitable for passing to the Model.
        """
        d: dict[str, Optional[str]] = {}

        if settings.__config__.case_sensitive:
            env_vars: Mapping[str, Optional[str]] = os.environ  # pragma: no cover
        else:
            env_vars = {k.lower(): v for k, v in os.environ.items()}

        env_file_vars: dict[str, Optional[str]] = {}
        env_file = (
            self.env_file
            if self.env_file != env_file_sentinel
            else settings.__config__.env_file
        )
        env_file_encoding = (
            self.env_file_encoding
            if self.env_file_encoding is not None
            else settings.__config__.env_file_encoding
        )
        if env_file is not None:
            env_path = Path(env_file)
            if env_path.is_file():
                env_file_vars = read_env_file(
                    env_path,
                    encoding=env_file_encoding,  # type: ignore
                    case_sensitive=settings.__config__.case_sensitive,
                )
                env_vars = {**env_file_vars, **env_vars}

        for field in settings.__fields__.values():
            env_val: Optional[str] = None
            for env_name in field.field_info.extra["env_names"]:
                env_val = env_vars.get(env_name)
                if env_name in env_file_vars:
                    del env_file_vars[env_name]
                if env_val is not None:
                    break

            if env_val is None:
                continue

            if field.is_complex():
                try:
                    env_val = settings.__config__.json_loads(env_val)
                except ValueError as e:  # pragma: no cover
                    raise SettingsError(
                        f'error parsing JSON for "{env_name}"'  # type: ignore
                    ) from e
            d[field.alias] = env_val

        if env_file_vars:
            for env_name in env_file_vars.keys():
                env_val = env_vars[env_name]
                try:
                    if env_val:
                        env_val = settings.__config__.json_loads(env_val.strip())
                except ValueError:
                    logger.trace(
                        f"Error while parsing JSON for {env_name}. Assumed as string."
                    )

                d[env_name] = env_val

        return d


class BaseConfig(BaseSettings):
    if TYPE_CHECKING:
        # dummy getattr for pylance checking, actually not used
        def __getattr__(self, name: str) -> Any:  # pragma: no cover
            return self.__dict__.get(name)

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: InitSettingsSource,
            env_settings: EnvSettingsSource,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            common_config = init_settings.init_kwargs.pop("_common_config", {})
            return (
                init_settings,
                CustomEnvSettings(
                    env_settings.env_file, env_settings.env_file_encoding
                ),
                InitSettingsSource(common_config),
                file_secret_settings,
            )


class Env(BaseConfig):
    """运行环境配置。大小写不敏感。

    将会从 `环境变量` > `.env 环境配置文件` 的优先级读取环境信息。
    """

    environment: str = "prod"
    """当前环境名。

    将从 `.env.{environment}` 文件中加载配置。
    """

    class Config:
        extra = "allow"
        env_file = ".env"


class Config(BaseConfig):
    """主要配置"""

    _env_file: str = ".env"
    smart: bool = True
    """是否注入当前wechat"""
    host: IPvAnyAddress = IPv4Address("127.0.0.1")
    """http服务地址"""
    port: int = 8000
    """http服务端口"""
    http_post_url: str = ""
    """http post上报地址，如果不填则不上报"""
    ws_address: str = ""
    """反向ws连接地址，如果不填则不会连接ws"""
    access_token: str = ""
    """密钥"""
    log_level: Union[int, str] = "INFO"
    """默认日志等级"""
    log_days: int = 10
    """日志保存天数"""
    msg_filter: Set[int] = {}
    """事件过滤列表"""
    report_self: bool = False
    """是否上报自身消息"""
    cache_path: str = "./file_cache"
    """文件缓存目录"""
    cache_days: int = 3
    """文件缓存天数"""

    class Config:
        extra = "allow"
