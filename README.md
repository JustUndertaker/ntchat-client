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
```

