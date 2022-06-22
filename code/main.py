# encoding: utf-8:

import json
import random

from khl import Bot, Message
# from keep_alive import keep_alive

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

@bot.command()
async def val(msg: Message, num: int):
    # msg 指的是我们所发送的那句 `/hello`
    # 所以 msg.reply() 就是回复我们那句话，回复的内容是 `world!`
    if num == 1067:
      await msg.reply('1.请检查您的电脑是否有安装[完美对战平台]，可能有冲突；\n2.请在[控制面板]中尝试修改时区为`美国`或者`香港`，这不会影响您电脑的时间显示；\n3.尝试重启游戏、重启加速器（更换节点）、重启电脑；\n4.卸载valorant，打开csgo/ow/r6。')
    elif num == 5:
      await msg.reply('网络链接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 10086:
      await msg.reply('本狸才不给你的手机充话费呢！')
    elif num == 10000:
      await msg.reply('本狸提醒您：谨防电信诈骗哦~')
    else:
      await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[好!](https://f.wps.cn/w/awM5Ej4g/)')

# register command
# invoke this via saying `!roll 1 100` in channel
# or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int, t_max: int, n: int = 1):
    result = [random.randint(t_min, t_max) for i in range(n)]
    await msg.reply(f'you got: {result}')


# 凭证传好了、机器人新建好了、指令也注册完了
# 接下来就是运行我们的机器人了，bot.run() 就是机器人的起跑线
# keep_alive()
bot.run()
