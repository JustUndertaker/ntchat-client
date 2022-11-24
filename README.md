<h1 align="center">NtChat-Client</h1>

<p align="center">
	<a href="https://github.com/JustUndertaker/ntchat-client/releases"><img src="https://img.shields.io/badge/release-0.3.2-blue.svg?" alt="release"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-brightgreen.svg?" alt="License"></a>
</p>

## 介绍

- ntchat的封装无头客户端，配合 [ntchat-adapter](https://github.com/JustUndertaker/adapter-ntchat) 实现和Nonebot2通信
- 微信pc hook，需求在windows端或者wine环境

## 上游依赖

- [ntchat](https://github.com/smallevilbeast/ntchat)：基于pc微信的api接口, 类似itchat项目

## 支持的微信版本

- [WeChat3.6.0.18](https://github.com/tom-snow/wechat-windows-versions/releases/download/v3.6.0.18/WeChatSetup-3.6.0.18.exe)：安装后请更改配置，修改hosts等操作关闭自动更新。
- hosts文件添加：127.0.0.1 		dldir1.qq.com

## 配置项

.env文件是项目配置文件

```dotenv
# 是否注入已开启微信进程
smart = True

# http api 地址
host = 127.0.0.1

# http api 端口
port = 8000

# http post上报地址，不填不会进行上报
http_post_url = ""

# ws主动连接地址，不填不会主动连接ws
ws_address = ""

# access_token验证密钥
access_token = ""

# 日志显示等级
log_level = "DEBUG"

# 日志保存天数
log_days = 10

# 事件过滤列表，列表填tpye的数字
msg_filter = []

# 是否上报自身消息
report_self = False

# 文件缓存地址
cache_path = "./file_cache"

# 文件缓存天数，为0则不清理缓存
cache_days = 3

# 聊天图片解密地址
image_path = "./image_decode"

# 聊天解密图片保存天数，为0则不清理缓存
image_days = 0

# 下载pc图片超时时间(s)，超时的图片不会解密
image_timeout = 30

# 超时的图片消息是否继续发送
timeout_image_send = False
```

## 与Nonebot2通信

目前支持反向websocket通信和http post通信

### 使用反向websocket

需要修改配置项：

```dotenv
# ws主动连接地址，不填不会主动连接ws
ws_address = "127.0.0.1:8080/ntchat/ws"
```

- 这里127.0.0.1与nb2的host配置对应
- 这里8080与nb2的port配置对应

### 使用http post

需要修改配置项：

```dotenv
# http post上报地址，不填不会进行上报
http_post_url = "http://127.0.0.1:8080/ntchat/http"
```

- 这里127.0.0.1与nb2的host配置对应
- 这里8080与nb2的port配置对应

<details>
    <summary><h2>更新日志</h2></summary>
    <h3>
        0.3.2
    </h3>
    <ul>
        <li>修复图片缓存清除bug</li>
        <li>升级上游依赖版本</li>
    </ul>
    <h3>
        0.3.1
    </h3>
    <ul>
        <li>修复部分日志bug</li>
        <li>增加图片解密及输出</li>
        <li>增加部分配置，设置缓存文件删除时间</li>
    </ul>
    <h3>
        0.3.0
    </h3>
    <ul>
        <li>重构整个框架，使用uvicorn管理主线程</li>
        <li>增加http api</li>
        <li>增加http post上报</li>
        <li>ws改为异步websockets管理</li>
        <li>定时器改为异步调度</li>
    </ul>
	<h3>
        0.2.0
    </h3>
    <ul>
        <li>增加二维码扫描</li>
        <li>增加日志保存</li>
        <li>增加文件缓存模块，拓展ntchat自身api中的file支持类型（支持filepath,url,base64）</li>
        <li>增加定时模块用于处理文件缓存</li>
        <li>api调用file及file_path字段需要修改，目前支持：</li>
        <ul>
            <li>绝对路径，采用file_uri：file:///path</li>
            <li>网络路径，支持http和https，格式：http://或https://</li>
            <li>base64，格式为：base64://values</li>
        </ul>
    </ul>
</details>


## Http api

在连接到wechat后，会自动开启http api，访问http api需要注意：

- 当前api只支持post方法，get无法访问
- post访问请将参数放入body，编码规则使用JSON， Content-Type设置为application/json

### 响应数据模型

| 字段 |        类型         |        说明         |
| :--: | :-----------------: | :-----------------: |
| code |         int         | 响应code，200为成功 |
| msg  |         str         | 失败时返回错误内容  |
| data | dict \| list \| str |    响应数据内容     |

下面是api列表：

### 获取登录信息

api地址：/get_login_info

参数： 无

响应数据类型：dict

### 获取自己个人信息

api地址：/get_self_info

参数：无

响应数据类型：dict

### 获取联系人列表

api地址：/get_contacts

参数：无

响应数据类型：list[dict]

### 获取关注公众号列表

api地址：/get_publics

参数：无

响应数据类型：list[dict]

### 获取联系人详细信息

api地址：/get_contact_detail

参数：

| 字段名 | 数据类型 | 可选 | 默认值 |        说明        |
| :----: | :------: | :--: | :----: | :----------------: |
| *wxid* |   str    | 必填 |  None  | 要获取联系人的wxid |

响应数据类型：dict

### 根据wxid、微信号、昵称和备注模糊搜索联系人

api地址：/search_contacts

参数：

|     字段名     | 数据类型 | 可选 | 默认值 |     说明     |
| :------------: | :------: | :--: | :----: | :----------: |
|     *wxid*     |   str    | 可选 |  None  |    微信id    |
|   *account*    |   str    | 可选 |  None  |    微信号    |
|   *nickname*   |   str    | 可选 |  None  |   微信昵称   |
|    *remark*    |   str    | 可选 |  None  |     备注     |
| *fuzzy_search* |   bool   | 可选 |  True  | 是否模糊搜索 |

响应数据类型：list

### 获取群列表

api地址：/get_rooms

参数：无

响应数据类型：list[dict]

### 获取指定群详细信息

api地址：/get_room_detail

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |   说明   |
| :---------: | :------: | :--: | :----: | :------: |
| *room_wxid* |   str    | 必填 |  None  | 群房间id |

响应数据类型：dict

### 获取群名

api地址：/get_room_name

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |  说明  |
| :---------: | :------: | :--: | :----: | :----: |
| *room_wxid* |   str    | 必填 |  None  | 房间号 |

响应数据类型：str

### 获取群成员列表

api地址：/get_room_members

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |   说明   |
| :---------: | :------: | :--: | :----: | :------: |
| *room_wxid* |   str    | 必填 |  None  | 群房间id |

响应数据类型：list[dict]

### 发送文本消息

api地址：/send_text

参数：

|  字段名   | 数据类型 | 可选 | 默认值 |                   说明                   |
| :-------: | :------: | :--: | :----: | :--------------------------------------: |
| *to_wxid* |   str    | 必填 |  None  | 接收人id，可以是个人id，也可以是群房间号 |
| *content* |   str    | 必填 |  None  |               发送文本内容               |

响应数据类型：None

### 发送群@消息

api地址：/send_room_at_msg

参数：

|  字段名   | 数据类型  | 可选 | 默认值 |               说明               |
| :-------: | :-------: | :--: | :----: | :------------------------------: |
| *to_wxid* |    str    | 必填 |  None  |     发送人id，也可以是房间号     |
| *content* |    str    | 必填 |  None  | 发送文本内容，需填写占位符：{$@} |
| *at_list* | list[str] | 必填 |  None  | at列表，个数需要与占位符数量一致 |

响应数据类型：None

**注意**：

- 假如文本为："test,你好{$@},你好{$@}.早上好"
- 文本消息的content的内容中设置占位字符串 {$@},这些字符的位置就是最终的@符号所在的位置
- 假设这两个被@的微信号的群昵称分别为aa,bb
- 则实际发送的内容为 "test,你好@ aa,你好@ bb.早上好"(占位符被替换了)
- 占位字符串的数量必须和at_list中的微信数量相等.

### 发送名片

api地址：/send_card

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |   说明   |
| :---------: | :------: | :--: | :----: | :------: |
|  *to_wxid*  |   str    | 必填 |  None  | 接收人id |
| *card_wxid* |   str    | 必填 |  None  | 卡片人id |

响应数据类型：None

### 发送链接卡片

api地址：/send_link_card

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |             说明             |
| :---------: | :------: | :--: | :----: | :--------------------------: |
|  *to_wxid*  |   str    | 必填 |  None  | 接收人id，支持个人id和房间id |
|   *title*   |   str    | 必填 |  None  |           卡片标题           |
|   *desc*    |   str    | 必填 |  None  |         卡片说明文字         |
|    *url*    |   str    | 必填 |  None  |           链接地址           |
| *image_url* |   str    | 必填 |  None  |        卡片图片的url         |

响应数据类型：None

### 发送图片

api地址：/send_image

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |             说明             |
| :---------: | :------: | :--: | :----: | :--------------------------: |
|  *to_wxid*  |   str    | 必填 |  None  | 接收人id，支持个人id和房间id |
| *file_path* |   str    | 必填 |  None  |           图片地址           |

响应数据类型：None

**注意**：

图片地址目前支持：

- 绝对路径，采用file_uri，格式为file:///path
- 网络路径，支持http和https，格式：http://或https://
- base64，格式为：base64://values

### 发送文件

api地址：/send_file

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |             说明             |
| :---------: | :------: | :--: | :----: | :--------------------------: |
|  *to_wxid*  |   str    | 必填 |  None  | 接收人id，支持个人id和房间id |
| *file_path* |   str    | 必填 |  None  |           文件地址           |

响应数据类型：None

**注意**：

文件地址目前支持：

- 绝对路径，采用file_uri，格式为file:///path
- 网络路径，支持http和https，格式：http://或https://
- base64，格式为：base64://values

### 发送视频

api地址：/send_video

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |             说明             |
| :---------: | :------: | :--: | :----: | :--------------------------: |
|  *to_wxid*  |   str    | 必填 |  None  | 接收人id，支持个人id和房间id |
| *file_path* |   str    | 必填 |  None  |           视频地址           |

响应数据类型：None

**注意**：

视频地址目前支持：

- 绝对路径，采用file_uri，格式为file:///path
- 网络路径，支持http和https，格式：http://或https://
- base64，格式为：base64://values

### 发送gif

api地址：/send_gif

参数：

|  字段名   | 数据类型 | 可选 | 默认值 |             说明             |
| :-------: | :------: | :--: | :----: | :--------------------------: |
| *to_wxid* |   str    | 必填 |  None  | 接收人id，支持个人id和房间id |
|  *file*   |   str    | 必填 |  None  |           gif地址            |

响应数据类型：None

**注意**：

gif地址目前支持：

- 绝对路径，采用file_uri，格式为file:///path
- 网络路径，支持http和https，格式：http://或https://
- base64，格式为：base64://values

### 发送xml消息

api地址：/send_xml

参数：

|   字段名   | 数据类型 | 可选 | 默认值 |             说明             |
| :--------: | :------: | :--: | :----: | :--------------------------: |
| *to_wxid*  |   str    | 必填 |  None  | 接收人id，支持个人id和房间id |
|   *xml*    |   str    | 必填 |  None  |           xml内容            |
| *app_type* |   int    | 选填 |   5    |        小程序分类type        |

响应数据类型：None

### 发送拍一拍

api地址：/send_pat

参数：

|    字段名     | 数据类型 | 可选 | 默认值 |     说明     |
| :-----------: | :------: | :--: | :----: | :----------: |
|  *room_wxid*  |   str    | 必填 |  None  |    房间号    |
| *patted_wxid* |   str    | 必填 |  None  | 拍一拍对象id |

响应数据类型：None

### 同意加好友请求

api地址：/accept_friend_request

参数：

|      字段名       | 数据类型 | 可选 | 默认值 |    说明    |
| :---------------: | :------: | :--: | :----: | :--------: |
| *encryptusername* |   str    | 必填 |  None  | 好友用户名 |
|     *ticket*      |   str    | 必填 |  None  | 事件ticket |
|      *scene*      |   int    | 必填 |  None  |  好友权限  |

响应数据类型：None

### 创建群

api地址：/create_room

参数：

|    字段名     | 数据类型  | 可选 | 默认值 |       说明       |
| :-----------: | :-------: | :--: | :----: | :--------------: |
| *member_list* | list[str] | 必填 |  None  | 初始成员wxid列表 |

响应数据类型：None

### 邀请好友入群

api地址：/invite_room_member

参数：

|    字段名     | 数据类型  | 可选 | 默认值 |       说明       |
| :-----------: | :-------: | :--: | :----: | :--------------: |
|  *room_wxid*  |    str    | 必填 |  None  |      房间号      |
| *member_list* | list[str] | 必填 |  None  | 邀请好友wxid列表 |

响应数据类型：None

### 删除群成员

api地址：/del_room_member

参数：

|    字段名     | 数据类型  | 可选 | 默认值 |       说明       |
| :-----------: | :-------: | :--: | :----: | :--------------: |
|  *room_wxid*  |    str    | 必填 |  None  |      房间号      |
| *member_list* | list[str] | 必填 |  None  | 删除成员wxid列表 |

响应数据类型：None

**注意**：需要有相应权限

### 修改群名

api地址：/modify_room_name

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |   说明   |
| :---------: | :------: | :--: | :----: | :------: |
| *room_wxid* |   str    | 必填 |  None  |  房间号  |
|   *name*    |   str    | 必填 |  None  | 房间名称 |

响应数据类型：None

**注意**：需要有相应权限

### 修改群公告

api地址：/modify_room_notice

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |   说明   |
| :---------: | :------: | :--: | :----: | :------: |
| *room_wxid* |   str    | 必填 |  None  |  房间号  |
|  *notice*   |   str    | 必填 |  None  | 公告内容 |

响应数据类型：None

**注意**：需要有相应权限

### 添加群成员为好友

api地址：/add_room_friend

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |     说明     |
| :---------: | :------: | :--: | :----: | :----------: |
| *room_wxid* |   str    | 必填 |  None  |    房间号    |
|   *wxid*    |   str    | 必填 |  None  | 请求对方wxid |
|  *verify*   |   str    | 选填 |  None  |     备注     |

响应数据类型：None

### 退出群

api地址：/quit_room

参数：

|   字段名    | 数据类型 | 可选 | 默认值 |  说明  |
| :---------: | :------: | :--: | :----: | :----: |
| *room_wxid* |   str    | 必填 |  None  | 房间号 |

响应数据类型：None

### 修改好友备注

api地址：/modify_friend_remark

参数：

|  字段名  | 数据类型 | 可选 | 默认值 |   说明   |
| :------: | :------: | :--: | :----: | :------: |
|  *wxid*  |   str    | 必填 |  None  | 好友wxid |
| *remark* |   str    | 必填 |  None  |   备注   |

响应数据类型：None

### 获取群名

api地址：/get_room_name

参数:

|   字段名    | 数据类型 | 可选 | 默认值 |  说明  |
| :---------: | :------: | :--: | :----: | :----: |
| *room_wxid* |   str    | 必填 |  None  | 房间号 |

响应数据类型：str
