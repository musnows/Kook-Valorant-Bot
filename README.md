


<h1 align="center">Kook-Valorant--bot</h1>


<h4 align="center">这是一个KOOK的「Valorant」小机器人</h4>



<div align="center">

[English](./README_EN.md) | 简体中文


![python](https://img.shields.io/badge/Python-3.8%2B-green) ![commit](https://img.shields.io/github/last-commit/Aewait/Valorant-kaiheila-bot) ![release](https://img.shields.io/github/v/release/Aewait/Valorant-kaiheila-bot)
[![khl server](https://www.kaiheila.cn/api/v3/badge/guild?guild_id=3566823018281801&style=3)](https://kaihei.co/oqz7Xg) ![githubstars](https://img.shields.io/github/stars/Aewait/Valorant-kaiheila-bot?style=social)

<img src="./screenshot/log.png" height="55px" alt="Bot Log Image">
</div>

## 功能
当前机器人基本完善，目前支持回复Valorant游戏错误码、查询Valorant每日商店/夜市/vp/r点，和一些简单功能。

下面是目前支持的功能列表：

| 帮助命令      | 功能                                       |
| ------------- | ------------------------------------------ |
| `/Ahri`           | 回复使用帮助（因`/help`和其他机器人冲突，故用阿狸的英文名`Ahri`替代） |
| `/vhelp` | Valorant相关查询功能的帮助命令                     |

关于商店查询的**初步功能**已经添加，但是其`稳定性/是否封号`未知，建议**谨慎**使用！


| 游戏相关      | 功能                                       |
| ------------- | ------------------------------------------ |
| `/val 错误码` | 回复游戏错误码解决方法                     |
| `/saveid`     | 保存（修改）用户的游戏id                   |
| `/myid`       | 显示用户的游戏id                           |
| `/bundle 皮肤名`  | 搜索已有皮肤系列包含什么枪械               |
| `/login 账户 密码` | 私聊bot进行登录riot账户的操作(获取token) |
| `/logout` | 退出riot账户登录 |
| `/shop` | 获取每日商店的4个皮肤 |
| `/night` | 获取夜市的6个皮肤 |
| `/uinfo`或`/point` | 获取玩家卡面和称号，剩余vp和r点 |
| `/notify-a 皮肤名` | 搜索皮肤名，并提供选项将指定皮肤加入商店提醒 |
| `/notify-l` | 查看当前已经设置了提醒的皮肤 |
| `/notify-d 皮肤uuid` | 使用uuid删除不需要提醒的皮肤 |
| `/vip-u 激活码` |兑换阿狸的vip |
| `/vip-c` | 查看vip的剩余时间 |
| `/vip-shop` | 查看已保存的商店查询diy背景图 |
| `/vip-shop 图片url` | 添加商店查询diy背景图  |
| `/vip-shop-s 图片编号` | 切换商店查询的背景图 |
| `/vip-shop-d 图片编号` | 删除商店查询的背景图 |
|`/rate 皮肤名`|查找皮肤，选择指定皮肤进行打分|
|`/rts 序号 打分 吐槽`|选中皮肤序号，给该皮肤打个分(0~100) 再吐槽一下!|
|`/kkn`|查看昨日评分最高/最低的用户|

更多vip用户的特殊功能

>* 「全新商店返回值」vip用户将获取到16-9的超帅商店返回值
>* 「保存登录信息」vip用户登陆后，阿狸会自动保存您的cookie。在阿狸维护重启的时候，您的登录信息不会丢失
>* 「早八商店提醒」阿狸将在早8点获取vip用户的每日商店并私聊发图给用户，同时会对这张图片进行缓存，当天使用/shop命令的时候，只需2s获取结果，三倍于普通用户的响应速度！
>
>目前商店查询背景图diy支持16-9(横屏)的图片，图片url获取：`PC端将图片上传到kook→点击图片→底部...处复制图片链接→使用/vip-shop命令设置背景` [教程图](https://img.kookapp.cn/assets/2022-12/nICYcewY8a0u00yt.png) 
>
>请不要设置违规图片(擦边也不行)！若因为您上传违禁图片后导致阿狸被封，您将被剥夺vip并永久禁止兑换vip

每日商店刷枪提醒功能需要用户**保持登录状态**，bot会在每天的`08:01`遍历列表，查看您的商店是否刷出了您想要的皮肤

| 其他命令    | 功能                                                         |
| ----------------- | ------------------------------------------------------------ |
| `/hello`          | 打个招呼 (一般用来测试bot在不在线)                                                 |
| `/roll 1 100`     | 掷色子1-100，范围可自行调节                                  |
| `/countdown 秒数` | 倒计时，默认60秒                                             |
| `/TL 内容` | 翻译内容。其他语言翻译为中文，中文默认翻译成en |
| `/TLON` | 在本文字频道`打开`实时翻译功能 |
| `/TLOFF` | 在本文字频道`关闭`实时翻译功能 |
| `/we 城市` | 查询`城市`未来3天的天气情况 |
| `/hs` | 历史上的今天（因为kook审核原因被删除） |
|         `无`         | 自动给新用户上对应角色（可自主修改）                           |
| `无` | 当有人助力服务器的时候，在通知频道发送感谢信息 |

你可以在[screenshot](./screenshot)文件夹中找到对应的截图示例

<img src="./screenshot/daily_shop.png" height="400px" alt="shop_img"> <img src="./screenshot/uinfo.png" weight="300px" height="200px" alt="vp_rp">

<details>
<summary>更多截图</summary>

<img src="./screenshot/bundle.png" alt="bundle">

<img src="./screenshot/weather.png" alt="we">

<img src="./screenshot/lead.png" alt="leaderborad">

<img src="./screenshot/night.png" height="300px" alt="night">

<img src="./screenshot/vip_daily_shop.png" height="300px" alt="vip_shop">
</details>

### valorant-shop-img-api

> api源码见 [code_api](./code_api/)

这个api是利用python写的小代码，主要还是复用了阿狸主代码中给商店画图的部分，支持自定义背景图

```
https://val.outpost54.top/shop-img?token=密钥&account=账户&passwd=密码&img_src=自定义背景图的url

提供一个测试密钥
da4ec652-4a25-11ed-bff2-525400c9274f
```
api后台不会记录您的账户信息，如果请求`/shop-img`接口，图片将直接跳转到kook的图床；如果请求`/shop-url`接口，图片将以json（内含url）的方式返回

> 咳咳，白嫖了kook的图床

以下为请求 `/shop-url` 接口的返回格式示例，只有返回code为0才为正确返回；由于该接口的特殊性，暂不支持2fa用户

```json
{
    "code": 0, 
    "message": "https://img.kookapp.cn/attachments/2022-12/16/gsvlSyfweq0zk0k0.png", 
    "info": "商店图片获取成功"
}
```

<img src="./screenshot/val_api_img.png" height="300px" alt="api_shop_img">

----

## 如何使用？

保证你的Windows/Linux中`Python`版本高于`3.8`，执行下面的安装库命令

~~~
pip install -r requirements.txt
~~~

> Q：为何`khl.py`只需要3.6.8以上版本，而本仓库需要3.8+？
>
> A：因为Valorant的第三方`Python Api`需要3.8+版本

建议根据[khl.py](https://github.com/TWT233/khl.py)的`example`教程，学习KOOK机器人的基本搭建（很简单的，相信我）

如果你想直接使用本机器人，可以转到本仓库[WIKI](https://github.com/Aewait/Valorant-kaiheila-bot/wiki)查看更多引导内容

----

## To Do

下面是一些未来的计划

- [x] 增加保存用户游戏id的功能
- [x] 添加自动给新用户上色功能（目前只有kook的valorant服务器能用）
- [ ] 实现查询游戏战绩（需要roit授权）
- [x] 实现玩家商店刷枪的查询
- [x] 实现当商店刷新某一把枪的时候提醒玩家
- [x] 查看玩家的夜市
- [x] 邮箱验证2fa登录
- [ ] 通行证、每日任务的查询
- [ ] 以类似抽卡的方式，用按钮、图片等等方式显示用户的夜市

~~由于很多人在使用类似商店查询软件后被ban，我决定正式停止相关功能的开发~~

咳咳，虽然初步的商店查询功能已经上线，但是其是否`封号`依旧有争论！目前功能已经上线一个月有余，且询问过外网开发者，其表示没有听说过有人因为使用api被封号。

**如果您担心风险，请不要使用相关功能**！bot的`/vhelp`命令`/login`命令中有相关警告提示，使用即代表您同意了承担风险！

<img src="./screenshot/issue_banned.png" height="250px" alt="issue screenshots">

----

## 依赖

由于本人压根没有系统的学过Python，所以本仓库的很多代码都是根据他人教程修改后使用的
* 基本框架参考[khl.py](https://github.com/TWT233/khl.py)提供的`kook sdk`以及使用教程
* Valorant游戏`leaderboard`排行榜获取基于 [frissyn/valorant.py](https://github.com/frissyn/valorant.py/) 提供的`sdk`
* Valorant游戏主要查询代码基于 [ValorantClientAPI](https://github.com/HeyM1ke/ValorantClientAPI) 项目提供的`api文档`
* 通过账户密码获取 `riot_auth_token` 基于 [floxay/python-riot-auth](https://github.com/floxay/python-riot-auth) 项目


### 特别鸣谢🎁
* [@DeeChael](https://github.com/DeeChael) for helping me debug
* [@Edint386](https://github.com/Edint386) for adding `PIL_code` for `/shop` 
* [@staciax](https://github.com/staciax) for [Valorant-DiscordBot/issues/74](https://github.com/staciax/Valorant-DiscordBot/issues/74)


### 支持本项目😘

阿狸的支出主要为云服务器的费用，您的支持是对作者的最大鼓励！

<a href="https://afdian.net/a/128ahri">
    <img src="https://pic1.afdiancdn.com/static/img/welcome/button-sponsorme.jpg" alt="aifadian">
</a >