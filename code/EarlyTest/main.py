import json
import random

from khl import Bot, Message
from keep_alive import keep_alive
# 新建机器人，token 就是机器人的身份凭证
bot = Bot(token='这里输入你的机器人token ')


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

# register command
# invoke this via saying `!roll 1 100` in channel
# or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int, t_max: int, n: int = 1):
    result = [random.randint(t_min, t_max) for i in range(n)]
    await msg.reply(f'you got: {result}')


# 凭证传好了、机器人新建好了、指令也注册完了
# 接下来就是运行我们的机器人了，bot.run() 就是机器人的起跑线
keep_alive()
bot.run()
