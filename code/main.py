# encoding: utf-8:
from ctypes.wintypes import MSG
import json
import random
import datetime
import traceback
import requests

from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event,Client,PublicChannel,PublicMessage
from khl.card import CardMessage, Card, Module, Element, Types, Struct
from khl.command import Rule
import khl.task
from khl.guild import Guild,GuildUser

# 新建机器人，token 就是机器人的身份凭证
# 用 json 读取 config.json，装载到 config 里
# 注意文件路径，要是提示找不到文件的话，就 cd 一下工作目录/改一下这里
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])

# 向botmarket通信
@bot.task.add_interval(minutes=30)
def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'a87ebe9c-1319-4394-9704-0ad2c70e2567'}
    r = requests.post(api,headers=headers)

# 设置全局变量：机器人开发者id
master_id = '1961572535'

##########################################################################################
##########################################################################################

# @ 是「装饰器」语法，大家可以网上搜搜教程，我们这里直接用就行
# bot 是我们刚刚新建的机器人，声明这个指令是要注册到 bot 中的
# name 标示了指令的名字，名字也被用于触发指令，所以我们 /hello 才会让机器人有反应
# async def 说明这是一个异步函数，khl.py 是异步框架，所以指令也需要是异步的
# world 是函数名，可以自选；函数第一个参数的类型固定为 Message
@bot.command(name='hello')
async def world(msg: Message):
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
    c3.append(Module.Section(Element.Text("「/val 错误码」 游戏错误码的解决方法，0为已包含的val报错码信息\n「/DX」 关于DirectX Runtime报错的解决方案\n\n「/saveid '游戏id'」 保存(修改)您的游戏id\n「/myid」 让阿狸说出您的游戏id\n「/skin '皮肤名'」 查询皮肤系列包含什么枪械，仅支持英文名\n「/lead」 显示出当前游戏的排行榜。可提供参数1前多少位，参数2过滤胜场。如`/lead 20 30`代表排行榜前20位胜场超过30的玩家",Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Header('和阿狸玩小游戏吧~ '))
    c3.append(Module.Section('「/roll 1 100」 掷骰子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个骰子\n「/countdown 秒数」倒计时，默认60秒\n「更多…」 还有一些隐藏指令哦~\n'))
    c3.append(Module.Divider())
    c3.append(Module.Section(' 游戏打累了？想来本狸的家坐坐吗~',
              Element.Button('让我康康', 'https://github.com/Aewait/Valorant-kaiheila-bot', Types.Click.LINK)))
    cm.append(c3)

    await msg.reply(cm)


#################################################################################################
#################################################################################################

# 倒计时函数，单位为秒，默认60秒
@bot.command()
async def countdown(msg: Message,time: int = 60):
    cm = CardMessage()

    c1 = Card(Module.Header('本狸帮你按下秒表喽~'), color=(198, 65, 55)) # color=(90,59,215) is another available form
    c1.append(Module.Divider())
    c1.append(Module.Countdown(datetime.now() + timedelta( seconds=time), mode=Types.CountdownMode.SECOND))
    cm.append(c1)

    await msg.reply(cm)

# 掷骰子
# invoke this via saying `!roll 1 100` in channel,or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int, t_max: int, n: int = 1):
    result = [random.randint(t_min, t_max) for i in range(n)]
    await msg.reply(f'掷出来啦: {result}')


# 当有人输入“/yes @某一个用户”时这个语句被触发（感觉没用？）
@bot.command(rules=[Rule.is_mention_all])
async def yes(msg: Message, mention_str: str):
    await msg.reply(f'yes! mentioned all with {mention_str}')

# 设定自己的规则
def my_rule(msg: Message) -> bool:
    return msg.content.find('khl') != -1
# 只有包含 'khl'的语句才能触发，比如 "/test_mine khl-go"
@bot.command(name='test_mine', rules=[my_rule])
async def test_mine(msg: Message, comment: str):
    await msg.reply(f'yes! {comment} can trigger this command')

# # 正则表达式（实测无效）
# @bot.command(regex = r'(.+)\\(met\\)ID\\(met\\)')
# async def cmd(msg: Message, text: str, user_id: str):
    # #pass 
    # await msg.reply('who are u')


####################################以下是给用户上色功能的内容############################################

# 用于记录使用表情回应获取ID颜色的用户
def save_userid_color(userid:str,emoji:str):
     flag=0
     # 需要先保证原有txt里面没有保存该用户的id，才进行追加
     with open("./log/color_idsave.txt", 'r',encoding='utf-8') as fr1:
        lines=fr1.readlines()   
     #使用r+同时读写（有bug）
        for line in lines:
            v = line.strip().split(':')
            if userid == v[0]:
                flag=1 #因为用户已经回复过表情，将flag置为1
                fr1.close()
                return flag
                
     fr1.close()
     #原有txt内没有该用户信息，进行追加操作
     if flag==0:
        fw2 = open("./log/color_idsave.txt",'a+',encoding='utf-8')
        fw2.write(userid + ':' + emoji + '\n')
        fw2.close()
     
     return flag

#确认用户回复的emoji是列表里面存在的，如果不是，那就不做任何操作
def check_userid_color(emoji:str):
     flag=0
     with open("./log/color_emoji.txt", 'r',encoding='utf-8') as fr1:
        lines=fr1.readlines()   

        for line in lines:
            v = line.strip().split(':')
            if emoji == v[0]:
                flag=1 #确认用户的emoji合法 
                fr1.close()
                return flag #合法 返回1
            else:
                flag=0
     fr1.close()
     return flag #没找到，不合法，返回0

# 设置下面这个event的服务器id和消息id
Guild_ID = '3566823018281801'
Msg_ID = '5553f709-75e8-4fd9-bd2e-2eaa37f068cb'

# # 在不修改代码的前提下设置上色功能的服务器和监听消息
# @bot.command()
# async def Color_Set_CM(msg: Message,Card_Msg_id:str):
#     Guild_ID = msg.ctx.guild.id
#     Msg_ID = Card_Msg_id
#     await msg.reply(f'颜色监听服务器更新为{Guild_ID}\n监听消息更新为{Msg_ID}\n')

# 判断消息的emoji回应，并给予不同角色
@bot.on_event(EventTypes.ADDED_REACTION)
async def update_reminder(b: Bot, event: Event):
    g = await b.fetch_guild(Guild_ID)# 填入服务器id
    
    # s = await b.fetch_user('1961572535') # 填入用户id
    #print(event.body)# 这里的打印eventbody的完整内容，包含emoji_id

    #将msg_id和event.body msg_id进行对比，确认是我们要的那一条消息的表情回应
    if event.body['msg_id'] == Msg_ID:
        channel = await b.fetch_public_channel(event.body['channel_id']) #获取事件频道
        s = await b.fetch_user(event.body['user_id'])#通过event获取用户id(对象)
        
        # 判断用户回复的emoji是否合法
        is_e = check_userid_color(event.body["emoji"]['id']) 
        if is_e == 0:#回复的表情不合法
            await b.send(channel,f'你回应的表情不在列表中哦~再试一次吧！',temp_target_id=event.body['user_id'])
        else:
            # 判断该用户是否已经对这个消息做出过回应
            ret = save_userid_color(event.body['user_id'],event.body["emoji"]['id'])
            if ret == 1:
                await b.send(channel,f'你已经设置过你的ID颜色啦！修改要去找管理员哦~',temp_target_id=event.body['user_id'])
                return
            else:
                # 这里的emoji顺序和下面colorset的顺序是一样的 
                if event.body["emoji"]['id'] == '🐷':
                    await g.grant_role(s,2881825)
                    await b.send(channel, '阿狸已经给你上了粉色啦~',temp_target_id=event.body['user_id'])
                elif event.body["emoji"]['id'] == '❤':
                    await g.grant_role(s,3970687)
                    await b.send(channel, '阿狸已经给你上了红色啦~',temp_target_id=event.body['user_id'])
                elif event.body["emoji"]['id'] == '🖤':
                    await g.grant_role(s,4196071)
                    await b.send(channel, '阿狸已经给你上了黑色啦~',temp_target_id=event.body['user_id'])
                elif event.body["emoji"]['id'] == '💛':
                    await g.grant_role(s,2882418)
                    await b.send(channel, '阿狸已经给你上了黄色啦~',temp_target_id=event.body['user_id'])
                elif event.body["emoji"]['id'] == '💙':
                    await g.grant_role(s,2928540)
                    await b.send(channel, '阿狸已经给你上了蓝色啦~',temp_target_id=event.body['user_id'])
                elif event.body["emoji"]['id'] == '💜':
                    await g.grant_role(s,2907567)
                    await b.send(channel, '阿狸已经给你上了紫色啦~',temp_target_id=event.body['user_id'])
                elif event.body["emoji"]['id'] == '💚':
                    await g.grant_role(s,2904370)
                    await b.send(channel, '阿狸已经给你上了绿色啦~',temp_target_id=event.body['user_id'])
                else:
                    await b.send(channel, '你选择了默认颜色，这也挺不错的！',temp_target_id=event.body['user_id'])


# 给用户上色（在发出消息后，机器人自动添加回应）
@bot.command()
async def Color_Set1(msg: Message):
    cm = CardMessage()
    c1 = Card(Module.Header('在下面添加回应，来设置你的id颜色吧！'), Module.Context('五颜六色等待上线...'))
    c1.append(Module.Divider())
    c1.append(Module.Section('「:pig:」粉色  「:heart:」红色\n「:black_heart:」黑色  「:yellow_heart:」黄色\n'))
    c1.append(Module.Section('「:blue_heart:」蓝色  「:purple_heart:」紫色\n「:green_heart:」绿色  「:+1:」默认\n'))
    cm.append(c1)
    sent = await msg.ctx.channel.send(cm) #接受send的返回值
    # 自己new一个msg对象    
    setMSG=PublicMessage(
        msg_id= sent['msg_id'],
        _gate_ = msg.gate,
        extra={'guild_id': msg.ctx.guild.id,
            'channel_name': msg.ctx.channel,
            'author':{'id': bot.me.id}}) #extra部分留空也行
    
    # 让bot给卡片消息添加对应emoji回应
    with open("./log/color_emoji.txt", 'r',encoding='utf-8') as fr1:
        lines = fr1.readlines()   
        for line in lines:
            v = line.strip().split(':')
            await setMSG.add_reaction(v[0])
    fr1.close()
    
###########################################################################################

# 检查文件中是否有这个助力者的id
def check(it:dict):
    flag=0
    # 需要先保证原有txt里面没有保存该用户的id，才进行追加
    with open("./log/sponsor_roles.txt", 'r',encoding='utf-8') as fr1:
        lines=fr1.readlines()   
        for line in lines:
            v = line.strip().split(':')
            if it['id'] == v[0]:
                flag=1
                fr1.close()
                return flag

    fr1.close()
    #原有txt内没有该用户信息，进行追加操作
    if flag==0:
        fw2 = open("./log/sponsor_roles.txt",'a+',encoding='utf-8')
        fw2.write(it['id']+ ':' + it['nickname'] + '\n')
        fw2.close()

    return flag

# 感谢助力者（每20分钟检查一次）
@bot.task.add_interval(minutes=20)
async def thanks_sonser():
    api = "https://www.kaiheila.cn/api/v3/guild/user-list?guild_id=3566823018281801&role_id=1454428"
    headers={f'Authorization': f"Bot {config['token']}"}
    r1 = requests.get(api, headers=headers)#写入token
    json_dict = json.loads(r1.text)
    #print(r1.text)
    for its in json_dict['data']['items']:
        #print(f"{its['id']}:{its['nickname']}")
        if check(its) == 0:
            channel = await bot.fetch_public_channel("8342620158040885") #发送感谢信息的文字频道
            #print(f"(met){its['id']}(met) 感谢{its['nickname']}对本服务器的助力")
            await bot.send(channel,f"(met){its['id']}(met) 感谢{its['nickname']}对本服务器的助力")



################################################################################################


# 设置段位角色（暂时没有启用）
@bot.command()
async def rankset(msg: Message):
    cm = CardMessage()
    c1 = Card(Module.Header('在下面添加回应，来设置你的段位吧！'), Module.Context('段位更改功能等待上线...'))
    c1.append(Module.Section('「:question:」黑铁 「:eyes:」青铜\n「:sweat_drops:」白银 「:yellow_heart:」黄金\n'))
    c1.append(Module.Section('「:blue_heart:」铂金 「:purple_heart:」钻石\n「:green_heart:」翡翠 「:heart:」神话\n'))
    #c1.append(Module.Section(Element.Text('「(emj)FW摆烂(emj)[5134217138075250/D1K4o7mYAm0p80p8]」铂金',Types.Text.KMD)))
    cm.append(c1)
    await msg.ctx.channel.send(cm)

# 当有人“/狸狸 @机器人”的时候进行回复，可识别出是否为机器人作者
@bot.command(name='狸狸', rules=[Rule.is_bot_mentioned(bot)])
async def atAhri(msg: Message, mention_str: str):
    if msg.author_id == master_id:
        await msg.reply(f'主人有何吩咐呀~')
    else:
        await msg.reply(f'呀，听说有人想我了，是吗？')


# for Bilibili Up @uncle艾登
@bot.command()
async def uncle(msg: Message):
    await msg.reply('本狸才不喜欢`又硬又细`的人呢~\n[https://s1.ax1x.com/2022/06/24/jFGjHA.png](https://s1.ax1x.com/2022/06/24/jFGjHA.png)')

@bot.command()
async def test01(msg: Message):
    print(msg.ctx.guild.id)
    await msg.ctx.channel.send('正在进行测试！')
    channel = await bot.fetch_public_channel("8342620158040885")
    

###########################################################################################
####################################以下是游戏相关代码区#####################################
###########################################################################################

from val import kda123,skin123,lead123,saveid123,saveid1,saveid2,myid123,val123,dx123

# 中二病
@bot.command(name='kda')
async def kda(msg: Message):
    await kda123(msg)

# 查询皮肤系列
@bot.command()
async def skin(msg: Message,name:str):
    await skin123(msg,name)
    
# 查询排行榜
@bot.command()
async def lead(msg: Message,sz=15,num=10):
    await lead123(msg,sz,num)
 
# 存储用户游戏id
@bot.command()
async def saveid(msg: Message,game1:str):
    await saveid123(msg,game1)

# 存储id的help命令 
@bot.command(name='saveid1')
async def saveid(msg: Message):
    await saveid1(msg)
# 已保存id总数
@bot.command(name='saveid2')
async def saveid(msg: Message):
    await saveid2(msg)

# 实现读取用户游戏ID并返回
#@bot.command(rules=[Rule.is_bot_mentioned(bot)])# myid不需要at机器人
@bot.command(name="myid",aliases=['MYID']) # 这里的aliases是别名
async def myid(msg: Message):
    await myid123(msg)

# 查询游戏错误码
@bot.command()
async def val(msg: Message, num: int):
    await val123(msg,num)

#关于dx报错的解决方法
@bot.command(name='DX',aliases=['dx'])# 新增别名dx
async def dx(msg: Message):
    await dx123(msg)


# 凭证传好了、机器人新建好了、指令也注册完了
# 下面运行机器人，bot.run()是机器人的起跑线
bot.run()
