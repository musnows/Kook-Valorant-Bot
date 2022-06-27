# encoding: utf-8:
import json
import random
import datetime

from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct
from khl.command import Rule

# 新建机器人，token 就是机器人的身份凭证
# 用 json 读取 config.json，装载到 config 里
# 注意文件路径，要是提示找不到文件的话，就 cd 一下工作目录/改一下这里
with open('./config/config.json', 'r', encoding='utf-8') as f:
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
    # 所以 msg.reply() 就是回复我们那句话
    await msg.reply('你好呀~')

# help命令
@bot.command()
async def Ahri(msg: Message):
    # msg 触发指令为 `/Ahri`,因为help指令和其他机器人冲突
    cm = CardMessage()

    c3 = Card(Module.Header('你可以用下面这些指令调戏本狸哦！'), Module.Context('更多调戏方式上线中...'))
    #实现卡片的markdown文本
    #c3.append(Module.Section(Element.Text('用`/hello`来和阿狸打个招呼吧！',Types.Text.KMD)))
    c3.append(Module.Section('「/hello」来和本狸打个招呼吧！\n「/Ahri」 帮助指令\n'))
    c3.append(Module.Divider())
    c3.append(Module.Header('上号，瓦一把！'))
    c3.append(Module.Section("「/val 错误码」 游戏错误码的解决方法，0为已包含的val报错码信息\n「/DX」 关于DirectX Runtime报错的解决方案\n\n「/saveid '游戏id'」 保存(修改)您的游戏id\n「/myid」 让阿狸说出您的游戏id\n"))
    c3.append(Module.Divider())
    c3.append(Module.Header('和阿狸玩小游戏吧~ '))
    c3.append(Module.Section('「/roll 1 100」 掷骰子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个骰子\n「/countdown 秒数」倒计时，默认60秒\n「更多…」 还有一些隐藏指令哦~\n'))
    c3.append(Module.Divider())
    c3.append(Module.Section(' 游戏打累了？想来本狸的家坐坐吗~',
              Element.Button('让我康康', 'https://github.com/Aewait/Valorant-kaiheila-bot', Types.Click.LINK)))
    cm.append(c3)

    await msg.reply(cm)




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

# 掷骰子
# register command
# invoke this via saying `!roll 1 100` in channel
# or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int, t_max: int, n: int = 1):
    result = [random.randint(t_min, t_max) for i in range(n)]
    await msg.reply(f'掷出来啦: {result}')



# 当有人输入“/yes @某一个用户”时这个语句被触发（感觉没用？）
@bot.command(rules=[Rule.is_mention_all])
async def yes(msg: Message, mention_str: str):
    await msg.reply(f'yes! mentioned all with {mention_str}')
    
# besides built-in rules in Rule.*, you can define your own rules
def my_rule(msg: Message) -> bool:
    return msg.content.find('khl') != -1

# this command can only be triggered with msg that contains 'khl' such as /test_mine khl-go
@bot.command(name='test_mine', rules=[my_rule])
async def test_mine(msg: Message, comment: str):
    await msg.reply(f'yes! {comment} can trigger this command')
  
  
# # a example to combine decorator and rule
# def is_contains(keyword: str):
    # def func(msg: Message):
        # return msg.content.find(keyword) != -1

    # return func

# # Q: how to trigger this command?
# # /test_decorator 2022-06-23
# @bot.command(name='test_decorator', rules=[is_contains(str(datetime.date.today()))])
# async def test_decorator(msg: Message, date: str):
    # await msg.reply(f'yes! today is {date}')


 
# 实现存储用户游戏ID
# @bot.command(name='saveid',rules=[Rule.is_bot_mentioned(bot)])
#async def saveid(msg: Message,game1:str,mention_str: str):
@bot.command()
async def saveid(msg: Message,game1:str):
     #gamerid = {'user_id':msg.author_id,'gameid':game1}
     flag=0
     # 需要先保证原有txt里面没有保存该用户的id，才进行追加
     with open("./log/idsave.txt", 'r') as fr1:
        lines=fr1.readlines()   
     #使用r+同时读写（有bug）
     with open("./log/idsave.txt", 'w') as fw1: 
        for line in lines:
            v = line.strip().split(':')
            if msg.author_id == v[0]:
                fw1.write(msg.author_id+ ':' + game1 + '\n')
                await msg.reply(f'本狸已经修改好你的游戏id啦!')
                flag=1#修改完毕后，将flag置为1
            else:
                fw1.write(line)
     fr1.close()
     fw1.close()
     #原有txt内没有该用户信息，进行追加操作
     if flag==0:
        fw2 = open("./log/idsave.txt",'a+')
        #fw.write(str(gamerid))      #把字典转化为str
        fw2.write(msg.author_id+':'+game1+'\n')  
        await msg.reply(f'本狸已经记下你的游戏id啦!')
        fw2.close()

# 让阿狸记住游戏id的help指令
@bot.command()
async def saveid1(msg: Message):
    await msg.reply("基本方式看图就行啦！如果你的id之中有空格，需要用**英文的单引号**括起来哦！就像这样: `/saveid '你的id'`\n[https://s1.ax1x.com/2022/06/27/jV2qqe.png](https://s1.ax1x.com/2022/06/27/jV2qqe.png)")

     
# 实现读取用户游戏ID并返回
#@bot.command(rules=[Rule.is_bot_mentioned(bot)])
@bot.command() #/myid不需要at机器人
async def myid(msg: Message):
    flag=0
    fr = open("./log/idsave.txt",'r')
    for line in fr:
        v = line.strip().split(':')
        if msg.author_id in v[0]:
           flag=1#找到了对应用户的id
           await msg.reply(f'游戏id: '+v[1])
    fr.close()
    if flag==0:
       await msg.reply("狸狸不知道你的游戏id呢，用`/saveid`告诉我吧！\n基本方式看图就行啦！如果你的id之中有空格，需要用英文的单引号括起来哦！就像这样: `/saveid '你的id'`\n[https://s1.ax1x.com/2022/06/27/jV2qqe.png](https://s1.ax1x.com/2022/06/27/jV2qqe.png)")



# # 正则表达式（实测无效）
# @bot.command(regex = r'(.+)\\(met\\)ID\\(met\\)')
# async def cmd(msg: Message, text: str, user_id: str):
    # #pass 
    # await msg.reply('who are u')



# 查询游戏错误码
@bot.command()
async def val(msg: Message, num: int):
    # msg 触发指令为 '/val 错误码'
    # msg.reply() 根据错误码回复对应解决方法
    if num ==0:
        await msg.reply('目前支持查询的错误信息有：\n「val 1,4-5,7-21,29,31,33,38,43-46,49-70,81,84,128,152,1067,9001,9002」')
    elif num == 1067:
        await msg.reply('1.请检查您的电脑是否有安装「完美对战平台」，可能有冲突；\n2.请在「控制面板-时钟和区域」中尝试修改时区为`美国`或者`香港`，这不会影响您电脑的时间显示；\n3.尝试重启游戏、重启加速器（更换节点）、重启电脑；\n4.可能和您的鼠标驱动有冲突，尝试关闭雷蛇/罗技的鼠标驱动软件;\n5.卸载valorant，打开csgo/ow/r6。')
    elif num == 1:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 4:
        await msg.reply('您的名称无效，请重新注册账户')
    elif num == 5:
        await msg.reply('1.账户在别处登录；\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 7:
        await msg.reply('账户可能被冻结，请查看注册邮箱是否有相关邮件信息')
    elif num > 7 and num <=11:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 12:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num >= 13 and num <=21:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 29:
        await msg.reply('1.防火墙问题，尝试关闭系统防火墙；\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 31:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 33:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num == 38:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 43:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num >= 44 and num <= 45:
        await msg.reply('反作弊未初始化：重启拳头客户端,如果未恢复,先卸载Vanguard,重启电脑后再启动游戏')
    elif num == 46:
        await msg.reply('服务器维护中……')
    elif num >= 49 and num <= 60:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 61:
        await msg.reply('哎呀你干了啥，怎么被系统ban了？狸狸可不喜欢你这样哦~')
    elif num >= 62 and num <= 67:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 68:
        await msg.reply('1.请尝试关闭valorant，右键图标以管理员身份运行游戏\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num >= 69 and num <= 70:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 81:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 84:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 128:
        await msg.reply('1.重启电脑和游戏客户端，卸载Vanguard、卸载游戏进行重装；\n2.需要提醒您，修改系统配置是一项有风险的操作，请确认您需要这么做！\n请查看本图进行操作:[https://s1.ax1x.com/2022/06/24/jFGXBd.png](https://s1.ax1x.com/2022/06/24/jFGXBd.png) ')
        #这里要使用[URL](URL)的方式，让开黑啦实别出图片并直接显示
    elif num == 152:
        await msg.reply('您的硬件被识别封锁，这可不是一个好兆头。')
    elif num == 9001:
        await msg.reply('`VAN9001_This build of Vanguard requires TPM version 2.0 and secure boot to be enabled in order to play.`\n需要您进电脑主板的bios打开tmp2.0哦！')
    elif num == 9002:
        await msg.reply('`VAN9002—This build of Vanguard requires Control Flow Guard (CFG)to be enabled in system exploit protection settings.`\n设置页面搜索Exploit Protection ，[开启控制流保护（CFG）](https://www.bilibili.com/read/cv11536577)。')
    elif num == 10086:
        await msg.reply('本狸才不给你的手机充话费呢！')
    elif num == 10000:
        await msg.reply('本狸提醒您：谨防电信诈骗哦~')
    else:
        await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[当然!](https://f.wps.cn/w/awM5Ej4g/)')

#关于dx报错的解决方法
@bot.command(name='DX')
async def world(msg: Message):
    await msg.reply('报错弹窗内容为`The following component(s) are required to run this program:DirectX Runtime`\n需要下载微软官方驱动安装，官网搜索[DirectX End-User Runtime Web Installer]\n你还可以下载本狸亲测可用的DX驱动 [链接](https://pan.baidu.com/s/1145Ll8vGtByMW6OKk6Zi2Q)，暗号是1067哦！\n狸狸记得之前玩其他游戏的时候，也有遇到过这个问题呢~')


# 当有人“/狸狸 @机器人”的时候进行回复
# register command and add a rule
# invoke this via saying `/hello @{bot_name}` in channel
@bot.command(name='狸狸', rules=[Rule.is_bot_mentioned(bot)])
async def atAhri(msg: Message, mention_str: str):
    if msg.author_id == '1961572535':
        await msg.reply(f'主人有何吩咐呀~')
    else:
        await msg.reply(f'呀，听说有人想我了，是吗？')


@bot.command()
async def uncle(msg: Message):
    await msg.reply('本狸才不喜欢`又硬又细`的人呢~\n[https://s1.ax1x.com/2022/06/24/jFGjHA.png](https://s1.ax1x.com/2022/06/24/jFGjHA.png)')


# 凭证传好了、机器人新建好了、指令也注册完了
# 接下来就是运行我们的机器人了，bot.run() 就是机器人的起跑线

bot.run()
