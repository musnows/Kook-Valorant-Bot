# encoding: utf-8:

import json
import random

from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct

# 新建机器人，token 就是机器人的身份凭证
# 用 json 读取 config.json，装载到 config 里
# 注意文件路径，要是提示找不到文件的话，就 cd 一下工作目录/改一下这里
with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])


# 注册指令
# @ 是「装饰器」语法，大家可以网上搜搜教程，我们这里直接用就行
# bot 是我们刚刚新建的机器人，声明这个指令是要注册到 bot 中的
# name 标示了指令的名字，名字也被用于触发指令，所以我们 /hello 才会让机器人有反应
# async def 说明这是一个异步函数，khl.py 是异步框架，所以指令也需要是异步的
# world 是函数名，可以自选；函数第一个参数的类型固定为 Message
@bot.command(name='hello')
async def world(msg: Message):
    # msg 指的是我们所发送的那句 `/hello`
    # 所以 msg.reply() 就是回复我们那句话，回复的内容是 `world!`
    await msg.reply('world!')

# 倒计时函数，单位为秒，默认60秒
@bot.command()
async def countdown(msg: Message,time: int = 60):
    cm = CardMessage()

    c1 = Card(Module.Header('本狸帮你按下秒表喽~'), color=(198, 65, 55)) # color=(90,59,215) is another available form
    c1.append(Module.Divider())
    c1.append(Module.Countdown(datetime.now() + timedelta( seconds=time), mode=Types.CountdownMode.SECOND))
    cm.append(c1)

    # c2 = Card(theme=Types.Theme.DANGER)  # priority: color > theme, default: Type.Theme.PRIMARY
    # c2.append(Module.Section('the DAY style countdown'))
    # c2.append(Module.Countdown(datetime.now() + timedelta(seconds=time), mode=Types.CountdownMode.DAY))
    # cm.append(c2)  # A CardMessage can contain up to 5 Cards

    await msg.reply(cm)

# help命令
@bot.command()
async def help(msg: Message):
    # msg 触发指令为 `/help`
    # await msg.reply(
    # CardMessage(
        # Card(
            # Module.Header('你可以用下面这些指令调戏本狸哦！'),
            # Module.Context('更多调戏方式上线中...'),
            # # Module.ActionGroup(
                # # # RETURN_VAL type(default): send an event when clicked, see print_btn_value() defined at L58
                # # Element.Button('Truth', 'RED', theme=Types.Theme.DANGER),
                # # Element.Button('Wonderland', 'BLUE', Types.Click.RETURN_VAL)),
            # Module.Section('`/help` #帮助指令\n`/val 错误码` #游戏错误码的解决方法\n`/roll 1 100` 掷色子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个色子\n'),
            # Module.Divider(),
            # Module.Section(
               # '想来本狸的家看看吗？',
                # # LINK type: user will open the link in browser when clicked
                # Element.Button('让我康康', 'https://github.com/Aewait/Valorant-kaiheila-bot', Types.Click.LINK)))))
    
    cm = CardMessage()

    c3 = Card(Module.Header('你可以用下面这些指令调戏本狸哦！'), Module.Context('更多调戏方式上线中...'))
    c3.append(Module.Section('「/help」帮助指令\n「/val 错误码」 游戏错误码的解决方法\n「/roll 1 100」 掷骰子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个骰子\n「/contdown 秒数」倒计时，默认60秒\n'))
    c3.append(Module.Divider())
    c3.append(Module.Section('游戏打累了？想来本狸的家坐坐吗~',
              Element.Button('让我康康', 'https://github.com/Aewait/Valorant-kaiheila-bot', Types.Click.LINK)))
    cm.append(c3)

    await msg.reply(cm)

# 查询错误码
@bot.command()
async def val(msg: Message, num: int):
    # msg 触发指令为 '/val 错误码'
    # msg.reply() 根据错误码回复对应解决方法
    if num == 1067:
      await msg.reply('1.请检查您的电脑是否有安装[完美对战平台]，可能有冲突；\n2.请在[控制面板]中尝试修改时区为`美国`或者`香港`，这不会影响您电脑的时间显示；\n3.尝试重启游戏、重启加速器（更换节点）、重启电脑；\n4.卸载valorant，打开csgo/ow/r6。')
    elif num == 5:
      await msg.reply('网络链接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 29:
        await msg.reply('网络链接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 10086:
      await msg.reply('本狸才不给你的手机充话费呢！')
    elif num == 10000:
      await msg.reply('本狸提醒您：谨防电信诈骗哦~')
    else:
      await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[当然!](https://f.wps.cn/w/awM5Ej4g/)')

# 掷骰子
# register command
# invoke this via saying `!roll 1 100` in channel
# or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int, t_max: int, n: int = 1):
    result = [random.randint(t_min, t_max) for i in range(n)]
    await msg.reply(f'you got: {result}')


# 凭证传好了、机器人新建好了、指令也注册完了
# 接下来就是运行我们的机器人了，bot.run() 就是机器人的起跑线

bot.run()
