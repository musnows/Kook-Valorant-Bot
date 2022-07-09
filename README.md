


<h1 align="center">Valorant-kaiheila-bot</h1>


<h4 align="center">这是一个KOOK的「Valorant」小机器人</h4>



<div align="center">

[English](./README_EN.md) | 简体中文


![python](https://img.shields.io/badge/Python-3.8%2B-green) ![commit](https://img.shields.io/github/last-commit/Aewait/Valorant-kaiheila-bot) ![release](https://img.shields.io/github/v/release/Aewait/Valorant-kaiheila-bot)
[![khl server](https://www.kaiheila.cn/api/v3/badge/guild?guild_id=3566823018281801&style=3)](https://kaihei.co/oqz7Xg) ![githubstars](https://img.shields.io/github/stars/Aewait/Valorant-kaiheila-bot?style=social)
</div>

## 功能
当前机器人处于极极极其早期版本，目前只支持回复valorant游戏错误码，和一些简单功能

下面是目前支持的功能列表：

| 命令              | 功能                                                         |
| ----------------- | ------------------------------------------------------------ |
| `/hello`          | 回复 world！                                                 |
| `/Ahri`           | 回复使用帮助（因`/help`和其他机器人冲突，故用阿狸的英文名`Ahri`替代） |
| `/val 错误码`     | 回复游戏错误码解决方法                                       |
| `/saveid`         | 保存（修改）用户的游戏id                                     |
| `/myid`           | 显示用户的游戏id                                             |
| `/skin name`      | 搜索已有皮肤系列包含什么枪械                                 |
| `/lead 30 20`     | 显示出亚服(ap)排行榜前30名胜场超过20的玩家                   |
| `/roll 1 100`     | 掷色子1-100，范围可自行调节                                  |
| `/countdown 秒数` | 倒计时，默认60秒                                             |
|         `无`         | 自动给新用户上对应角色（可自主修改）                           |
| `无` | 当有人助力服务器的时候，在通知频道发送感谢信息 |

你可以在[screenshot](./screenshot)文件夹中找到对应的截图示例

----

## 如何使用？

保证你的Linux中`Python`版本高于`3.8`，执行下面的安装库命令

~~~
pip install khl.py
pip install valorant
pip install requests
~~~

> Q：为何`khl.py`只需要3.6.8以上版本，而本仓库需要3.8+？
>
> A：因为valorant的第三方`Python Api`需要3.8+版本

建议根据[khl.py](https://github.com/TWT233/khl.py)的`example`教程，学习KOOK机器人的基本搭建（很简单的，相信我）

如果你想直接使用本机器人，则继续往下看👇

### 1.克隆本仓库

准备好Linux下的git，克隆本仓库

~~~
git clone https://github.com/Aewait/Valorant-kaiheila-bot.git
~~~

### 2.配置config文件

光光克隆还不够，你需要在[KOOK开发者页面](https://developer.kaiheila.cn/doc/intro)申请一个机器人内测资格，并获得你的`token`

在`code`路径下创建`config`文件夹，并在其中创建`config.json`，将你的`token`写入其中

~~~
{
  "token": "你的token",
  "verify_token": "",
  "encrypt_key": ""
}
~~~

* 如果你想使用`Valorant`游戏相关的接口，则还需要去往[Roit Develop](https://developer.riotgames.com/)申请拳头游戏的`api_key`。并将获得的key写入`code/config`路径下的`valorant.json`文件（格式同上）

因为这两个文件已经被我写入了`.gitignore`，所以在本仓库中你是看不到该文件夹的。这也保证当我们把代码托管到gitee/github/gitlab等平台上时，自己的`token`不会泄漏

除此之外，`v0.0.7`新增的`自动给用户上角色`功能需要手动设置服务器id、消息id和emoji列表内容，具体示例请看[code/log](./code/log)文件夹中的内容

### 3.让机器人跑起来！


* 直接运行机器人

当你完成上面两步后，即可`cd`进入`code`目录，执行运行命令

~~~
python main.py
~~~

但是这样，你会发现程序在shell中挂起，且关闭终端后机器人会停止运行

* 让机器人后台运行

下面这个代码的功能是让机器人在Linux后台运行，并将输出内容写入`code/log`路径下的`bot.log`文件。为了不让机器人的log也被他人看到，我也将log类型文件写入了`.gitignore`
```
nohup python -u main.py>./log/bot.log 2>&1&
```
执行后，Linux会给你返回一个进程编号（建议先用`python main.py`直接运行，确认无bug后再执行上面的命令）

* 找到后台运行的机器人并让其下岗

我们可以通过`ps -e`查看当前正在运行的进程，但这样的缺点是，当你关闭shell后，下一次再打开，就会发现之前的进程貌似不见了。

这时候就可以用下面这个语句来**具体定位**之前已经在运行的后台程序

~~~
ps -aux|grep main.py|grep -v grep 
~~~

当你想让机器人下岗的时候，可以使用下面这个指令

```
kill -9 进程号
```

注意：如果你需要修改代码并测试新功能，请一定要先终止先前在后台运行的程序。否则你修改后的代码，即使使用`python main.py`运行，其功能也是无法生效的

### 4.等待补充……

----

## TODO

下面是一些未来的计划

- [x] 增加保存用户游戏id的功能
- [x] 添加自动给新用户上色功能
- [ ] 学习python
- [x] 学习接入官方的`valorant api`库
- [ ] 实现查询游戏战绩（需要roit授权）
- [ ] ~~实现玩家商店刷枪的查询~~
- [ ] ~~实现当商店刷新某一把枪的时候提醒玩家~~
- [ ] ~~查看玩家的夜市~~

由于很多人在使用类似商店查询软件后被ban，我决定正式停止相关功能的开发
![ban](https://s1.ax1x.com/2022/07/07/jwNGMF.png)

---

## 依赖

由于本人压根没有学过python，所以本仓库的很多代码都是根据他人教程修改后使用的
* 基本代码参考[khl.py](https://github.com/TWT233/khl.py)提供的api库以及使用教程
* Valorant游戏部分代码基于@frissyn大佬提供的[valorant.py](https://github.com/frissyn/valorant.py/)
* 早期使用了`https://replit.com/`和`https://uptimerobot.com/`提供的服务，无需使用**云服务器**也可部署机器人。
这两个网站的使用教程见[B站视频](https://www.bilibili.com/video/BV12U4y1g7JY?spm_id_from=333.1007.top_right_bar_window_history.content.click)，代码可以查看`code/EarlyTest`里面的内容（注意，部署到云服务器的方式和这两个网站是不一样的）


