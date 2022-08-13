# encoding: utf-8:
import json
import random
import time
import datetime
import aiohttp
# import requests

from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event,Client,PublicChannel,PublicMessage
from khl.card import CardMessage, Card, Module, Element, Types
from khl.command import Rule



with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])

Botoken=config['token']
kook="https://www.kookapp.cn"
headers={f'Authorization': f"Bot {Botoken}"}

# 设置全局变量：机器人开发者id
master_id = '1961572535'


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
    now_time = GetTime()
    print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")


@bot.command(name='hello')
async def world(msg: Message):
    logging(msg)
    await msg.reply('你好呀~')

# help命令
@bot.command(name='Ahri',aliases=['阿狸'])
async def Ahri(msg: Message):
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
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json错误是因为消息无法成功创建\n"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

#################################################################################################
#################################################################################################

# 倒计时函数，单位为秒，默认60秒
@bot.command()
async def countdown(msg: Message,time: int = 60):
    logging(msg)
    cm = CardMessage()
    c1 = Card(Module.Header('本狸帮你按下秒表喽~'), color=(198, 65, 55)) # color=(90,59,215) is another available form
    c1.append(Module.Divider())
    c1.append(Module.Countdown(datetime.now() + timedelta( seconds=time), mode=Types.CountdownMode.SECOND))
    cm.append(c1)

    await msg.reply(cm)

# 掷骰子
# invoke this via saying `!roll 1 100` in channel,or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int=1, t_max: int=100, n: int = 1):
    logging(msg)
    result = [random.randint(t_min, t_max) for i in range(n)]
    await msg.reply(f'掷出来啦: {result}')


# # 正则表达式（实测无效）
# @bot.command(regex = r'(.+)\\(met\\)ID\\(met\\)')

################################以下是给用户上色功能的内容########################################

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
        with open("./config/color_emoji.txt", 'r',encoding='utf-8') as fr1:
            lines=fr1.readlines()   
            for line in lines:
                v = line.strip().split(':')
                if emoji == v[0]:
                    flag=1 #确认用户回复的emoji合法 
                    ret = save_userid_color(event.body['user_id'],event.body["emoji"]['id'])# 判断用户之前是否已经获取过角色
                    if ret ==1: #已经获取过角色
                        await b.send(channel,f'你已经设置过你的ID颜色啦！修改要去找管理员哦~',temp_target_id=event.body['user_id'])
                        fr1.close()
                        return
                    else:
                        role=int(v[1])
                        await g.grant_role(s,role)
                        await b.send(channel, f'阿狸已经给你上了 {emoji} 对应的颜色啦~',temp_target_id=event.body['user_id'])
        fr1.close()
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
    with open("./config/color_emoji.txt", 'r',encoding='utf-8') as fr1:
        lines = fr1.readlines()   
        for line in lines:
            v = line.strip().split(':')
            await setMSG.add_reaction(v[0])
    fr1.close()
    

#########################################感谢助力者###############################################

# 检查文件中是否有这个助力者的id
def check_sponsor(it:dict):
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
    #在api链接重需要设置服务器id和助力者角色的id
    api = "https://www.kaiheila.cn/api/v3/guild/user-list?guild_id=3566823018281801&role_id=1454428"
    #headers={f'Authorization': f"Bot {config['token']}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(api, headers=headers) as response:
            #json_dict=json.loads(await response.text())
            json_dict = await response.json()

    for its in json_dict['data']['items']:
        #print(f"{its['id']}:{its['nickname']}")
        if check_sponsor(its) == 0:
            channel = await bot.fetch_public_channel("8342620158040885") #发送感谢信息的文字频道
            await bot.send(channel,f"(met){its['id']}(met) 感谢{its['nickname']}对本服务器的助力")
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
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
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

from val import kda123,skin123,lead123,saveid123,saveid1,saveid2,myid123,val123,dx123
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
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 存储id的help命令 
@bot.command(name='saveid1')
async def saveid_1(msg: Message):
    logging(msg)
    await saveid1(msg)

# 已保存id总数
@bot.command(name='saveid2')
async def saveid_2(msg: Message):
    logging(msg)
    try:
        await saveid2(msg)
    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json错误是因为消息无法成功创建\n"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

# 实现读取用户游戏ID并返回
@bot.command(name="myid",aliases=['MYID']) # 这里的aliases是别名
async def myid(msg: Message):
    logging(msg)
    try:
        await myid123(msg)

    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Context(f"提示:出现json错误是因为消息无法成功创建\n"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

# str转int
from functools import reduce
def str2int(s):
     return reduce(lambda x,y:x*10+y, map(lambda s:{'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}[s], s))

# 查询游戏错误码
@bot.command(name='val',aliases=['van'])
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



#bot.run()是机器人的起跑线
bot.run()
