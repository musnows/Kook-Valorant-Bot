# encoding: utf-8:
import json
import random
import time
import datetime
import aiohttp
import requests

from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event,Client,PublicChannel,PublicMessage
from khl.card import CardMessage, Card, Module, Element, Types
from khl.command import Rule

#忽略PytzUsageWarning相关警告(由bot task引发的报错)
from warnings import filterwarnings
from pytz_deprecation_shim import PytzUsageWarning
filterwarnings('ignore', category=PytzUsageWarning)


with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])

Botoken=config['token']
kook="https://www.kookapp.cn"
headers={f'Authorization': f"Bot {Botoken}"}

# 设置全局变量：机器人开发者id/报错频道
master_id = '1961572535'
Debug_ch  = '6248953582412867'

# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'a87ebe9c-1319-4394-9704-0ad2c70e2567'}
    # r = requests.post(api,headers=headers)
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)
    
##########################################################################################
##########################################################################################

def GetTime(): #将获取当前时间封装成函数方便使用
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

# 开机的时候打印一次时间，记录重启时间
print(f"Start at: [%s]"%GetTime())

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    #print(type(msg))
    now_time = GetTime()
    if f"{type(msg)}"=="<class 'khl.message.PrivateMessage'>":
        print(f"[{now_time}] PrivateMessage - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")
    else:
        print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")


@bot.command(name='hello')
async def world(msg: Message):
    logging(msg)
    await msg.reply('你好呀~')

# help命令
@bot.command(name='Ahri',aliases=['阿狸'])
async def Ahri(msg: Message,*arg):
    logging(msg)
    try:
        # msg 触发指令为 `/Ahri`,因为help指令和其他机器人冲突
        cm = CardMessage()
        c3 = Card(Module.Header('你可以用下面这些指令呼叫本狸哦！'), Module.Context('更多玩耍方式上线中...'))
        #c3.append(Module.Section(Element.Text('用`/hello`来和阿狸打个招呼吧！',Types.Text.KMD))) #实现卡片的markdown文本
        c3.append(Module.Section('「/hello」来和本狸打个招呼吧！\n「/Ahri」 帮助指令\n'))
        c3.append(Module.Divider())
        c3.append(Module.Header('上号，瓦一把！'))
        c3.append(Module.Section(Element.Text("「/val 错误码」 游戏错误码的解决方法，0为已包含的val报错码信息\n「/dx」 关于DirectX Runtime报错的解决方案\n「/saveid 游戏id」 保存(修改)您的游戏id\n「/myid」 让阿狸说出您的游戏id\n「/skin 皮肤名」 查询皮肤系列包含什么枪械，仅支持英文名\n「/lead」 显示出当前游戏的排行榜。可提供参数1前多少位，参数2过滤胜场。如`/lead 20 30`代表排行榜前20位胜场超过30的玩家",Types.Text.KMD)))
        c3.append(Module.Divider())
        c3.append(Module.Header('和阿狸玩小游戏吧~ '))
        c3.append(Module.Section('「/roll 1 100」掷骰子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个骰子\n「/countdown 秒数」倒计时，默认60秒\n「/TL 内容」翻译内容，支持多语译中和中译英\n「/TLON」 在本频道打开实时翻译\n「/TLOFF」在本频道关闭实时翻译\n「/we 城市」查询城市未来3天的天气情况\n「更多…」还有一些隐藏指令哦~\n'))
        c3.append(Module.Divider())
        c3.append(Module.Section(' 游戏打累了？想来本狸的家坐坐吗~',
                Element.Button('让我康康', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm.append(c3)

        await msg.reply(cm)

    except Exception as result:
        err_str=f"ERR! [{GetTime()}] Ahri - {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_ch)
        await bot.send(debug_channel,err_str)

#################################################################################################
#################################################################################################

# 倒计时函数，单位为秒，默认60秒
@bot.command()
async def countdown(msg: Message,time: int = 60):
    logging(msg)
    try:
        cm = CardMessage()
        c1 = Card(Module.Header('本狸帮你按下秒表喽~'), color=(198, 65, 55)) # color=(90,59,215) is another available form
        c1.append(Module.Divider())
        c1.append(Module.Countdown(datetime.now() + timedelta( seconds=time), mode=Types.CountdownMode.SECOND))
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] countdown- {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_ch)
        await bot.send(debug_channel,err_str)


# 掷骰子 saying `!roll 1 100` in channel,or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int=1, t_max: int=100, n: int = 1):
    logging(msg)
    try:
        result = [random.randint(t_min, t_max) for i in range(n)]
        await msg.reply(f'掷出来啦: {result}')
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] roll - {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_ch)
        await bot.send(debug_channel,err_str)

################################以下是给用户上色功能的内容########################################

# 预加载文件
with open("./log/color_idsave.json", 'r',encoding='utf-8') as frcl:
    ColorIdDict = json.load(frcl)

with open("./config/color_emoji.txt", 'r',encoding='utf-8') as fremoji:
    EmojiLines=fremoji.readlines()   


# 用于记录使用表情回应获取ID颜色的用户
def save_userid_color(userid:str,emoji:str):
    global ColorIdDict
    flag=0
    # 需要先保证原有txt里面没有保存该用户的id，才进行追加
    if userid in ColorIdDict.keys():
        flag=1 #因为用户已经回复过表情，将flag置为1
        return flag
    #原有txt内没有该用户信息，进行追加操作
    ColorIdDict[userid]=emoji
    with open("./log/color_idsave.json",'w',encoding='utf-8') as fw2:
        json.dump(ColorIdDict,fw2,indent=2,sort_keys=True, ensure_ascii=False)
        
    return flag


# 设置自动上色event的服务器id和消息id
Guild_ID = '3566823018281801'
Msg_ID = '6fec1aeb-9d5c-4642-aa95-862e3db8aa61'

# # 在不修改代码的前提下设置上色功能的服务器和监听消息
@bot.command()
async def Color_Set_GM(msg: Message,Card_Msg_id:str):
    logging(msg)
    global Guild_ID,Msg_ID #需要声明全局变量
    Guild_ID = msg.ctx.guild.id
    Msg_ID = Card_Msg_id
    await msg.reply(f'颜色监听服务器更新为 {Guild_ID}\n监听消息更新为 {Msg_ID}\n')


# 判断消息的emoji回应，并给予不同角色
@bot.on_event(EventTypes.ADDED_REACTION)
async def update_reminder(b: Bot, event: Event):
    g = await b.fetch_guild(Guild_ID)# 填入服务器id
    #将msg_id和event.body msg_id进行对比，确认是我们要的那一条消息的表情回应
    if event.body['msg_id'] == Msg_ID:
        now_time = GetTime()#记录时间
        print(f"[{now_time}] React:{event.body}")# 这里的打印eventbody的完整内容，包含emoji_id

        channel = await b.fetch_public_channel(event.body['channel_id']) #获取事件频道
        s = await b.fetch_user(event.body['user_id'])#通过event获取用户id(对象)
        # 判断用户回复的emoji是否合法
        emoji=event.body["emoji"]['id']
        flag=0
        for line in EmojiLines:
            v = line.strip().split(':')
            if emoji == v[0]:
                flag=1 #确认用户回复的emoji合法 
                ret = save_userid_color(event.body['user_id'],event.body["emoji"]['id'])# 判断用户之前是否已经获取过角色
                if ret ==1: #已经获取过角色
                    await b.send(channel,f'你已经设置过你的ID颜色啦！修改要去找管理员哦~',temp_target_id=event.body['user_id'])
                    return
                else:
                    role=int(v[1])
                    await g.grant_role(s,role)
                    await b.send(channel, f'阿狸已经给你上了 {emoji} 对应的颜色啦~',temp_target_id=event.body['user_id'])

        if flag == 0: #回复的表情不合法
            await b.send(channel,f'你回应的表情不在列表中哦~再试一次吧！',temp_target_id=event.body['user_id'])


# 给用户上色（在发出消息后，机器人自动添加回应）
@bot.command()
async def Color_Set(msg: Message):
    logging(msg)
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
        extra={'guild_id': msg.ctx.guild.id,'channel_name': msg.ctx.channel,'author':{'id': bot.me.id}}) 
        # extra部分留空也行
    # 让bot给卡片消息添加对应emoji回应
    for line in EmojiLines:
        v = line.strip().split(':')
        await setMSG.add_reaction(v[0])
    

#########################################感谢助力者###############################################

# 预加载文件
with open("./log/sponsor_roles.json", 'r',encoding='utf-8') as frsp:
    SponsorDict = json.load(frsp)

# 检查文件中是否有这个助力者的id
def check_sponsor(it:dict):
    global SponsorDict
    flag=0
    # 需要先保证原有txt里面没有保存该用户的id，才进行追加
    if it['id'] in SponsorDict.keys():
        flag=1
        return flag

    #原有txt内没有该用户信息，进行追加操作
    SponsorDict[it['id']]=it['nickname']
    with open("./log/sponsor_roles.json",'w',encoding='utf-8') as fw2:
        json.dump(SponsorDict,fw2,indent=2,sort_keys=True, ensure_ascii=False)        

    return flag

# 感谢助力者（每20分钟检查一次）
@bot.task.add_interval(minutes=20)
async def thanks_sonser():
    #在api链接重需要设置服务器id和助力者角色的id
    api = "https://www.kaiheila.cn/api/v3/guild/user-list?guild_id=3566823018281801&role_id=1454428"

    async with aiohttp.ClientSession() as session:
        async with session.post(api, headers=headers) as response:
            json_dict = await response.json()

    for its in json_dict['data']['items']:
        #print(f"{its['id']}:{its['nickname']}")
        if check_sponsor(its) == 0:
            channel = await bot.fetch_public_channel("8342620158040885") #发送感谢信息的文字频道
            await bot.send(channel,f"感谢 (met){its['id']}(met) 对本服务器的助力")
            print(f"[%s] 感谢{its['nickname']}对本服务器的助力"%GetTime())


######################################## Translate ################################################

from translate import youdao_translate,caiyun_translate,is_CN

# 单独处理met和rol消息，不翻译这部分内容
def deleteByStartAndEnd(s, start, end):
    # 找出两个字符串在原始字符串中的位置
    # 开始位置是：开始始字符串的最左边第一个位置；
    # 结束位置是：结束字符串的最右边的第一个位置
    while s.find(start) != -1:
        x1 = s.find(start)
        x2 = s.find(end,x1+5) + len(end)  # s.index()函数算出来的是字符串的最左边的第一个位置，所以需要加上长度找到末尾
        # 找出两个字符串之间的内容
        x3 = s[x1:x2]
        # 将内容替换为空字符串s
        s = s.replace(x3, "")

    print(f'Handel{start}: {s}')
    return s


# 调用翻译,有道和彩云两种引擎（有道寄了就用彩云）
async def translate(msg: Message,*arg):
    word = " ".join(arg)
    ret = word
    if '(met)' in word:
        ret = deleteByStartAndEnd(word,'(met)','(met)')
    elif '(rol)' in word:
        ret = deleteByStartAndEnd(word,'(rol)','(rol)')
    #重新赋值
    word = ret
    try:
        cm = CardMessage()
        c1 = Card(Module.Section(Element.Text(f"**翻译结果(Result):** {youdao_translate(word)}",Types.Text.KMD)), Module.Context('来自: 有道翻译'))
        cm.append(c1)
        #await msg.ctx.channel.send(cm)
        await msg.reply(cm)
    except:
        cm = CardMessage()
        if is_CN(word):
            c1 = Card(Module.Section(Element.Text(f"**翻译结果(Result):** {await caiyun_translate(word,'auto2en')}",Types.Text.KMD)), Module.Context('来自: 彩云小译，中译英'))
        else:
            c1 = Card(Module.Section(Element.Text(f"**翻译结果(Result):** {await caiyun_translate(word,'auto2zh')}",Types.Text.KMD)), Module.Context('来自: 彩云小译，英译中'))
            
        cm.append(c1)
        await msg.reply(cm)
   

# 普通翻译指令
@bot.command(name='TL',aliases=['tl'])
async def translate1(msg: Message,*arg):
    logging(msg)
    await translate(msg,' '.join(arg))   

# 实时翻译栏位
ListTL = ['0','0','0','0']

# 查看目前已经占用的容量
def checkTL():
    sum=0
    for i in ListTL:
        if i !='0':
            sum+=1
    return sum

#查看当前占用的实时翻译栏位
@bot.command()
async def CheckTL(msg:Message):
    logging(msg)
    global ListTL
    await msg.reply(f"目前已使用栏位:{checkTL()}/{len(ListTL)}")

# 关闭所有栏位的实时翻译（避免有些人用完不关）
@bot.command()
async def ShutdownTL(msg:Message):
    logging(msg)
    if msg.author.id != master_id:
        return#这条命令只有bot的作者可以调用
    global ListTL
    if checkTL()==0:
        await msg.reply(f"实时翻译栏位为空: {checkTL()}/{len(ListTL)}")
        return
    i=0
    while i< len(ListTL):
        if(ListTL[i])!='0': #不能对0的频道进行操作
            channel = await bot.fetch_public_channel(ListTL[i]) 
            await bot.send(channel,"不好意思，阿狸的主人已经清空了实时翻译的栏位！")
            ListTL[i] = '0'
        i+=1
    await msg.reply(f"实时翻译栏位已清空！目前为: {checkTL()}/{len(ListTL)}")

# 通过频道id判断是否实时翻译本频道内容
@bot.command(regex=r'(.+)')
async def TL_Realtime(msg:Message,*arg):
    word = " ".join(arg)
    # 不翻译关闭实时翻译的指令
    if word == "/TLOFF" or word == "/tloff" or word=='/tlon' or word =='/TLON':
        return
    global ListTL
    if msg.ctx.channel.id in ListTL:
        logging(msg)
        await translate(msg,' '.join(arg))
        return

# 开启实时翻译功能
@bot.command(name='TLON',aliases=['tlon'])
async def TLON(msg: Message):
    #print(msg.ctx.channel.id)
    logging(msg)
    global ListTL
    if checkTL() == len(ListTL):
        await msg.reply(f"目前栏位: {checkTL()}/{len(ListTL)}，已满！")
        return
    #发现bug，同一个频道可以开启两次实时翻译，需要加一个判断
    if msg.ctx.channel.id in ListTL:
         await msg.reply(f"本频道已经开启了实时翻译功能，请勿重复操作!")
         return
    i=0
    while i< len(ListTL):
        if ListTL[i] == '0':
            ListTL[i] = msg.ctx.channel.id
            break
        i+=1
    ret = checkTL()
    await msg.reply(f"Real-Time Translation ON\n阿狸现在会实时翻译本频道的对话啦！\n目前栏位: {ret}/{len(ListTL)}，使用`/TLOFF`可关闭实时翻译哦~")

# 关闭实时翻译功能
@bot.command(name='TLOFF',aliases=['tloff'])
async def TLOFF(msg: Message):
    logging(msg)
    global ListTL
    i=0
    while i< len(ListTL):
        if ListTL[i] == msg.ctx.channel.id:
            ListTL[i] = '0'
            await msg.reply(f"Real-Time Translation OFF！目前栏位: {checkTL()}/{len(ListTL)}")
            return
        i+=1
    await msg.reply(f"本频道并没有开启实时翻译功能！目前栏位: {checkTL()}/{len(ListTL)}")
    

######################################## Other ################################################

from other import history,weather

# 返回历史上的今天
@bot.command(name='hs')
async def History(msg: Message):
    logging(msg)
    #await history(msg)
    await msg.reply(f"抱歉，`hs` 功能已被取消！")

# 返回天气
@bot.command(name='we')
async def Weather(msg: Message,city:str="err"):
    logging(msg)
    if city=="err":
        await msg.reply(f"函数参数错误，城市: `{city}`\n")
        return

    try:
        await weather(msg,city)
    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json错误是因为消息无法成功创建\n"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

# 设置段位角色（暂时没有启用）
@bot.command()
async def rankset(msg: Message):
    logging(msg)
    cm = CardMessage()
    c1 = Card(Module.Header('在下面添加回应，来设置你的段位吧！'), Module.Context('段位更改功能等待上线...'))
    c1.append(Module.Section('「:question:」黑铁 「:eyes:」青铜\n「:sweat_drops:」白银 「:yellow_heart:」黄金\n'))
    c1.append(Module.Section('「:blue_heart:」铂金 「:purple_heart:」钻石\n「:green_heart:」翡翠 「:heart:」神话\n'))
    cm.append(c1)
    await msg.ctx.channel.send(cm)


# 当有人“/狸狸 @机器人”的时候进行回复，可识别出是否为机器人作者
@bot.command(name='狸狸', rules=[Rule.is_bot_mentioned(bot)])
async def atAhri(msg: Message, mention_str: str):
    logging(msg)
    if msg.author_id == master_id:
        await msg.reply(f'主人有何吩咐呀~')
    else:
        await msg.reply(f'呀，听说有人想我了，是吗？')


# for Bilibili Up @uncle艾登
@bot.command()
async def uncle(msg: Message):
    logging(msg)
    await msg.reply('本狸才不喜欢`又硬又细`的人呢~\n[https://s1.ax1x.com/2022/06/24/jFGjHA.png](https://s1.ax1x.com/2022/06/24/jFGjHA.png)')

    
###########################################################################################
####################################以下是游戏相关代码区#####################################
###########################################################################################

from val import kda123,skin123,lead123,saveid123,saveid_1,saveid_2,myid123,val123,dx123
from status import status_active_game,status_active_music,status_delete,server_status


# 开始打游戏
@bot.command()
async def gaming(msg: Message,game:int=1):
    logging(msg)
    #await bot.client.update_playing_game(3,1)# 英雄联盟
    if game ==1:    
        ret = await status_active_game(453027) # 瓦洛兰特
        await msg.reply(f"{ret['message']}，阿狸上号valorant啦！")
    elif game ==2:
        ret = await status_active_game(3)      # 英雄联盟
        await msg.reply(f"{ret['message']}，阿狸上号LOL啦！")

# 开始听歌
@bot.command()
async def singing(msg: Message,music:str="err",singer:str="err"):
    logging(msg)
    if music=="err" or singer=="err":
        await msg.reply(f"函数参数错误，music: `{music}` singer: `{singer}`")
        return 

    ret = await status_active_music(music,singer) 
    await msg.reply(f"{ret['message']}，阿狸开始听歌啦！")
    

# 停止打游戏1/听歌2
@bot.command(name='sleeping')
async def sleeping(msg: Message,d:int=1):
    logging(msg)
    ret = await status_delete(d)
    if d ==1:
        await msg.reply(f"{ret['message']}，阿狸下号休息啦!")
    elif d==2:
        await msg.reply(f"{ret['message']}，阿狸摘下了耳机~")
    #await bot.client.stop_playing_game()

# 中二病
@bot.command(name='kda')
async def kda(msg: Message):
    logging(msg)
    await kda123(msg)

# 查询皮肤系列
@bot.command()
async def skin(msg: Message,name:str="err"):
    logging(msg)
    if name =="err":
        await msg.reply(f"函数参数错误，name: `{name}`\n")
        return
    #name=" ".join(arg)
    await skin123(msg,name)
    
# 查询排行榜
@bot.command()
async def lead(msg: Message,sz:int=15,num:int=10):
    logging(msg)
    await lead123(msg,sz,num)
 

# 存储用户游戏id
@bot.command()
async def saveid(msg: Message,*args):
    logging(msg)
    try:
        game_id = " ".join(args)#避免用户需要输入双引号
        await saveid123(msg, game_id)
    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json错误是因为消息无法成功创建\n"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 存储id的help命令 
@bot.command(name='saveid1')
async def saveid1(msg: Message):
    logging(msg)
    await saveid_1(msg)

# 已保存id总数
@bot.command(name='saveid2')
async def saveid2(msg: Message):
    logging(msg)
    try:
        await saveid_2(msg)
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] check_server_user_status: {result}"
        print(err_str)
        await msg.reply(err_str)


# 实现读取用户游戏ID并返回
@bot.command(name="myid",aliases=['MYID']) # 这里的aliases是别名
async def myid(msg: Message,*args):
    logging(msg)
    if args !=():
        await msg.reply(f"`/myid`命令不需要参数！")
        return

    try:
        await myid123(msg)
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] check_server_user_status: {result}"
        print(err_str)
        await msg.reply(err_str)

# str转int
from functools import reduce
def str2int(s):
     return reduce(lambda x,y:x*10+y, map(lambda s:{'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}[s], s))

# 查询游戏错误码
@bot.command(name='val',aliases=['van','VAN','VAL'])
async def val(msg: Message, numS:str="err"):
    logging(msg)
    if numS=="err":
        await msg.reply(f"函数参数错误，请提供正确范围的错误码")
        return
    try:
        num=str2int(numS) 
        await val123(msg,num)
    except Exception as result:
        await msg.reply(f"您输入的错误码格式不正确！\n请提供正确范围的`数字`,而非`{numS}`")

#关于dx报错的解决方法
@bot.command(name='DX',aliases=['dx'])# 新增别名dx
async def dx(msg: Message):
    logging(msg)
    await dx123(msg)


#多出来的import
import copy
import riot_auth
import aiofiles
import io  #用于将 图片url 转换成可被打开的二进制
from PIL import Image, ImageDraw, ImageFont  #用于合成图片
import zhconv  #用于繁体转简体（因为部分字体不支持繁体
import math  #用于小数取整
from val import authflow,fetch_daily_shop,fetch_user_gameID,fetch_valorant_point,fetch_item_price,fetch_item_iters,fetch_skins_all

standard_length = 1000  #图片默认边长
# 用math.floor 是用来把float转成int 我也不晓得为啥要用 但是不用会报错（我以前不用也不会）
# 所有的数都  * standard_length / 1000 是为了当标准边长变动时这些参数会按照比例缩放
standard_length_sm = math.floor(standard_length / 2)  # 组成四宫格小图的边长
stardard_blank_sm = 60 * standard_length / 1000  # 小图左边的留空
stardard_icon_resize_ratio = 0.59 * standard_length / 1000  #枪的默认缩放
standard_icon_top_blank = math.floor(180 * standard_length /
                                     1000)  # 枪距离图片顶部的像素
standard_text_position = (math.floor(130 * standard_length / 1000),
                          math.floor(317 * standard_length / 1000))  #默认文字位置
standard_price_position = (math.floor(280 * standard_length / 1000),
                           math.floor(120 * standard_length / 1000))  #皮肤价格文字位置
standard_level_icon_reszie_ratio = 0.13 * standard_length / 1000  #等级icon图标的缩放
standard_level_icon_position = (math.floor(350 * standard_length /1000),
                                math.floor(120 * standard_length /1000))  # 等级icon图标的坐标

resp = {}  #没有那个resp数据 为了防止报错

font_color = '#ffffff'  #文字颜色：白色
bg_main = Image.open(
    io.BytesIO(
        requests.get(
            'https://img.kookapp.cn/assets/2022-08/WsjGI7PYuf0rs0rs.png').
        content))  #背景

def sm_comp(icon, name,price,level_icon):
    bg = Image.new(mode='RGBA',
                   size=(standard_length_sm, standard_length_sm))  #新建一个画布
    # 处理武器图片
    layer_icon = Image.open(io.BytesIO(requests.get(icon).content))  # 打开武器图片
    w, h = layer_icon.size  #读取武器图片长宽
    new_w = math.floor(w * stardard_icon_resize_ratio)  #按比例缩放的长
    new_h = math.floor(h * stardard_icon_resize_ratio)  #按比例缩放的宽
    layer_icon = layer_icon.resize((new_w, new_h), Image.Resampling.LANCZOS) 
    # 按缩放比例后的长宽进行resize（resize就是将图像原长宽拉伸到新长宽） Image.Resampling.LANCZOS 是一种处理方式
    left_position = math.floor((standard_length_sm - new_w) /2) 
    # 用小图的宽度减去武器图片的宽度再除以二 得到武器图片x轴坐标  y轴坐标 是固定值 standard_icon_top_blank
    bg.paste(layer_icon, (left_position, standard_icon_top_blank), layer_icon)
    # bg.paste代表向bg粘贴一张图片
    # 第一个参数是图像layer_icon 
    # 第二个参数(left_position, standard_icon_top_blank)就是刚刚算出来的 x,y 坐标 最后一个layer_icon是蒙版

    # 处理武器level的图片
    Level_icon = Image.open(io.BytesIO(requests.get(level_icon).content))  # 打开武器图片
    w, h = Level_icon.size  #读取武器图片长宽
    new_w = math.floor(w * standard_level_icon_reszie_ratio )  #按比例缩放的长
    new_h = math.floor(h * standard_level_icon_reszie_ratio )  #按比例缩放的宽
    Level_icon = Level_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    bg.paste(Level_icon, standard_level_icon_position, Level_icon)


    name = zhconv.convert(name, 'zh-cn')  #将名字简体化
    name_list = name.split(' ')  #将武器名字分割换行
    if len(name_list[0])>5:
        text = ''.join(name_list[0]) + '\n'  #如果武器名很长就不用加
    else:
        text = ' '.join(name_list[0]) + '\n'  #向武器名字添加空格增加字间距
    interval = len(name_list[0])
    #print(len(name_list))
    if len(name_list) > 2:
        i = 1
        while i <= len(name_list) - 2:
            name_list[0] = name_list[0] + ' ' + name_list[i]
            #print(name_list[0])
            i += 1
        interval = len(name_list[0])
        name_list[1] = name_list[len(name_list) - 1]
        text = name_list[0] + '\n'
    if len(name_list) > 1: #有些刀皮肤只有一个元素
        # if len(name_list[1]) > 3:
        #     interval = interval - len(name_list[1]) - 2
        interval = interval - interval//3
        for i in range(interval):  #第二行前半部分要留空 根据第一行的字数加空格
            text += '　'
        text += ' '.join(name_list[1])  #插入第二行字符
    draw = ImageDraw.Draw(bg)  # emmm大概就是让bg这个图层能被写字
    #第一个参数 standard_text_position 是固定参数坐标 ， 第二个是文字内容 ， 第三个是字体 ， 第四个是字体颜色
    draw.text(standard_text_position,
              text,
              font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 30),
              fill=font_color)
    text=f"{price}"#价格
    draw.text(standard_price_position,
            text,
            font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 30),
            fill=font_color)
    #bg.show() #测试用途，展示图片(linux貌似不可用)
    return bg

def bg_comp(bg, img, x, y):
    position = (x, y)
    bg.paste(img, position, img)  #如sm—comp中一样，向bg粘贴img
    return bg


##############################################################################

# 预加载
with open("./log/UserAuth.json", 'r', encoding='utf-8') as frau:
    UserAuthDict = json.load(frau)
# 所有皮肤
with open("./config/ValSkin.json", 'r', encoding='utf-8') as frsk:
    ValSkinList = json.load(frsk)

# 登录，保存用户的token
@bot.command(name='login')
async def login_authtoekn(msg: Message,user: str = 'err',passwd: str = 'err',*arg):
    print(f"[{GetTime()}] Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = /login")
    if passwd == 'err' or user == 'err':
        await msg.reply(f"参数不完整，请提供您的账户和密码！\naccout: `{user}` passwd: `{passwd}`")
        return

    elif arg!=():
        await msg.reply(f"您给予了多余的参数！\naccout: `{user}` passwd: `{passwd}`\n多余参数: `{arg}`")
        return

    try:
        global UserAuthDict

        if msg.author_id in UserAuthDict: #用in判断dict种是否存在这个键
            # 如果用户id已有，则不进行操作
            await msg.reply(f'您今日已经登陆过，无需重复操作\n如需重新登录，请先使用`/logout`命令退出当前登录')
            return

        # 不在其中才进行获取token的操作（耗时)
        res_auth = await authflow(user, passwd)
        res_gameid=await fetch_user_gameID(res_auth) # 获取用户玩家id
        UserAuthDict[msg.author_id] = {'access_token':res_auth.access_token,'entitlements_token':res_auth.entitlements_token,'auth_user_id':res_auth.user_id,'GameName':res_gameid[0]['GameName'],'TagLine':res_gameid[0]['TagLine']}
        #dict[键] = 值
        cm=CardMessage()
        c=Card(Module.Header("登陆成功！"),
                Module.Divider(),
                Module.Section(Element.Text("在明日的`03:00`之前，您可以使用和valorant对接的功能\n在`03:00`之后，您需要重新登录\n",Types.Text.KMD)),
                Module.Divider(),
                Module.Section("登陆游戏、多次使用查询命令等操作会使token失效\n您需要logout之后再login以重新登录您的账户")
                )
        cm.append(c)
        await msg.reply(cm)
        # 修改/新增都需要写入文件
        with open("./log/UserAuth.json", 'w', encoding='utf-8') as fw2:
            json.dump(UserAuthDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(f"【报错】  {result}\n\n您可能需要重新执行`/login`操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

# 退出登录
@bot.command(name='logout')
async def logout_authtoekn(msg:Message,*arg):
    logging(msg)
    if arg!=():
        await msg.reply(f"您给予了多余的参数！`{arg}`")
        return

    global UserAuthDict
    if msg.author_id not in UserAuthDict: #使用not in判断是否不存在
        await msg.reply(f"你还没有登陆呢！")
        return
    #如果id存在， 删除id
    print(f"Logout: {msg.author_id}")
    del UserAuthDict[msg.author_id]
    await msg.reply(f"已成功取消登录")

    #最后重新执行写入
    with open("./log/UserAuth.json",'w',encoding='utf-8') as fw1:
        json.dump(UserAuthDict,fw1,indent=2,sort_keys=True, ensure_ascii=False)
    fw1.close()


# 定时任务，每天凌晨3点清空token保存
@bot.task.add_cron(hour=3, minute=0)
async def clear_authtoken():
    global UserAuthDict
    UserAuthDict= {}  #置空
    # 写入文件
    with open("./log/UserAuth.json", 'w', encoding='utf-8') as fw2:
        json.dump(UserAuthDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
    print(f"[{GetTime()}] task_clear_authtoken")

# 定时任务，每3天获取一次皮肤（避免因为关闭bot导致时间不够，没法更新）
@bot.task.add_interval(days=3)
async def update_skins():
    global ValSkinList
    skins=await fetch_skins_all()
    ValSkinList=skins
    # 写入文件
    with open("./config/ValSkin.json", 'w', encoding='utf-8') as fw2:
        json.dump(ValSkinList, fw2, indent=2, sort_keys=True, ensure_ascii=False)
    print(f"[{GetTime()}] task_update_skins")

# 获取每日商店的命令
@bot.command(name='shop',aliases=['SHOP'])
async def get_daily_shop(msg: Message,*arg):
    logging(msg)
    if arg !=():
        await msg.reply(f"`/shop`命令不需要参数。您是否想`/login`？")
        return

    try:
        flag_au = 0
        if msg.author_id in UserAuthDict:
            # 如果用户id已有，则不需要再次获取token
            flag_au = 1
            userdict=UserAuthDict[msg.author_id]
            resp = await fetch_daily_shop(userdict)
            if "SkinsPanelLayout" not in resp:#这个键值不存在代表没有正常返回结果
                await msg.reply(f"访问商店失败！请尝试重新登录\n```\n{resp}\n```")
                return
            
            list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]
            timeout = resp["SkinsPanelLayout"][
                "SingleItemOffersRemainingDurationInSeconds"]
            timeout = time.strftime("%H:%M:%S",time.gmtime(timeout))  #将秒数转为标准时间
            x = 0
            y = 0
            bg = copy.deepcopy(bg_main)
            for skinuuid in list_shop:
                url = f"https://valorant-api.com/v1/weapons/skinlevels/{skinuuid}"
                headers = {'Connection': 'close'}
                params = {"language": "zh-TW"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers,
                                        params=params) as response:
                        res_item = json.loads(await response.text())
                        #print(res_item)
                res_price=await fetch_item_price(userdict,skinuuid)
                price=res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
                for it in ValSkinList['data']:
                    if it['levels'][0]['uuid'] == skinuuid:
                        res_iters = await fetch_item_iters(it['contentTierUuid'])
                        break
                #print(price,' ',res_iters['data']['displayName'])
                img = sm_comp(res_item["data"]["displayIcon"],res_item["data"]["displayName"],price,res_iters['data']['displayIcon'])
                bg = bg_comp(bg, img, x, y)

                if x == 0:
                    x += standard_length_sm
                elif x == standard_length_sm:
                    x = 0
                    y += standard_length_sm

            #bg.save(f"test.png")  #保存到本地
            imgByteArr = io.BytesIO()
            bg.save(imgByteArr, format='PNG')
            imgByte = imgByteArr.getvalue()
            dailyshop_img_src = await bot.client.create_asset(imgByte)

            cm = CardMessage()
            c = Card(Module.Header(f"玩家 {userdict['GameName']}#{userdict['TagLine']} 的每日商店！"),
                    Module.Context(f"失效时间剩余：{timeout}"),
                    Module.Container(Element.Image(src=dailyshop_img_src)))
            cm.append(c)
            await msg.reply(cm)

        if flag_au != 1:
            await msg.reply(f"您今日尚未登陆！请私聊使用`/login`命令进行登录操作\n```\n/login 账户 密码\n```")
            return

    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(f"【报错】  {result}\n\n您可能需要重新执行`/login`操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 获取vp和r点剩余的命令
@bot.command(name='point',aliases=['POINT'])
async def get_user_vp(msg: Message,*arg):
    logging(msg)
    if arg !=():
        await msg.reply(f"`/point`命令不需要参数。您是否想`/login`？")
        return

    try:
        flag_au = 0
        if msg.author_id in UserAuthDict:
            # 如果用户id已有，则不需要再次获取token
            flag_au = 1
            userdict=UserAuthDict[msg.author_id]
            resp = await fetch_valorant_point(userdict)
            vp = resp["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]#vp
            rp = resp["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]#R点

            cm = CardMessage()
            c = Card(Module.Header(f"玩家 {userdict['GameName']}#{userdict['TagLine']} 的点数剩余"),
                    Module.Divider(),
                    Module.Section(Element.Text(f"(emj)r点(emj)[3986996654014459/X3cT7QzNsu03k03k]  {rp}"+"    "+f"(emj)vp(emj)[3986996654014459/qGVLdavCfo03k03k]  {vp}\n",Types.Text.KMD)))
            cm.append(c)
            await msg.reply(cm)

        if flag_au != 1:
            await msg.reply(f"您今日尚未登陆！请私聊使用`/login`命令进行登录操作\n```\n/login 账户 密码\n```")
            return
    
    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(f"【报错】  {result}\n\n您可能需要重新执行`/login`操作",Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)




#bot.run()是机器人的起跑线
bot.run()
