<h1 align="center">NtChat-Client</h1>

<p align="center">
	<a href="https://github.com/JustUndertaker/ntchat-client/releases"><img src="https://img.shields.io/badge/release-0.1.0-blue.svg?" alt="release"></a>   
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-brightgreen.svg?" alt="License"></a>
</p>

## 介绍

- ntchat的封装无头客户端，配合 [ntchat-adapter](https://github.com/JustUndertaker/adapter-ntchat) 实现和Nonebot2通信
- 微信pc hook，需求在windows端或者wine环境

## 上游依赖

- [ntchat](https://github.com/smallevilbeast/ntchat)：基于pc微信的api接口, 类似itchat项目

## 支持的微信版本

- [WeChat3.6.0.18](https://github.com/tom-snow/wechat-windows-versions/releases/download/v3.6.0.18/WeChatSetup-3.6.0.18.exe)：安装后请更改配置，修改host等操作关闭自动更新。

## 配置项

.env文件是项目配置文件

```dotenv
# 是否注入已开启进程
smart = True

# ws主动连接地址
ws_address = "ws://127.0.0.1:8080/ntchat/ws"

# access_token密钥
access_token = ""

# 日志显示等级
log_level = "DEBUG"

# 事件过滤列表，列表填tpye的数字
msg_filter = []

# 是否上报自身消息
report_self = False

# 文件缓存地址
cache_path = "./file_cache"

# 文件缓存天数
cache_days = 3
```

## 更新日志

#### 0.2.0

- 增加二维码扫描
- 增加文件缓存模块，拓展ntchat自身api中的file支持类型（支持filepath,url,base64）
- 增加定时模块用于处理文件缓存
- api调用file及file_path字段需要修改，目前支持：
  - 绝对路径，采用file_uri：file:///path
  - 网络路径，支持http和https，格式：http://或https://
  - base64，格式为：base64://values
