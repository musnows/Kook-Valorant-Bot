23-01-12更新：目前采用 `start.py` 来同时启动Api和Bot。若想单独启动Api或Bot，需取消 `api.py/main.py` 的底部注释

# 如何开始？

建议根据[khl.py](https://github.com/TWT233/khl.py)的`example`教程，学习KOOK机器人的基本搭建（很简单的，相信我）

如果你已经学习完了所有example，那么本仓库的内容对于你来说就是不难的！

我会添加一些只有本仓库中包含的内容的代码解释，方便你来搭建你自己的kook机器人！有任何问题，都可以加入我的[kook频道](https://kook.top/gpbTwZ)交流！

### 1.克隆本仓库

准备好Linux下的git，克隆本仓库

~~~
git clone https://github.com/musnows/Valorant-kaiheila-bot.git
~~~

如果想使用最新的commit和新功能，请切换到develop分支。

保证你的Windows/Linux中`Python`版本高于`3.8`，执行下面的安装库命令

~~~
pip3 install -r requirements.txt
~~~


更新Python的方法可以参考本wiki的 [01-How_to_update_Python](https://github.com/Aewait/Valorant-Kook-Bot/wiki/01-How_to_update_Python)

> Q：为何`khl.py`只需要3.6.8以上版本，而本仓库需要3.8+？
>
> A：因为valorant的第三方`Python Api`需要3.8+版本

如果安装及其缓慢，则可以使用清华镜像源

```
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

若无法安装 riot-auth，请前往 [floxay/python-riot-auth](https://github.com/floxay/python-riot-auth) 下载仓库zip，解压后，cd进入目录，执行如下命令

```
pip3 install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

![install-riot-auth](https://img.kookapp.cn/assets/2023-02/NSEuH87KrO1y90y8.png)


### 2.配置config文件

在`code`路径下创建`config`文件夹，并在其中创建`config.json`，将你的`token`写入其中

>示例文件参考 [config.exp.json](../code/config/config.exp.json)

总结一下，本仓库需要手动配置的文件有下面两个，其中`color_emoji.json`在仓库中有示例文件

| 文件路径                    | 功能                                                         |
| --------------------------- | ------------------------------------------------------------ |
| code/config/config.json     | 存放本机器人的基本配置：[KOOK开发者页面](https://developer.kaiheila.cn/doc/intro) |
| [code/config/color_emoji.json](https://github.com/Valorant-Shop-CN/Kook-Valorant-Bot/blob/develop/code/config/color_emoji.json) | 存放`code/main.py`中自动给用户上角色功能相关的emoji以及`msg_id/guild_id`       |
| ~code/config/valorant.json~ | ~存放拳头开发者api-key：[Roit Develop](https://developer.riotgames.com/)~ 目前需要使用该api的代码都已被删除 |
| ~code/config/caiyun.json~     | ~存放彩云小译的api-key：[彩云](https://docs.caiyunapp.com/blog/2018/09/03/lingocloud-api/#python-%E8%B0%83%E7%94%A8)~ 已使用`config.json`代替 |

这些config文件已经被我写入了`.gitignore`，所以在本仓库中你是看不到该文件夹的。这也保证当我们把代码托管到 `gitee/github/gitlab` 等平台上时，自己的`token`不会泄漏。

在 `code/log` 路径下还有各种记录文件，你可以在 [docs/log.example](./log.example) 里面找到示例文件。其中调用 `valorant api` 获取到的本地文件，以及`valorant`常见错误码的解决方案直接给出。

这些不同log文件存放内容参考 [code/endpoints/FileManage.py](../code/endpoints/FileManage.py) 中的注释


### 3.让机器人跑起来！


当你完成上面两步后，即可`cd`进入`code`目录，执行运行命令;

~~~bash
python3 start.py #同时运行api和机器人
python3 main.py  #只运行机器人
~~~

但是这样，你会发现程序在shell中挂起，且关闭终端后机器人会停止运行

* 让机器人后台运行(Linux)

下面这个代码的功能是让机器人在Linux后台运行，并将输出内容写入`code/log`路径下的`bot.log`文件。为了不让机器人的log也被他人看到，我也将log类型文件写入了`.gitignore`
```
nohup python3 -u start.py >> ./log/bot.log 2>&1&
```
执行后，Linux会给你返回一个进程编号（建议先用`python3 start.py`直接运行，确认无bug后再执行上面的命令）

* 找到后台运行的机器人并让其下岗(Linux)

我们可以通过`ps -e`查看当前正在运行的进程，但这样的缺点是，当你关闭shell后，下一次再打开，就会发现之前的进程貌似不见了。

这时候就可以用下面这个语句来**具体定位**之前已经在运行的后台程序

~~~
ps -aux | grep start.py | grep -v grep 
~~~

当你想让机器人下岗的时候，可以使用下面这个指令

```
kill -9 进程号
```

注意：如果你需要修改代码并测试新功能，请一定要先**终止先前在后台运行的程序**。否则你修改后的代码，即使用 `python3 main.py` 运行，其新功能也是无法生效的！

本仓库code路径下有`makefile`文件，你可以使用`make`快速运行bot，`make ps`快速查找后台运行的程序。使用之前，你需要将make中的py3修改为你本地的python命令。

# 起飞！

好了！配置完本页面的内容，想必你的bot已经可以**正常起步**了！

在频道里面输入 `/ahri`，让我们来看看本仓库里面一些函数的对应功能吧！

## 常见错误参考

bot运行的时候经常会碰到一些常见的错误，在这里做出记录。

### 1.jsonDecode err

如果你学习过网络协议，序列化和反序列化相关知识，应该就会知道这个报错是什么原因。

简单说明就是，json是一个序列化方式，其正在对api的返回值进行`decode`反序列化，这个报错的意思就是反序列化失败了，可以理解为api调用失败！

一般出现这个问题的原因是**短暂连不上riot的服务器**，属于正常情况；如果此报错出现较久且无法去除，请先确认是否是无法链接上riot的api服务器。

```
Exception in thread Thread-85 (auth2fa):
Traceback (most recent call last):
  File "/home/muxue/.local/lib/python3.10/site-packages/requests/models.py", line 971, in json
    return complexjson.loads(self.text, **kwargs)
  File "/usr/local/lib/python3.10/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
  File "/usr/local/lib/python3.10/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/usr/local/lib/python3.10/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.10/threading.py", line 1016, in _bootstrap_inner
    self.run()
  File "/usr/local/lib/python3.10/threading.py", line 953, in run
    self._target(*self._args, **self._kwargs)
  File "/home/muxue/kook/val-bot/code/utils/valorant/EzAuth.py", line 277, in auth2fa
    auth.authorize(user, passwd, key=key)
  File "/home/muxue/kook/val-bot/code/utils/valorant/EzAuth.py", line 156, in authorize
    self.Region = self.get_Region()
  File "/home/muxue/kook/val-bot/code/utils/valorant/EzAuth.py", line 213, in get_Region
    data = r.json()
  File "/home/muxue/.local/lib/python3.10/site-packages/requests/models.py", line 975, in json
    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
```

### 2.channel_name

khl.py的常驻报错，不影响bot运行，忽略即可

```
Traceback (most recent call last):
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/client.py", line 63, in handle_pkg
    await self._consume_pkg(pkg)
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/client.py", line 75, in _consume_pkg
    msg = self._make_msg(pkg)
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/client.py", line 85, in _make_msg
    msg = self._make_channel_msg(pkg)
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/client.py", line 92, in _make_channel_msg
    msg = PublicMessage(**pkg, _gate_=self.gate)
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/message.py", line 135, in __init__
    channel = PublicTextChannel(id=self.target_id, name=self.extra['channel_name'], _gate_=self.gate)
KeyError: 'channel_name'
'channel_name'
```

### 3.asyncio

有两个任务被撞到了同一个时间，导致任务被miss临时取消；这也是个正常情况。因为bot里面有不少的定时任务，总有些`@bot.task.add_interval()`运行道一定时间后，时间重合导致撞车

```
Run time of job "vip_roll_task (trigger: interval[0:01:20], next run at: 2023-02-09 16:54:05 CST)" was missed by 0:00:23.478322
Run time of job "Save_File_Task (trigger: interval[0:05:00], next run at: 2023-02-09 16:55:45 CST)" was missed by 0:02:24.723250
error raised during message handling
Traceback (most recent call last):
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/client.py", line 111, in safe_handler
    await handler(msg)
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/bot/bot.py", line 142, in handler
    await event_handler(self, event)
  File "/home/muxue/kook/val-bot/code/main.py", line 230, in Grant_Roles
    await Color_GrantRole(b, event)
  File "/home/muxue/kook/val-bot/code/utils/GrantRoles.py", line 36, in Color_GrantRole
    g = await bot.client.fetch_guild(EmojiDict['guild_id'])  # 填入服务器id
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/client.py", line 163, in fetch_guild
    await guild.load()
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/guild.py", line 152, in load
    self._update_fields(**(await self.gate.exec_req(api.Guild.view(self.id))))
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/gateway.py", line 30, in exec_req
    return await self.requester.exec_req(r)
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/requester.py", line 45, in exec_req
    return await self.request(r.method, r.route, **r.params)
  File "/home/muxue/.local/lib/python3.10/site-packages/khl/requester.py", line 32, in request
    async with self._cs.request(method, f'{API}/{route}', **params) as res:
  File "/home/muxue/.local/lib/python3.10/site-packages/aiohttp/client.py", line 1138, in __aenter__
    self._resp = await self._coro
  File "/home/muxue/.local/lib/python3.10/site-packages/aiohttp/client.py", line 466, in _request
    with timer:
  File "/home/muxue/.local/lib/python3.10/site-packages/aiohttp/helpers.py", line 721, in __exit__
    raise asyncio.TimeoutError from None
asyncio.exceptions.TimeoutError
```