# encoding: utf-8:
import json
import os
import random
import time
import traceback
from datetime import datetime, timedelta
from typing import Union

import aiohttp
import requests
from khl import (Bot, Client, Event, EventTypes, Message, PrivateMessage, PublicChannel, PublicMessage, requester)
from khl.card import Card, CardMessage, Element, Module, Types
from khl.command import Rule

from upd_msg import icon_cm, upd_card
from endpoints import (status_active_game, status_active_music, status_delete, weather,caiyun_translate,youdao_translate,is_CN)

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])
# 只用来上传图片的bot
bot_upimg = Bot(token=config['img_upload_token'])

Botoken = config['token']
kook = "https://www.kookapp.cn"
headers = {f'Authorization': f"Bot {Botoken}"}

# 设置全局变量：机器人开发者id/报错频道
master_id = '1961572535'
Debug_ch = '6248953582412867'

#在bot一开机的时候就获取log频道作为全局变量
debug_ch = None
cm_send_test = None


# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api = "http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid': 'a87ebe9c-1319-4394-9704-0ad2c70e2567'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)


##########################################################################################
##########################################################################################

#将获取当前时间封装成函数方便使用
def GetTime():  
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

#记录开机时间
start_time = GetTime()

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    if isinstance(msg, PrivateMessage):
        print(
            f"[{now_time}] PrivateMessage - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}"
        )
    else:
        print(
            f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}"
        )


@bot.command(name='hello')
async def world(msg: Message):
    logging(msg)
    await msg.reply('你好呀~')


# help命令
@bot.command(name='Ahri', aliases=['ahri'])
async def Ahri(msg: Message, *arg):
    logging(msg)
    try:
        # msg 触发指令为 `/Ahri`,因为help指令和其他机器人冲突
        cm = CardMessage()
        c3 = Card(
            Module.Header('你可以用下面这些指令呼叫本狸哦！'),
            Module.Context(
                Element.Text(f"开源代码见[Github](https://github.com/Aewait/Valorant-Kook-Bot)，开机于 [{start_time}]",
                             Types.Text.KMD)))
        c3.append(Module.Section('「/hello」来和本狸打个招呼吧！\n「/Ahri」 帮助指令\n'))
        c3.append(Module.Divider())
        c3.append(Module.Header('上号，瓦一把！'))
        text  = "「/val 错误码」 游戏错误码的解决方法，0为已包含的val报错码信息\n"
        text += "「/dx」 关于DirectX Runtime报错的解决方案\n"
        text += "「/saveid 游戏id」 保存(修改)您的游戏id\n"
        text += "「/myid」 让阿狸说出您的游戏id\n"
        text += "「`/vhelp`」瓦洛兰特游戏查询相关功能的帮助\n"
        text += "[如果你觉得这些功能还不错，可以支持一下阿狸吗?](https://afdian.net/a/128ahri?tab=shop)"
        c3.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        c3.append(Module.Divider())
        c3.append(Module.Header('和阿狸玩小游戏吧~ '))
        text  = "「/roll 1 100」掷骰子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个骰子\n"
        text += "「/countdown 秒数」倒计时，默认60秒\n"
        text += "「/TL 内容」翻译内容，支持多语译中和中译英\n"
        text += "「/TLON」 在本频道打开实时翻译\n"
        text += "「/TLOFF」在本频道关闭实时翻译\n"
        text += "「/we 城市」查询城市未来3天的天气情况\n"
        text += "「更多…」还有一些隐藏指令哦~\n"
        c3.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        c3.append(Module.Divider())
        c3.append(
            Module.Section(' 游戏打累了？想来本狸的家坐坐吗~', Element.Button('让我康康', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm.append(c3)

        await msg.reply(cm)

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] Ahri - {result}"
        print(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# help命令(瓦洛兰特相关)
@bot.command(name='Vhelp', aliases=['vhelp'])
async def Vhelp(msg: Message, *arg):
    logging(msg)
    try:
        # msg 触发指令为 `/Ahri`,因为help指令和其他机器人冲突
        cm = CardMessage()
        c3 = Card(
            Module.Header('目前阿狸支持查询的valorant信息如下'),
            Module.Context(
                Element.Text("开源代码见[Github](https://github.com/Aewait/Valorant-Kook-Bot)，更多查询功能上线中...",
                             Types.Text.KMD)))
        text = "使用前，请确认您知晓相关功能可能有风险：\n"
        text += "1.阿狸的后台不会做任何`打印/保存`您的游戏账户密码的操作，若在使用相关功能后被盗号，阿狸可不承担任何责任;\n"
        text += "2.目前查询功能稳定性未知，可能有`封号`风险，建议使用小号测试;\n若担心相关风险，请不要使用如下功能\n"
        c3.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        c3.append(Module.Divider())
        help_1  = "「/bundle 皮肤名」 查询皮肤系列包含什么枪械\n"
        help_1 += "「/lead」 显示出当前游戏的排行榜。可提供参数1前多少位，参数2过滤胜场。如`/lead 20 30`代表排行榜前20位胜场超过30的玩家\n"
        help_1 += "「/login 账户 密码」请`私聊`使用，登录您的riot账户\n"
        help_1 += "「/shop」 查询您的每日商店\n"
        help_1 += "「/point」「/uinfo」查询当前装备的卡面/称号/剩余vp和r点\n"
        help_1 += "「/notify-a 皮肤名」查询皮肤，并选择指定皮肤加入每日商店提醒\n"
        help_1 += "「/notify-l 」查看当前设置了提醒的皮肤\n"
        help_1 += "「/notify-d 皮肤uuid」删除不需要提醒的皮肤\n"
        help_1 += "「/logout」取消登录\n"
        c3.append(Module.Section(Element.Text(help_1, Types.Text.KMD)))
        c3.append(Module.Divider())
        c3.append(Module.Header("以下进阶功能，发电支持阿狸即可解锁哦~"))
        help_2  = "「/vip-u 激活码」兑换阿狸的vip\n"
        help_2 += "「/vip-c」 查看vip的剩余时间\n"
        help_2 += "「全新商店返回值」vip用户将获取到16-9的超帅商店返回值\n"
        help_2 += "「/vip-shop」查看已保存的商店查询diy背景图\n"
        help_2 += "「/vip-shop 图片url」添加商店查询diy背景图\n"
        help_2 += "「/vip-shop-s 图片编号」切换商店查询的背景图\n"
        help_2 += "「保存登录信息」vip用户登陆后，阿狸会自动保存您的cookie。在阿狸维护重启的时候，您的登录信息不会丢失\n"
        help_2 += "「图片形式的商店提醒」vip用户将在早8点获取当日的每日商店。阿狸会对这张图片进行缓存，同天使用`/shop`命令的时候，只需要2s即可获取结果，3倍于普通用户的响应速度！\n\n"
        help_2 += "1.目前商店查询背景图diy支持16-9(横屏)的图片，图片url获取：PC端将图片上传到kook→点击图片→底部`...`处复制图片链接→使用`/vip-shop`命令设置背景 [教程图](https://s1.ax1x.com/2022/09/12/vXD1Nq.jpg)\n"
        help_2 +="2.请不要设置违规图片(擦边也不行)！若因为您上传违禁图片后导致阿狸被封，您将被剥夺vip并永久禁止兑换vip\n"
        c3.append(Module.Section(Element.Text(help_2, Types.Text.KMD)))
        c3.append(
            Module.Context(
                Element.Text("[如果你觉得这些功能还不错，可以发电支持一下阿狸吗?](https://afdian.net/a/128ahri?tab=shop)", Types.Text.KMD)))
        c3.append(Module.Divider())
        c3.append(Module.Section('若有任何问题，欢迎加入帮助频道', Element.Button('来狸', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm.append(c3)
        await msg.reply(cm)

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] vhelp - {result}"
        print(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


#################################################################################################
#################################################################################################

# 倒计时函数，单位为秒，默认60秒
@bot.command()
async def countdown(msg: Message, time: int = 60):
    logging(msg)
    try:
        cm = CardMessage()
        c1 = Card(Module.Header('本狸帮你按下秒表喽~'), color=(198, 65, 55))  # color=(90,59,215) is another available form
        c1.append(Module.Divider())
        c1.append(Module.Countdown(datetime.now() + timedelta(seconds=time), mode=Types.CountdownMode.SECOND))
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] countdown\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        #发送错误信息到指定频道
        
        await bot.client.send(debug_ch, err_str)


# 掷骰子 saying `!roll 1 100` in channel,or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int = 1, t_max: int = 100, n: int = 1):
    logging(msg)
    if t_min >= t_max:#判断范围
        await msg.reply(f'范围错误，必须提供两个参数，由小到大！\nmin:`{t_min}` max:`{t_max}`')
        return
    try:
        result = [random.randint(t_min, t_max) for i in range(n)]
        await msg.reply(f'掷出来啦: {result}')
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] roll\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        #发送错误信息到指定频道
        
        await bot.client.send(debug_ch, err_str)


################################以下是给用户上色功能的内容########################################

# 预加载文件
with open("./log/color_idsave.json", 'r', encoding='utf-8') as frcl:
    ColorIdDict = json.load(frcl)

with open("./config/color_emoji.txt", 'r', encoding='utf-8') as fremoji:
    EmojiLines = fremoji.readlines()


# 用于记录使用表情回应获取ID颜色的用户
def save_userid_color(userid: str, emoji: str):
    global ColorIdDict
    flag = 0
    # 需要先保证原有txt里面没有保存该用户的id，才进行追加
    if userid in ColorIdDict.keys():
        flag = 1  #因为用户已经回复过表情，将flag置为1
        return flag
    #原有txt内没有该用户信息，进行追加操作
    ColorIdDict[userid] = emoji
    with open("./log/color_idsave.json", 'w', encoding='utf-8') as fw2:
        json.dump(ColorIdDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

    return flag


# 设置自动上色event的服务器id和消息id
Guild_ID = '3566823018281801'
Msg_ID = '6fec1aeb-9d5c-4642-aa95-862e3db8aa61'


# # 在不修改代码的前提下设置上色功能的服务器和监听消息
@bot.command()
async def Color_Set_GM(msg: Message, Card_Msg_id: str):
    logging(msg)
    if msg.author_id == master_id:
        global Guild_ID, Msg_ID  #需要声明全局变量
        Guild_ID = msg.ctx.guild.id
        Msg_ID = Card_Msg_id
        await msg.reply(f'颜色监听服务器更新为 {Guild_ID}\n监听消息更新为 {Msg_ID}\n')


# 判断消息的emoji回应，并给予不同角色
@bot.on_event(EventTypes.ADDED_REACTION)
async def update_reminder(b: Bot, event: Event):
    g = await bot.client.fetch_guild(Guild_ID)  # 填入服务器id
    #将msg_id和event.body msg_id进行对比，确认是我们要的那一条消息的表情回应
    if event.body['msg_id'] == Msg_ID:
        now_time = GetTime()  #记录时间
        print(f"[{now_time}] React:{event.body}")  # 这里的打印eventbody的完整内容，包含emoji_id

        channel = await bot.client.fetch_public_channel(event.body['channel_id'])  #获取事件频道
        s = await bot.client.fetch_user(event.body['user_id'])  #通过event获取用户id(对象)
        # 判断用户回复的emoji是否合法
        emoji = event.body["emoji"]['id']
        flag = 0
        for line in EmojiLines:
            v = line.strip().split(':')
            if emoji == v[0]:
                flag = 1  #确认用户回复的emoji合法
                ret = save_userid_color(event.body['user_id'], event.body["emoji"]['id'])  # 判断用户之前是否已经获取过角色
                if ret == 1:  #已经获取过角色
                    await b.client.send(channel, f'你已经设置过你的ID颜色啦！修改要去找管理员哦~', temp_target_id=event.body['user_id'])
                    return
                else:
                    role = int(v[1])
                    await g.grant_role(s, role)
                    await b.client.send(channel, f'阿狸已经给你上了 {emoji} 对应的颜色啦~', temp_target_id=event.body['user_id'])

        if flag == 0:  #回复的表情不合法
            await b.client.send(channel, f'你回应的表情不在列表中哦~再试一次吧！', temp_target_id=event.body['user_id'])


# 给用户上色（在发出消息后，机器人自动添加回应）
@bot.command()
async def Color_Set(msg: Message):
    logging(msg)
    if msg.author_id != master_id:
        await msg.reply("您没有权限执行这条命令！")
        return
    cm = CardMessage()
    c1 = Card(Module.Header('在下面添加回应，来设置你的id颜色吧！'), Module.Context('五颜六色等待上线...'))
    c1.append(Module.Divider())
    c1.append(Module.Section('「:pig:」粉色  「:heart:」红色\n「:black_heart:」黑色  「:yellow_heart:」黄色\n'))
    c1.append(Module.Section('「:blue_heart:」蓝色  「:purple_heart:」紫色\n「:green_heart:」绿色  「:+1:」默认\n'))
    cm.append(c1)
    sent = await msg.ctx.channel.send(cm)  #接受send的返回值
    # 自己new一个msg对象
    setMSG = PublicMessage(msg_id=sent['msg_id'],
                           _gate_=msg.gate,
                           extra={
                               'guild_id': msg.ctx.guild.id,
                               'channel_name': msg.ctx.channel,
                               'author': {
                                   'id': bot.me.id
                               }
                           })
    # extra部分留空也行
    # 让bot给卡片消息添加对应emoji回应
    for line in EmojiLines:
        v = line.strip().split(':')
        await setMSG.add_reaction(v[0])


#########################################感谢助力者###############################################

# 预加载文件
with open("./log/sponsor_roles.json", 'r', encoding='utf-8') as frsp:
    SponsorDict = json.load(frsp)


# 检查文件中是否有这个助力者的id
def check_sponsor(it: dict):
    global SponsorDict
    flag = 0
    # 需要先保证原有txt里面没有保存该用户的id，才进行追加
    if it['id'] in SponsorDict.keys():
        flag = 1
        return flag

    #原有txt内没有该用户信息，进行追加操作
    SponsorDict[it['id']] = it['nickname']
    with open("./log/sponsor_roles.json", 'w', encoding='utf-8') as fw2:
        json.dump(SponsorDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

    return flag


# 感谢助力者（每天19点进行检查）
@bot.task.add_cron(hour=19, minute=0, timezone="Asia/Shanghai")
async def thanks_sponser():
    print("[BOT.TASK] thanks_sponser start!")
    #在api链接重需要设置服务器id和助力者角色的id，目前这个功能只对KOOK最大valorant社区生效
    api = "https://www.kaiheila.cn/api/v3/guild/user-list?guild_id=3566823018281801&role_id=1454428"
    async with aiohttp.ClientSession() as session:
        async with session.post(api, headers=headers) as response:
            json_dict = json.loads(await response.text())

    #长度相同无需更新
    sz = len(SponsorDict)
    if json_dict['data']['meta']['total'] == sz:
        print(f"[BOT.TASK] No new sponser, same_len [{sz}]")
        return

    for its in json_dict['data']['items']:
        if check_sponsor(its) == 0:
            channel = await bot.client.fetch_public_channel("8342620158040885")  #发送感谢信息的文字频道
            await bot.client.send(channel, f"感谢 (met){its['id']}(met) 对本服务器的助力")
            print(f"[%s] 感谢{its['nickname']}对本服务器的助力" % GetTime())
    print("[BOT.TASK] thanks_sponser finished!")


######################################## Translate ################################################

# 单独处理met和rol消息，不翻译这部分内容
def deleteByStartAndEnd(s, start, end):
    # 找出两个字符串在原始字符串中的位置
    # 开始位置是：开始始字符串的最左边第一个位置；
    # 结束位置是：结束字符串的最右边的第一个位置
    while s.find(start) != -1:
        x1 = s.find(start)
        x2 = s.find(end, x1 + 5) + len(end)  # s.index()函数算出来的是字符串的最左边的第一个位置，所以需要加上长度找到末尾
        # 找出两个字符串之间的内容
        x3 = s[x1:x2]
        # 将内容替换为空字符串s
        s = s.replace(x3, "")

    print(f'Handel{start}: {s}')
    return s


# 调用翻译,有道和彩云两种引擎（有道寄了就用彩云）
async def translate(msg: Message, *arg):
    word = " ".join(arg)
    ret = word
    if '(met)' in word:
        ret = deleteByStartAndEnd(word, '(met)', '(met)')
    elif '(rol)' in word:
        ret = deleteByStartAndEnd(word, '(rol)', '(rol)')
    #重新赋值
    word = ret
    try:
        cm = CardMessage()
        c1 = Card(Module.Section(Element.Text(f"**翻译结果(Result):** {youdao_translate(word)}", Types.Text.KMD)),
                  Module.Context('来自: 有道翻译'))
        cm.append(c1)
        #await msg.ctx.channel.send(cm)
        await msg.reply(cm)
    except:
        cm = CardMessage()
        if is_CN(word):
            c1 = Card(
                Module.Section(
                    Element.Text(f"**翻译结果(Result):** {await caiyun_translate(word,'auto2en')}", Types.Text.KMD)),
                Module.Context('来自: 彩云小译，中译英'))
        else:
            c1 = Card(
                Module.Section(
                    Element.Text(f"**翻译结果(Result):** {await caiyun_translate(word,'auto2zh')}", Types.Text.KMD)),
                Module.Context('来自: 彩云小译，英译中'))

        cm.append(c1)
        await msg.reply(cm)


# 普通翻译指令
@bot.command(name='TL', aliases=['tl'])
async def translate1(msg: Message, *arg):
    logging(msg)
    await translate(msg, ' '.join(arg))


# 实时翻译栏位
ListTL = ['0', '0', '0', '0','0','0']


# 查看目前已经占用的容量
def checkTL():
    sum = 0
    for i in ListTL:
        if i != '0':
            sum += 1
    return sum


#查看当前占用的实时翻译栏位
@bot.command()
async def CheckTL(msg: Message):
    logging(msg)
    global ListTL
    await msg.reply(f"目前已使用栏位:{checkTL()}/{len(ListTL)}")


# 关闭所有栏位的实时翻译（避免有些人用完不关）
@bot.command()
async def ShutdownTL(msg: Message):
    logging(msg)
    if msg.author.id != master_id:
        return  #这条命令只有bot的作者可以调用
    global ListTL
    if checkTL() == 0:
        await msg.reply(f"实时翻译栏位为空: {checkTL()}/{len(ListTL)}")
        return
    i = 0
    while i < len(ListTL):
        if (ListTL[i]) != '0':  #不能对0的频道进行操作
            channel = await bot.client.fetch_public_channel(ListTL[i])
            await bot.client.send(channel, "不好意思，阿狸的主人已经清空了实时翻译的栏位！")
            ListTL[i] = '0'
        i += 1
    await msg.reply(f"实时翻译栏位已清空！目前为: {checkTL()}/{len(ListTL)}")


# 通过频道id判断是否实时翻译本频道内容
@bot.command(regex=r'(.+)')
async def TL_Realtime(msg: Message, *arg):
    word = " ".join(arg)
    # 不翻译关闭实时翻译的指令
    if word == "/TLOFF" or word == "/tloff" or word == '/tlon' or word == '/TLON':
        return
    global ListTL
    if msg.ctx.channel.id in ListTL:
        logging(msg)
        await translate(msg, ' '.join(arg))
        return


# 开启实时翻译功能
@bot.command(name='TLON', aliases=['tlon'])
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
    i = 0
    while i < len(ListTL):
        if ListTL[i] == '0':
            ListTL[i] = msg.ctx.channel.id
            break
        i += 1
    ret = checkTL()
    await msg.reply(f"Real-Time Translation ON\n阿狸现在会实时翻译本频道的对话啦！\n目前栏位: {ret}/{len(ListTL)}，使用`/TLOFF`可关闭实时翻译哦~")


# 关闭实时翻译功能
@bot.command(name='TLOFF', aliases=['tloff'])
async def TLOFF(msg: Message):
    logging(msg)
    global ListTL
    i = 0
    while i < len(ListTL):
        if ListTL[i] == msg.ctx.channel.id:
            ListTL[i] = '0'
            await msg.reply(f"Real-Time Translation OFF！目前栏位: {checkTL()}/{len(ListTL)}")
            return
        i += 1
    await msg.reply(f"本频道并没有开启实时翻译功能！目前栏位: {checkTL()}/{len(ListTL)}")


######################################## Other ################################################

# 返回历史上的今天
@bot.command(name='hs')
async def History(msg: Message):
    logging(msg)
    #await history(msg)
    await msg.reply(f"抱歉，`hs` 功能已被取消！")


# 返回天气
@bot.command(name='we')
async def Weather(msg: Message, city: str = "err"):
    logging(msg)
    if city == "err":
        await msg.reply(f"函数参数错误，城市: `{city}`\n")
        return

    try:
        await weather(msg, city)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] we\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


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
    await msg.reply(
        '本狸才不喜欢`又硬又细`的人呢~\n[https://s1.ax1x.com/2022/06/24/jFGjHA.png](https://s1.ax1x.com/2022/06/24/jFGjHA.png)')


###########################################################################################
####################################以下是游戏相关代码区#####################################
###########################################################################################

from val import (authflow, dx123, fetch_buddies_uuid, fetch_bundle_weapen_byname, fetch_bundles_all,
                 fetch_contract_uuid, fetch_daily_shop, fetch_item_iters, fetch_item_price_all, fetch_item_price_uuid,
                 fetch_player_contract, fetch_player_loadout, fetch_playercard_uuid, fetch_skinlevel_uuid,
                 fetch_skins_all, fetch_spary_uuid, fetch_title_uuid, fetch_user_gameID, fetch_valorant_point, kda123,
                 lead123, myid123, saveid123, saveid_1, saveid_2, skin123, val123)


# 开始打游戏
@bot.command()
async def gaming(msg: Message, game: int = 1):
    logging(msg)
    #await bot.client.update_playing_game(3,1)# 英雄联盟
    if game == 1:
        ret = await status_active_game(453027)  # 瓦洛兰特
        await msg.reply(f"{ret['message']}，阿狸上号valorant啦！")
    elif game == 2:
        ret = await status_active_game(3)  # 英雄联盟
        await msg.reply(f"{ret['message']}，阿狸上号LOL啦！")


# 开始听歌
@bot.command()
async def singing(msg: Message, music: str = "err", singer: str = "err"):
    logging(msg)
    if music == "err" or singer == "err":
        await msg.reply(f"函数参数错误，music: `{music}` singer: `{singer}`")
        return

    ret = await status_active_music(music, singer)
    await msg.reply(f"{ret['message']}，阿狸开始听歌啦！")


# 停止打游戏1/听歌2
@bot.command(name='sleeping')
async def sleeping(msg: Message, d: int = 1):
    logging(msg)
    ret = await status_delete(d)
    if d == 1:
        await msg.reply(f"{ret['message']}，阿狸下号休息啦!")
    elif d == 2:
        await msg.reply(f"{ret['message']}，阿狸摘下了耳机~")
    #await bot.client.stop_playing_game()


# 中二病
@bot.command(name='kda')
async def kda(msg: Message):
    logging(msg)
    await kda123(msg)


# 查询排行榜
@bot.command()
async def lead(msg: Message, sz: int = 15, num: int = 10):
    logging(msg)
    await lead123(msg, sz, num)


# 存储用户游戏id
@bot.command()
async def saveid(msg: Message, *args):
    logging(msg)
    if args == ():
        await msg.reply(f"您没有提供您的游戏id：`{args}`")
        return
    try:
        game_id = " ".join(args)  #避免用户需要输入双引号
        await saveid123(msg, game_id)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] saveid\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


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
        err_str = f"ERR! [{GetTime()}] saveid2 = {result}"
        print(err_str)
        await msg.reply(err_str)


# 实现读取用户游戏ID并返回
@bot.command(name="myid", aliases=['MYID'])  # 这里的aliases是别名
async def myid(msg: Message, *args):
    logging(msg)
    if args != ():
        await msg.reply(f"`/myid`命令不需要参数！")
        return

    try:
        await myid123(msg)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] myid\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


# str转int
from functools import reduce


def str2int(s):
    return reduce(lambda x, y: x * 10 + y,
                  map(lambda s: {
                      '0': 0,
                      '1': 1,
                      '2': 2,
                      '3': 3,
                      '4': 4,
                      '5': 5,
                      '6': 6,
                      '7': 7,
                      '8': 8,
                      '9': 9
                  }[s], s))


# 查询游戏错误码
@bot.command(name='val', aliases=['van', 'VAN', 'VAL'])
async def val_err(msg: Message, numS: str = "err"):
    logging(msg)
    if numS == "err":
        await msg.reply(f"函数参数错误，请提供正确范围的错误码")
        return
    try:
        num = str2int(numS)
        await val123(msg, num)
    except Exception as result:
        await msg.reply(f"您输入的错误码格式不正确！\n请提供正确范围的`数字`,而非`{numS}`")


#关于dx报错的解决方法
@bot.command(name='DX', aliases=['dx'])  # 新增别名dx
async def dx(msg: Message):
    logging(msg)
    await dx123(msg)


###########################################################################################
###########################################################################################

import asyncio
#多出来的import
import copy
import io  # 用于将 图片url 转换成可被打开的二进制
import threading

import zhconv  # 用于繁体转简体（因为部分字体不支持繁体
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError  # 用于合成图片
from riot_auth import RiotAuth, auth_exceptions

standard_length = 1000  #图片默认边长
# 用math.floor 是用来把float转成int 我也不晓得为啥要用 但是不用会报错（我以前不用也不会）
# 所有的数都  * standard_length / 1000 是为了当标准边长变动时这些参数会按照比例缩放
standard_length_sm = int(standard_length / 2)  # 组成四宫格小图的边长
stardard_blank_sm = 60 * standard_length / 1000  # 小图左边的留空
stardard_icon_resize_ratio = 0.59 * standard_length / 1000  # 枪的默认缩放
standard_icon_top_blank = int(180 * standard_length / 1000)  # 枪距离图片顶部的像素
standard_text_position = (int(124 * standard_length / 1000), int(317 * standard_length / 1000))  # 默认文字位置
standard_price_position = (int(280 * standard_length / 1000), int(120 * standard_length / 1000))  # 皮肤价格文字位置
standard_level_icon_reszie_ratio = 0.13 * standard_length / 1000  # 等级icon图标的缩放
standard_level_icon_position = (int(350 * standard_length / 1000), int(120 * standard_length / 1000))  # 等级icon图标的坐标


async def img_requestor(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as r:
            return await r.read()


font_color = '#ffffff'  # 文字颜色：白色

bg_main = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/m8o9eCuKHQ0rs0rs.png').content))  # 普通用户商店背景
bg_main_11 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/FjPcmVwDkf0rs0rs.png').content))  # vip用户背景框 1-1
bg_main_vip = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/lSj90Xr9yA0zk0k0.png').content))  # vip商店默认背景
bg_main_169 = Image.open(io.BytesIO(
    requests.get('https://img.kookapp.cn/assets/2022-09/rLxOSFB1cC0zk0k0.png').content))  # vip用户背景框 16-9


# 缩放图片，部分皮肤图片大小不正常
def resize(standard_x, img, standard_y=''):
    standard_y = standard_x if standard_y == '' else standard_y
    log_info = "[shop] "
    w, h = img.size
    log_info += f"原始图片大小:({w},{h}) - "
    ratio = w / h
    if ratio > standard_x / standard_y:
        sizeco = w / standard_x
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
    else:
        sizeco = h / standard_y
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
    log_info += f"缩放后大小:({w_s},{h_s})"
    print(log_info)
    img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
    return img


# 将图片修改到标准大小
def resize_vip(standard_x, standard_y, img):
    w, h = img.size
    log_info = "[resize_vip] "
    log_info += f"原始图片大小:({w},{h}) - "
    ratio = w / h
    if ratio <= 1.78:
        sizeco = w / standard_x
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
        log_info += f"缩放后大小:({w_s},{h_s})"
        blank = (h_s - standard_y) / 2
        img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
        img = img.crop((0, blank, w_s, h_s - blank))
    else:
        sizeco = h / standard_y
        log_info += f"缩放系数:{format(sizeco,'.3f')} - "
        w_s = int(w / sizeco)
        h_s = int(h / sizeco)
        log_info += f"缩放后大小:({w_s},{h_s})"
        blank = (w_s - standard_x) / 2
        img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
        img = img.crop((blank, 0, w_s - blank, h_s))
    return img


level_icon_temp = {}
weapon_icon_temp = {}
weapon_icon_temp_vip = {}


def sm_comp(icon, name, price, level_icon, skinuuid):
    bg = Image.new(mode='RGBA', size=(standard_length_sm, standard_length_sm))  # 新建一个画布
    # 处理武器图片
    start = time.perf_counter()  #开始计时

    if os.path.exists(f'./log/img_temp/weapon/{skinuuid}.png'):
        layer_icon = Image.open(f'./log/img_temp/weapon/{skinuuid}.png')  # 打开武器图片
    else:
        layer_icon = Image.open(io.BytesIO(requests.get(icon).content))  # 打开武器图片
        layer_icon.save(f'./log/img_temp/weapon/{skinuuid}.png', format='PNG')
    end = time.perf_counter()
    log_time = f"[GetWeapen] {format(end - start, '.4f')} "
    # w, h = layer_icon.size  # 读取武器图片长宽
    # new_w = int(w * stardard_icon_resize_ratio)  # 按比例缩放的长
    # new_h = int(h * stardard_icon_resize_ratio)  # 按比例缩放的宽
    stardard_icon_x = 300  #图像标准宽（要改大小就改这个
    layer_icon = resize(300, layer_icon)
    # layer_icon = layer_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # 按缩放比例后的长宽进行resize（resize就是将图像原长宽拉伸到新长宽） Image.Resampling.LANCZOS 是一种处理方式
    left_position = int((standard_length_sm - stardard_icon_x) / 2)
    # 用小图的宽度减去武器图片的宽度再除以二 得到武器图片x轴坐标  y轴坐标 是固定值 standard_icon_top_blank
    bg.paste(layer_icon, (left_position, standard_icon_top_blank), layer_icon)
    # bg.paste代表向bg粘贴一张图片
    # 第一个参数是图像layer_icon
    # 第二个参数(left_position, standard_icon_top_blank)就是刚刚算出来的 x,y 坐标 最后一个layer_icon是蒙版
    # 处理武器level的图片(存到本地dict里面方便调用)
    start = time.perf_counter()  #开始计时
    if level_icon not in level_icon_temp:
        LEVEL_Icon = Image.open(io.BytesIO(requests.get(level_icon).content))  # 打开武器图片
        level_icon_temp[level_icon] = LEVEL_Icon
    else:
        LEVEL_Icon = level_icon_temp[level_icon]
    end = time.perf_counter()
    log_time += f"- [GetIters] {format(end - start, '.4f')} "
    print(log_time)

    w, h = LEVEL_Icon.size  # 读取武器图片长宽
    new_w = int(w * standard_level_icon_reszie_ratio)  # 按比例缩放的长
    new_h = int(h * standard_level_icon_reszie_ratio)  # 按比例缩放的宽
    LEVEL_Icon = LEVEL_Icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    bg.paste(LEVEL_Icon, standard_level_icon_position, LEVEL_Icon)

    name = zhconv.convert(name, 'zh-cn')  # 将名字简体化
    name_list = name.split(' ')  # 将武器名字分割换行
    # print(name_list)
    if '' in name_list:  # 避免出现返回值后面带空格的情况，如'重力鈾能神經爆破者 制式手槍 '
        name_list.remove('')

    text = ""
    if len(name_list[0]) > 5:
        text = name_list[0] + '\n'  # 如果皮肤名很长就不用加空格
    else:
        text = ' '.join(name_list[0]) + '\n'  # 向皮肤名字添加空格增加字间距
    # interval = len(name_list[0])
    # print(len(name_list))
    if len(name_list) > 2:
        i = 1
        while i <= len(name_list) - 2:
            name_list[0] = name_list[0] + ' ' + name_list[i]
            # print(name_list[0])
            i += 1
        interval = len(name_list[0])
        name_list[1] = name_list[len(name_list) - 1]
        text = name_list[0] + '\n'
    if len(name_list) > 1:  # 有些刀皮肤只有一个元素
        text += '              '  # 添加固定长度的缩进，12个空格
        if len(name_list[1]) < 4:
            text += ' '.join(name_list[1])  # 插入第二行字符
        else:
            text += name_list[1]  # 单独处理制式手槍（不加空格）

    draw = ImageDraw.Draw(bg)  # 让bg这个图层能被写字
    # 第一个参数 standard_text_position 是固定参数坐标 ， 第二个是文字内容 ， 第三个是字体 ， 第四个是字体颜色
    draw.text(standard_text_position,
              text,
              font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 30),
              fill=font_color)
    text = f"{price}"  # 价格
    draw.text(standard_price_position,
              text,
              font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 30),
              fill=font_color)
    # bg.show() #测试用途，展示图片(linux貌似不可用)
    if not os.path.exists(f'./log/img_temp/comp/{skinuuid}.png'):
        bg.save(f'./log/img_temp/comp/{skinuuid}.png')
    global weapon_icon_temp #普通用户的抽屉
    if skinuuid not in weapon_icon_temp:
        weapon_icon_temp[skinuuid] = bg
    return bg


# 处理vip图片
def sm_comp_vip(icon, name, price, level_icon, skinuuid):
    bg = Image.new(mode='RGBA', size=(400, 240))  # 新建一个画布
    # 处理武器图片
    start = time.perf_counter()  #开始计时
    if os.path.exists(f'./log/img_temp/weapon/{skinuuid}.png'):
        layer_icon = Image.open(f'./log/img_temp/weapon/{skinuuid}.png')  # 打开武器图片
    else:
        layer_icon = Image.open(io.BytesIO(requests.get(icon).content))  # 打开武器图片
        layer_icon.save(f'./log/img_temp/weapon/{skinuuid}.png', format='PNG')
    end = time.perf_counter()
    log_time = f"[GetWeapen] {format(end - start, '.4f')} "
    layer_icon = resize(300, layer_icon, 130)
    # layer_icon = layer_icon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # 按缩放比例后的长宽进行resize（resize就是将图像原长宽拉伸到新长宽） Image.Resampling.LANCZOS 是一种处理方式
    # 用小图的宽度减去武器图片的宽度再除以二 得到武器图片x轴坐标  y轴坐标 是固定值 standard_icon_top_blank
    w, h = layer_icon.size
    x = 50 if w == 300 else int((350 - w) / 2)
    y = int((240 - h) / 2) if w == 300 else 30
    bg.paste(layer_icon, (x, y), layer_icon)
    # bg.paste代表向bg粘贴一张图片
    # 第一个参数是图像layer_icon
    # 第二个参数(left_position, standard_icon_top_blank)就是刚刚算出来的 x,y 坐标 最后一个layer_icon是蒙版
    # 处理武器level的图片(存到本地dict里面方便调用)
    start = time.perf_counter()  #开始计时
    if level_icon not in level_icon_temp:
        LEVEL_Icon = Image.open(io.BytesIO(requests.get(level_icon).content))  # 打开武器图片
        level_icon_temp[level_icon] = LEVEL_Icon
    else:
        LEVEL_Icon = level_icon_temp[level_icon]
    end = time.perf_counter()
    log_time += f"- [GetIters] {format(end - start, '.4f')} "
    print(log_time)
    LEVEL_Icon = LEVEL_Icon.resize((25, 25), Image.Resampling.LANCZOS)
    bg.paste(LEVEL_Icon, (368, 11), LEVEL_Icon)
    text = zhconv.convert(name, 'zh-cn')  # 将名字简体化
    draw = ImageDraw.Draw(bg)  # 让bg这个图层能被写字
    # 第一个参数 standard_text_position 是固定参数坐标 ， 第二个是文字内容 ， 第三个是字体 ， 第四个是字体颜色
    draw.text((15, 205), text, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 25), fill=font_color)
    text = f"{price}"  # 价格
    draw.text((320, 13), text, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    # bg.show() #测试用途，展示图片(linux貌似不可用)
    if not os.path.exists(f'./log/img_temp_vip/comp/{skinuuid}.png'):
        bg.save(f'./log/img_temp_vip/comp/{skinuuid}.png')
    global weapon_icon_temp_vip#vip用户的抽屉
    if skinuuid not in weapon_icon_temp_vip:
        weapon_icon_temp_vip[skinuuid] = bg
    return bg


def bg_comp(bg, img, x, y):
    position = (x, y)
    bg.paste(img, position, img)  #如sm—comp中一样，向bg粘贴img
    return bg


shop_img_temp = {}
shop_img_temp_vip = {}


def skin_uuid_to_comp(skinuuid, ran, is_vip: bool):
    res_item = fetch_skin_bylist(skinuuid)  # 从本地文件中查找
    res_price = fetch_item_price_bylist(skinuuid)  # 在本地文件中查找
    price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
    for it in ValSkinList['data']:
        if it['levels'][0]['uuid'] == skinuuid:
            res_iters = fetch_item_iters_bylist(it['contentTierUuid'])
            break
    if is_vip:
        img = sm_comp_vip(res_item["data"]['levels'][0]["displayIcon"], res_item["data"]["displayName"], price,
                          res_iters['data']['displayIcon'], skinuuid)
        global shop_img_temp_vip  #这里是把处理好的图片存到本地
        shop_img_temp_vip[ran].append(img)
    else:
        img = sm_comp(res_item["data"]['levels'][0]["displayIcon"], res_item["data"]["displayName"], price,
                      res_iters['data']['displayIcon'], skinuuid)
        global shop_img_temp  #这里是把处理好的图片存到本地
        shop_img_temp[ran].append(img)


#####################################################################################################

from check_vip import (VipUserDict, create_vip_uuid, fetch_vip_user, using_vip_uuid, vip_ck, vip_time_remain,
                       vip_time_remain_cm, vip_time_stamp)

# 加载文件中的uuid
with open("./log/VipUuid.json", 'r', encoding='utf-8') as frrk:
    VipUuidDict = json.load(frrk)


# 新建vip的uuid，第一个参数是天数，第二个参数是数量
@bot.command(name="vip-a")
async def get_vip_uuid(msg: Message, day: int = 30, num: int = 10):
    logging(msg)
    try:
        if msg.author_id == master_id:
            text = await create_vip_uuid(num, day)
            cm = CardMessage()
            c = Card(Module.Header(f"已生成新的uuid   数量:{num}  天数:{day}"),
                     Module.Divider(),
                     Module.Section(Element.Text(text, Types.Text.KMD)),
                     color='#e17f89')
            cm.append(c)
            await msg.reply(cm)
            print("[vip-c] create_vip_uuid reply successful!")
        else:
            await msg.reply("您没有权限操作此命令！")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] create_vip_uuid\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


# 兑换vip
@bot.command(name="vip-u", aliases=['兑换'])
async def buy_vip_uuid(msg: Message, uuid: str = 'err', *arg):
    logging(msg)
    if uuid == 'err':
        await msg.reply(f"只有输入vip的兑换码才可以操作哦！uuid: `{uuid}`")
        return
    try:
        #把bot传过去是为了让阿狸在有人成兑换激活码之后发送消息到log频道
        ret = await using_vip_uuid(msg, uuid, bot)

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] buy_vip_uuid\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新执行操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 看vip剩余时间
@bot.command(name="vip-c")
async def check_vip_timeremain(msg: Message, *arg):
    logging(msg)
    try:
        if not await vip_ck(msg):
            return
        # 获取时间
        ret_t = vip_time_remain(msg.author_id)
        ret_cm = await vip_time_remain_cm(ret_t)
        await msg.reply(ret_cm)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] ck_vip_timeremain\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新执行操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 看vip用户列表
@bot.command(name="vip-l")
async def list_vip_user(msg: Message, *arg):
    logging(msg)
    try:
        if msg.author_id == master_id:
            text = fetch_vip_user()
            cm2 = CardMessage()
            c = Card(Module.Header(f"当前vip用户列表如下"), color='#e17f89')
            c.append(Module.Section(Element.Text(f"```\n{text}```", Types.Text.KMD)))
            cm2.append(c)
            await msg.reply(cm2)
        else:
            await msg.reply("您没有权限操作此命令！")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] create_vip_uuid\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


# vip用户商店自定义图片
VipShopBgDict = {}
with open("./log/VipUserShopBg.json", 'r', encoding='utf-8') as frau:
    VipShopBgDict = json.load(frau)

#定期检查图片是否没问题
#下图用于替换违规的vip图片
illegal_img_11 = "https://img.kookapp.cn/assets/2022-09/a1k6QGZMiW0rs0rs.png"
illegal_img_169 = "https://img.kookapp.cn/assets/2022-09/CVWFac7CJG0zk0k0.png"


#替换掉违规图片（传入list的下标)
async def replace_illegal_img(user_id: str, num: int):
    """
        user_id:  kook user_id
        num: VipShopBgDict list index
    """
    try:
        global VipShopBgDict
        img_str = VipShopBgDict[user_id]["background"][num]
        VipShopBgDict[user_id]["background"][num] = illegal_img_169
        VipShopBgDict[user_id]["status"] = False  #需要重新加载图片
        with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipShopBgDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"[Replace_img] Au:{user_id} [{img_str}]")  #写入文件后打印log信息
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] replace_illegal_img\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await bot.client.send(debug_ch, err_str)  #发送消息到debug频道


async def check_vip_img():
    print("[BOT.TASK] check_vip_img start!")
    try:
        global VipShopBgDict
        cm0 = CardMessage()
        c = Card(color='#fb4b57')  #卡片侧边栏颜色
        text = f"您设置的vip背景图违规！请尽快替换"
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.powder, size='sm')))
        c.append(Module.Context(Element.Text("多次发送违禁图片会导致阿狸被封，请您慎重选择图片！", Types.Text.KMD)))
        #遍历vip用户的图片
        for vip_user, vip_bg in VipShopBgDict.items():
            user = await bot.client.fetch_user(vip_user)
            sz = len(vip_bg["background"])
            i = 0
            while i < sz:
                try:
                    bg_test = Image.open(io.BytesIO(await img_requestor(vip_bg["background"][i])))
                    i += 1
                except UnidentifiedImageError as result:
                    err_str = f"ERR! [{GetTime()}] checking [{vip_user}] img\n```\n{result}\n"
                    #把被ban的图片替换成默认的图片，打印url便于日后排错
                    err_str += f"[UnidentifiedImageError] url={vip_bg['background'][i]}\n```"
                    c.append(Module.Section(Element.Text(err_str, Types.Text.KMD)))
                    cm0.append(c)
                    await user.send(cm0)  # 发送私聊消息给用户
                    await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道
                    vip_bg["background"][i] = illegal_img_169  #修改成16比9的图片
                    vip_bg["status"] = False  #需要重新加载图片
                    print(err_str)
                except Exception as result:
                    err_str = f"ERR! [{GetTime()}] checking[{vip_user}]img\n```\n{traceback.format_exc()}\n```"
                    print(err_str)
                    c.append(Module.Section(Element.Text(err_str, Types.Text.KMD)))
                    cm0.append(c)
                    await user.send(cm0)
                    await bot.client.send(debug_ch, err_str)

            # 遍历完一个用户后打印结果
            print(f"[BOT.TASK] check_vip_img Au:{vip_user} finished!")
        #所有用户成功遍历后，写入文件
        with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipShopBgDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        #打印
        print("[BOT.TASK] check_vip_img finished!")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] check_vip_img\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道


#因为这个功能很重要，所以设置成可以用命令调用+定时任务
@bot.task.add_cron(hour=3, minute=0, timezone="Asia/Shanghai")
async def check_vip_img_task():
    await check_vip_img()


@bot.command(name="vip-img")
async def check_vip_img_task(msg: Message, *arg):
    logging(msg)
    if msg.author_id == master_id:
        await check_vip_img()
        await msg.reply("背景图片diy检查完成！")
    else:
        await msg.reply("您没有权限执行此命令！")
        return


#计算用户背景图的list大小，避免出现空list的情况
def len_VusBg(user_id: str):
    """
       - len(VipShopBgDict[user_id]["background"])
       - return 0 if user not in dict 
    """
    if user_id in VipShopBgDict:
        return len(VipShopBgDict[user_id]["background"])
    else:
        return 0


#因为下面两个函数都要用，所以直接独立出来
async def get_vip_shop_bg_cm(msg: Message):
    global VipShopBgDict
    if msg.author_id not in VipShopBgDict:
        return "您尚未自定义商店背景图！"
    elif len_VusBg(msg.author_id) == 0:
        return "您尚未自定义商店背景图！"

    cm = CardMessage()
    c1 = Card(color='#e17f89')
    c1.append(Module.Header('您当前设置的商店背景图如下'))
    c1.append(Module.Container(Element.Image(src=VipShopBgDict[msg.author_id]["background"][0])))
    sz = len(VipShopBgDict[msg.author_id]["background"])
    if sz > 1:
        c1.append(Module.Divider())
        c1.append(Module.Section(Element.Text('当前未启用的背景图，可用「/vip-shop-s 序号」切换', Types.Text.KMD)))
        i = 0
        while (i < sz):
            try:
                # 打开图片进行测试，没有问题就append
                bg_test = Image.open(io.BytesIO(await img_requestor(VipShopBgDict[msg.author_id]["background"][i])))
                if i == 0:  #第一张图片只进行打开测试，没有报错就是没有违规，不进行后续的append操作
                    i += 1
                    continue
                # 插入后续其他图片
                c1.append(
                    Module.Section(Element.Text(f' [{i}]', Types.Text.KMD),
                                   Element.Image(src=VipShopBgDict[msg.author_id]["background"][i])))
                i += 1
            except UnidentifiedImageError as result:
                err_str = f"ERR! [{GetTime()}] checking [{msg.author_id}] img\n```\n{result}\n"
                #把被ban的图片替换成默认的图片，打印url便于日后排错
                err_str += f"[UnidentifiedImageError] url={VipShopBgDict[msg.author_id]['background'][i]}\n```"
                await replace_illegal_img(msg.author_id, i)  #替换图片
                await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道
                print(err_str)
                return f"您上传的图片违规！请慎重选择图片。多次上传违规图片会导致阿狸被封！下方有违规图片的url\n{err_str}"

    cm.append(c1)
    return cm


@bot.command(name="vip-shop")
async def vip_shop_bg_set(msg: Message, icon: str = "err", *arg):
    logging(msg)
    if icon != 'err' and ('http' not in icon or '](' not in icon):
        await msg.reply(f"请提供正确的图片url！\n当前：`{icon}`")
        return

    cm = CardMessage()
    c = Card(color='#fb4b57')
    try:
        if not await vip_ck(msg):
            return

        x3 = "[None]"
        if icon != 'err':
            user_ind = (msg.author_id in VipShopBgDict)  #判断当前用户在不在dict中
            if user_ind and len(VipShopBgDict[msg.author_id]["background"]) >= 4:
                text = f"当前仅支持保存4个自定义图片"
                c.append(
                    Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.that_it, size='sm')))
                c.append(Module.Context(Element.Text("您可用「/vip-shop-d 图片编号」删除已有图片再添加", Types.Text.KMD)))
                cm.append(c)
                await msg.reply(cm)
                return

            #提取图片url
            x1 = icon.find('](')
            x2 = icon.find(')', x1 + 2)
            x3 = icon[x1 + 2:x2]
            print(f"[vip-shop] Au:{msg.author_id} get_url ", x3)
            try:
                # 检查图片链接格式是否支持
                if ('png' not in x3) and ('jpg' not in x3) and ('jpeg' not in x3):
                    text = f"您当前上传的图片格式不支持！请上传png/jpg/jpeg格式的图片"
                    c.append(
                        Module.Section(Element.Text(text, Types.Text.KMD),
                                       Element.Image(src=icon_cm.ahri_dark, size='sm')))
                    c.append(Module.Context(Element.Text("请优先尝试png格式图片，其余格式兼容性有一定问题", Types.Text.KMD)))
                    cm.append(c)
                    await msg.reply(cm)
                    print(f"[vip-shop] Au:{msg.author_id} img_type_not support")
                    return
                #打开图片(测试)
                bg_vip = Image.open(io.BytesIO(await img_requestor(x3)))
            except UnidentifiedImageError as result:
                err_str = f"ERR! [{GetTime()}] vip_shop_imgck\n```\n{result}\n```"
                print(err_str)
                await msg.reply(f"图片违规！请重新上传\n{err_str}")
                return

            #到插入的时候再创建list，避免出现图片没有通过检查，但是list又被创建了的情况
            if not user_ind:
                VipShopBgDict[msg.author_id] = {}
                VipShopBgDict[msg.author_id]["background"] = list()
                #新建用户，但是有可能已经缓存了默认的背景图片，所以状态为false（重画）
                VipShopBgDict[msg.author_id]["status"] = False
            #插入图片
            VipShopBgDict[msg.author_id]["background"].append(x3)

        cm = await get_vip_shop_bg_cm(msg)
        #先让测试bot把这个卡片发到频道，如果发出去了说明json没有问题
        await bot_upimg.client.send(cm_send_test, cm)
        print(f"[vip-shop] Au:{msg.author_id} cm_send_test success")
        #然后阿狸在进行回应
        await msg.reply(cm)

        # 修改/新增都需要写入文件
        with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipShopBgDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        # 打印用户新增的图片日后用于排错
        print(f"[vip-shop] Au:{msg.author_id} add ", x3)

    except requester.HTTPRequester.APIRequestFailed as result:
        err_str = f"ERR! [{GetTime()}]  vip_shop_cm\n```\n{result}\n```\n"
        print(json.dumps(cm))
        cm1 = CardMessage()
        c = Card(
            Module.Header(f"卡片消息json没有通过验证或者不存在"), Module.Divider(),
            Module.Section(Element.Text(f"图片违规或图片格式有问题，请不要多次重试，会导致阿狸被封！建议加入帮助频道找我康康到底是啥问题\n{err_str}", Types.Text.KMD)),
            Module.Divider(),
            Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm1.append(c)
        await msg.reply(cm1)
        VipShopBgDict[msg.author_id]["background"].remove(x3)  #删掉里面的图片
        print(err_str)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}]  vip_shop\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm1 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了未知错误"), color='#fb4b57')
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n\n建议加入帮助频道找我康康到底是啥问题", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm1.append(c)
        await msg.reply(cm1)


@bot.command(name="vip-shop-s")
async def vip_shop_bg_set_s(msg: Message, num: str = "err", *arg):
    logging(msg)
    if num == 'err':
        await msg.reply(f"请提供正确的图片序号！\n当前：`{num}`")
        return
    try:
        global VipShopBgDict
        if not await vip_ck(msg):
            return
        if msg.author_id not in VipShopBgDict:
            await msg.reply("您尚未自定义商店背景图！")
            return

        num = str2int(num)
        if num < len(VipShopBgDict[msg.author_id]["background"]):
            try:  #打开用户需要切换的图片
                bg_vip = Image.open(io.BytesIO(await img_requestor(VipShopBgDict[msg.author_id]["background"][num])))
            except UnidentifiedImageError as result:
                err_str = f"ERR! [{GetTime()}] vip_shop_s_imgck\n```\n{result}\n```"
                await msg.reply(f"图片违规！请重新上传\n{err_str}")
                await replace_illegal_img(msg.author_id, num)  #替换图片
                print(err_str)
                return
            # 图片检查通过，交换两个图片的位置
            icon_num = VipShopBgDict[msg.author_id]["background"][num]
            VipShopBgDict[msg.author_id]["background"][num] = VipShopBgDict[msg.author_id]["background"][0]
            VipShopBgDict[msg.author_id]["background"][0] = icon_num
            VipShopBgDict[msg.author_id]['status'] = False  #修改图片之后，因为8点bot存储了商店图，所以需要重新获取新的背景

            # #进行缩放+贴上图后保存
            # bg_vip = resize_vip(1280,720,bg_vip)
            # bg_vip = bg_vip.convert('RGBA')
            # # alpha_composite才能处理透明的png。参数1是底图，参数2是需要粘贴的图片
            # finalImg = Image.alpha_composite(bg_vip, bg_main_169)
            # finalImg.save(f'./log/img_temp_vip/bg/{msg.author_id}.png')
        else:
            await msg.reply("请提供正确返回的图片序号，可以用`/vip-shop`进行查看")
            return

        cm = await get_vip_shop_bg_cm(msg)
        #先让测试bot把这个卡片发到频道，如果发出去了说明json没有问题
        await bot_upimg.client.send(cm_send_test, cm)
        print(f"[vip-shop] Au:{msg.author_id} cm_send_test success")
        #然后阿狸在进行回应
        await msg.reply(cm)

        # 修改/新增都需要写入文件
        with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipShopBgDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"[vip-shop-s] Au:{msg.author_id} switch to [{VipShopBgDict[msg.author_id]['background'][0]}]")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] vip_shop_s\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了未知错误"), color='#fb4b57')
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n\n您可能需要重新执行操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)


@bot.command(name="vip-shop-d")
async def vip_shop_bg_set_d(msg: Message, num: str = "err", *arg):
    logging(msg)
    if num == 'err':
        await msg.reply(f"请提供正确的图片序号！\n当前：`{num}`")
        return
    try:
        if not await vip_ck(msg):
            return
        if msg.author_id not in VipShopBgDict:
            await msg.reply("您尚未自定义商店背景图！")
            return

        num = str2int(num)
        if num < len(VipShopBgDict[msg.author_id]["background"]) and num > 0:
            # 删除图片
            del_img_url = VipShopBgDict[msg.author_id]["background"][num]
            del VipShopBgDict[msg.author_id]["background"][num]
        elif num == 0:
            await msg.reply("不支持删除当前正在使用的背景图！")
            return
        else:
            await msg.reply("请提供正确返回的图片序号，可以用`/vip-shop`进行查看")
            return

        cm = await get_vip_shop_bg_cm(msg)
        #先让测试bot把这个卡片发到频道，如果发出去了说明json没有问题
        await bot_upimg.client.send(cm_send_test, cm)
        print(f"[vip-shop] Au:{msg.author_id} cm_send_test success")
        #然后阿狸在进行回应
        await msg.reply(cm)

        # 修改/新增都需要写入文件
        with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipShopBgDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"[vip-shop-d] Au:{msg.author_id} delete [{del_img_url}]")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] vip_shop_d\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了未知错误"), color='#fb4b57')
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n\n您可能需要重新执行操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)

from endpoints import roll_vip_start
#用来存放roll的频道/服务器/回应用户的dict
RollVipDcit={}
with open("./log/VipRoll.json", 'r', encoding='utf-8') as frau:
    RollVipDcit = json.load(frau)

# 判断消息的emoji回应，并记录id
@bot.on_event(EventTypes.ADDED_REACTION)
async def vip_roll_log(b: Bot, event: Event):
    global RollVipDcit
    if event.body['msg_id'] not in RollVipDcit:
        return
    else:
        user_id = event.body['user_id']
        # 把用户id添加到list中
        log_str = f"[vip-roll-log] Au:{user_id} roll_msg:{event.body['msg_id']}"
        if user_id not in RollVipDcit[event.body['msg_id']]['user']:
            RollVipDcit[event.body['msg_id']]['user'].append(user_id)
            channel = await bot.client.fetch_public_channel(event.body['channel_id'])
            await bot.client.send(channel,f"[添加回应]->抽奖参加成功！", temp_target_id=event.body['user_id'])
            log_str +=" Join"#有join的才是新用户
            #用户不在才有变动，写入文件
            with open("./log/VipRoll.json", 'w', encoding='utf-8') as fw2:
                json.dump(RollVipDcit, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        
        print(log_str)
        
# 开启一波抽奖
@bot.command(name='vip-r',aliases=['vip-roll'])
async def vip_roll(msg:Message,vday:int=7,vnum:int=5,rday:float=1.0):
    logging(msg)
    if msg.author_id != master_id:
        await msg.reply(f"您没有权限执行本命令")
        return
    # 设置开始抽奖
    global RollVipDcit
    cm = roll_vip_start(vnum,vday,rday)
    roll_ch = await bot.client.fetch_public_channel(msg.ctx.channel.id)
    roll_send = await bot.client.send(roll_ch,cm)
    RollVipDcit[roll_send['msg_id']]={}
    RollVipDcit[roll_send['msg_id']]['time']= time.time()+rday*86400
    RollVipDcit[roll_send['msg_id']]['nums']= vnum
    RollVipDcit[roll_send['msg_id']]['days']= vday
    RollVipDcit[roll_send['msg_id']]['channel_id']=msg.ctx.channel.id
    RollVipDcit[roll_send['msg_id']]['guild_id']=msg.ctx.guild.id
    RollVipDcit[roll_send['msg_id']]['user']=list()
    with open("./log/VipRoll.json", 'w', encoding='utf-8') as fw2:
        json.dump(RollVipDcit, fw2, indent=2, sort_keys=True, ensure_ascii=False)
    print(f"[vip-roll] card message send to {msg.ctx.channel.id}")
    
@bot.task.add_interval(minutes=1)
async def vip_roll_task():
    global RollVipDcit,VipUserDict
    rollvipdict_temp = copy.deepcopy(RollVipDcit) #临时变量用于修改
    for msg_id,minfo in RollVipDcit.items():
        if time.time()<minfo['time']:
            continue
        else:
            print(f"[BOT.TASK] vip_roll_task msg:{msg_id}")
            vday = RollVipDcit[msg_id]['days']
            vnum = RollVipDcit[msg_id]['nums']
            # 结束抽奖
            log_str=f"```\n[MsgID] {msg_id}\n"
            send_str="恭喜 "
            # 生成n个随机数
            ran = random.sample(range(0, len(RollVipDcit[msg_id]['user'])-1),vnum)
            for j in ran:
                user_id = RollVipDcit[msg_id]['user'][j]
                user = await bot.client.fetch_user(user_id)
                # 设置用户的时间和个人信息
                time_vip = vip_time_stamp(user_id, vday)
                VipUserDict[user_id] = {
                    'time':time_vip,
                    'name_tag':f"{user.username}#{user.identify_num}"
                }
                #创建卡片消息
                cm = CardMessage()
                c=Card(Module.Section(Element.Text("恭喜您中奖vip激活码了！", Types.Text.KMD), Element.Image(src=icon_cm.ahri_kda2, size='sm')))
                c.append(Module.Context(Element.Text(f"您抽中了{vday}天vip", Types.Text.KMD)))
                c.append(
                    Module.Countdown(datetime.now() + timedelta(seconds=vip_time_remain(user_id)), mode=Types.CountdownMode.DAY))
                c.append(Module.Divider())
                c.append(Module.Section('加入官方服务器，即可获得「阿狸赞助者」身份组', Element.Button('来狸', 'https://kook.top/gpbTwZ',
                                                                                Types.Click.LINK)))
                cm.append(c)
                await user.send(cm)
                log_str+=f"[vip-roll] Au:{user_id} get [{vday}]day-vip\n"
                send_str+=f"(met){user_id}(met) "
                
            log_str+="```"
            send_str+="获得了本次奖品！"
            await bot.client.send(debug_ch,log_str) #发送此条抽奖信息的结果到debug
            #发送结果到抽奖频道
            roll_ch = await bot.client.fetch_public_channel(RollVipDcit[msg_id]['channel_id'])
            cm1 = CardMessage()
            c=Card(Module.Header(f"🎊 阿狸vip {RollVipDcit[msg_id]['days']}天体验卡 🎊"),
                Module.Section(Element.Text(send_str, Types.Text.KMD)),
                Module.Context(Element.Text(f"本次抽奖结束，奖励已私信发送", Types.Text.KMD)))
            cm1.append(c)
            await bot.client.send(roll_ch,cm1)
            del rollvipdict_temp[msg_id] #删除此条抽奖信息
        
    # 更新抽奖列表(如果有变化)
    if rollvipdict_temp!=RollVipDcit:
        RollVipDcit=rollvipdict_temp
        with open("./log/VipRoll.json", 'w', encoding='utf-8') as fw2:
            json.dump(RollVipDcit, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        # 更新vip用户列表
        with open("./log/VipUser.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipUserDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(log_str)# 打印中奖用户作为log
    

##############################################################################

# 预加载用户token(其实已经没用了)
with open("./log/UserAuth.json", 'r', encoding='utf-8') as frau:
    UserTokenDict = json.load(frau)
# 所有皮肤
with open("./log/ValSkin.json", 'r', encoding='utf-8') as frsk:
    ValSkinList = json.load(frsk)
# 所有商品价格
with open("./log/ValPrice.json", 'r', encoding='utf-8') as frpr:
    ValPriceList = json.load(frpr)
# 所有捆绑包的图片
with open("./log/ValBundle.json", 'r', encoding='utf-8') as frbu:
    ValBundleList = json.load(frbu)
# 所有物品等级（史诗/传说）
with open("./log/ValIters.json", 'r', encoding='utf-8') as frrk:
    ValItersList = json.load(frrk)


#从list中获取价格
def fetch_item_price_bylist(item_id):
    for item in ValPriceList['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item


#从list中获取等级(这个需要手动更新)
def fetch_item_iters_bylist(iter_id):
    for iter in ValItersList['data']:  #遍历查找指定uuid
        if iter_id == iter['uuid']:
            res = {'data': iter}  #所以要手动创建一个带data的dict作为返回值
            return res


#从list中获取皮肤
def fetch_skin_bylist(item_id):
    res = {}  #下面我们要操作的是获取通行证的皮肤，但是因为遍历的时候已经跳过data了，返回的时候就不好返回
    for item in ValSkinList['data']:  #遍历查找指定uuid
        if item_id == item['levels'][0]['uuid']:
            res['data'] = item  #所以要手动创建一个带data的dict作为返回值
            return res


#从list中，通过皮肤名字获取皮肤列表
def fetch_skin_byname_list(name):
    wplist = list()  #包含该名字的皮肤list
    for skin in ValSkinList['data']:
        if name in skin['displayName']:
            data = {'displayName': skin['displayName'], 'lv_uuid': skin['levels'][0]['uuid']}
            wplist.append(data)
    return wplist


# 用来存放auth对象（无法直接保存到文件）
UserAuthDict = {}
# 用来存放已保存cookie的用户id（保存在文件中）
UserCookieDict = {}
#用于限制用户操作，一分钟只能3次
login_dict = {}
#全局的速率限制，如果触发了速率限制的err，则阻止所有用户login
login_rate_limit = {'limit': False, 'time': time.time()}


#查询当前有多少用户登录了
@bot.command(name="ckau")
async def check_UserAuthDict_len(msg: Message):
    logging(msg)
    sz = len(UserAuthDict)
    res = f"UserAuthDict_len: `{sz}`"
    print(res)
    await msg.reply(res)


#遇到全局速率限制统一获取卡片消息
def get_login_rate_cm(time_diff=None):
    if time_diff != None:
        text = f"阿狸的登录请求超速！请在 {format(240.0-time_diff, '.1f')}s 后重试"
    else:
        text = f"阿狸的登录请求超速！请在 240.0s 后重试"
    cm = CardMessage()
    c = Card(color='#fb4b57')
    c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.lagging, size='sm')))
    c.append(Module.Context(Element.Text("raise RiotRatelimitError, please try again later", Types.Text.KMD)))
    cm.append(c)
    return cm


#检查是否存在用户请求超速
async def check_user_login_rate(msg: Message):
    """
    Returns:
     - True: UserRatelimitError
     - False: good_to_go
    """
    global login_dict  #检查用户请求次数，避免超速
    if msg.author_id in login_dict:
        time_stap = time.time()
        time_diff = time_stap - login_dict[msg.author_id]['time']
        if login_dict[msg.author_id]['nums'] >= 3 and time_diff <= 70.0:
            # 思路是第一次请求超速后，要过70s才能执行下一次
            if login_dict[msg.author_id]['nums'] == 3:  #第一次请求超速
                login_dict[msg.author_id]['time'] = time_stap  #更新时间戳
                time_diff = 0  #更新diff

            login_dict[msg.author_id]['nums'] += 1
            time_remain = format(70.0 - time_diff, '.1f')  #剩余需要等待的时间
            text = f"用户登录请求超速，请在 {time_remain}s 后重试"
            cm0 = CardMessage()
            c = Card(color='#fb4b57')  #卡片侧边栏颜色
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.powder, size='sm')))
            c.append(
                Module.Context(
                    Element.Text(f"raise UserRatelimitError, please try again after {time_remain}s", Types.Text.KMD)))
            cm0.append(c)
            await msg.reply(cm0)
            return True
        elif time_diff > 70.0:  #请求次数超限，但是已经过了70s
            login_dict[msg.author_id]['nums'] = 1  #重置为1
            login_dict[msg.author_id]['time'] = time_stap
            return False
        else:  # login_dict[msg.author_id]['nums']<3 and time_diff<=60.0
            login_dict[msg.author_id]['nums'] += 1
            return False
    else:
        login_dict[msg.author_id] = {'time': time.time(), 'nums': 1}
        return False


#在阿狸开机的时候自动加载所有保存过的cookie
@bot.task.add_date()
async def loading_channel_cookie():
    try:
        global debug_ch, cm_send_test
        cm_send_test = await bot_upimg.client.fetch_public_channel('3001307981469706')
        debug_ch = await bot.client.fetch_public_channel(Debug_ch)
        print("[BOT.TASK] fetch_public_channel success")
    except:
        print("[BOT.TASK] fetch_public_channel failed")
        os._exit(-1)  #出现错误直接退出程序

    print("[BOT.TASK] loading cookie start")
    global UserAuthDict
    log_str = "[BOT.TASK] cookie path not exists = Au:"
    #遍历用户列表
    for user, uinfo in VipUserDict.items():
        cookie_path = f"./log/cookie/{user}.cke"
        #如果路径存在，那么说明已经保存了这个vip用户的cookie
        if os.path.exists(cookie_path):
            auth = RiotAuth()  #新建一个对象
            auth._cookie_jar.load(cookie_path)  #加载cookie
            ret_bool = await auth.reauthorize()  #尝试登录
            if ret_bool:  # True登陆成功
                UserAuthDict[user] = auth  #将对象插入
                print(f"[BOT.TASK] Au:{user} - load cookie success!")
                #不用重新修改UserTokenDict里面的游戏名和uuid
                #因为UserTokenDict是在login的时候保存的，只要用户没有切换账户
                #那么玩家id和uuid都是不会变化的，也没必要重新加载
            else:
                print(f"[BOT.TASK] Au:{user} - load cookie failed!")
                continue
        else:
            log_str += f"({user}) "
            continue
    #结束任务
    print(log_str)  #打印路径不存在的用户
    print("[BOT.TASK] loading cookie finished")


# 登录，保存用户的token
@bot.command(name='login')
async def login_authtoken(msg: Message, user: str = 'err', passwd: str = 'err', *arg):
    print(f"[{GetTime()}] Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = /login")
    if passwd == 'err' or user == 'err':
        await msg.reply(f"参数不完整，请提供您的账户和密码！\naccout: `{user}` passwd: `{passwd}`")
        return
    elif arg != ():
        await msg.reply(f"您给予了多余的参数！\naccout: `{user}` passwd: `{passwd}`\n多余参数: `{arg}`")
        return

    global login_rate_limit
    try:
        cm0 = CardMessage()
        c = Card(color='#fb4b57')  #卡片侧边栏颜色
        global UserTokenDict, UserAuthDict
        if msg.author_id in UserAuthDict:  #用in判断dict是否存在这个键，如果用户id已有，则不进行操作
            text = "您已经登陆，无需重复操作"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.shaka, size='sm')))
            c.append(Module.Context(Element.Text("如需重新登录，请先logout退出当前登录", Types.Text.KMD)))
            cm0.append(c)
            await msg.reply(cm0)
            return

        #全局请求超速
        if login_rate_limit['limit']:
            time_stap = time.time()
            time_diff = time_stap - login_rate_limit['time']
            if time_diff <= 240.0:  #240s内无法使用login
                ret_cm = get_login_rate_cm(time_diff)
                await msg.reply(ret_cm)
                print(f"Login  - Au:{msg.author_id} - raise global_login_rate_limit")
                return
            else:  #超过240s，解除限制
                login_rate_limit['limit'] = False
                login_rate_limit['time'] = time_stap

        if await check_user_login_rate(msg):
            print(f"Login  - Au:{msg.author_id} - raise user_login_rate_limit")
            return

        text = "正在尝试获取您的riot账户token"
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.val_logo_gif, size='sm')))
        c.append(Module.Context(Element.Text("小憩一下，很快就好啦！", Types.Text.KMD)))
        cm0.append(c)
        send_msg = await msg.reply(cm0)  #记录消息id用于后续更新

        # 不在AuthDict中才进行获取token的操作（耗时)
        res_auth = await authflow(user, passwd)
        UserTokenDict[msg.author_id] = {'auth_user_id': res_auth.user_id}  #先创建基本信息 dict[键] = 值
        userdict = {
            'auth_user_id': res_auth.user_id,
            'access_token': res_auth.access_token,
            'entitlements_token': res_auth.entitlements_token
        }
        res_gameid = await fetch_user_gameID(userdict)  # 获取用户玩家id
        UserTokenDict[msg.author_id]['GameName'] = res_gameid[0]['GameName']
        UserTokenDict[msg.author_id]['TagLine'] = res_gameid[0]['TagLine']
        UserAuthDict[msg.author_id] = res_auth  #将对象插入

        cm = CardMessage()
        text = f"登陆成功！欢迎回来，{UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}"
        c = Card(color='#fb4b57')
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.correct, size='sm')))
        c.append(Module.Context(Element.Text("当前token失效时间为1h，有任何问题请[点我](https://kook.top/gpbTwZ)", Types.Text.KMD)))
        cm.append(c)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)

        # 修改/新增都需要写入文件
        with open("./log/UserAuth.json", 'w', encoding='utf-8') as fw2:
            json.dump(UserTokenDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

        # 如果是vip用户，则保存cookie
        if await vip_ck(msg.author_id):
            cookie_path = f"./log/cookie/{msg.author_id}.cke"#用于保存cookie的路径
            res_auth._cookie_jar.save(cookie_path)#保存
            global VipShopBgDict #因为换了用户，所以需要修改状态码重新获取商店
            if msg.author_id in VipShopBgDict:
                VipShopBgDict[msg.author_id]['status']=False
                #为了保险起见，保存一下状态信息到文件
                with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw1:
                    json.dump(VipShopBgDict, fw1, indent=2, sort_keys=True, ensure_ascii=False)

        # 全部都搞定了，打印登录信息
        print(
            f"Login  - Au:{msg.author_id} - {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}"
        )

    except auth_exceptions.RiotAuthenticationError as result:
        print(f"ERR! [{GetTime()}] login - {result}")
        cm = CardMessage()
        c = Card(color='#fb4b57')
        text = f"当前的账户密码真的对了吗？"
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.dont_do_that, size='sm')))
        c.append(Module.Context(Element.Text("Make sure username and password are correct", Types.Text.KMD)))
        cm.append(c)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except auth_exceptions.RiotMultifactorError as result:
        print(f"ERR! [{GetTime()}] login - {result}")
        text = f"当前不支持开启了`邮箱双重验证`的账户"
        cm = CardMessage()
        c = Card(color='#fb4b57')
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.that_it, size='sm')))
        c.append(Module.Context(Element.Text("Multi-factor authentication is not currently supported", Types.Text.KMD)))
        cm.append(c)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except auth_exceptions.RiotRatelimitError as result:
        print(f"ERR! [{GetTime()}] login - riot_auth.auth_exceptions.RiotRatelimitError")
        #更新全局速率限制
        login_rate_limit['limit'] = True
        login_rate_limit['time'] = time.time()
        ret_cm = get_login_rate_cm()  #这里是第一个出现速率限制err的用户
        await upd_card(send_msg['msg_id'], ret_cm, channel_type=msg.channel_type)
    except:
        err_str = f"ERR! [{GetTime()}] login\n ```\n{traceback.format_exc()}\n```"
        print(err_str)  #只有不认识的报错消息才打印结果
        cm = CardMessage()
        c = Card(color='#fb4b57')
        c.append(Module.Header(f"很抱歉，发生了未知错误"))
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n\n您可能需要重新执行/login操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm.append(c)
        await msg.reply(cm)


#重新登录（kook用户id）
async def login_re_auth(kook_user_id: str):
    base_print = f"[{GetTime()}] Au:{kook_user_id} = "
    print(base_print + "auth_token failure,trying reauthorize()")
    global UserAuthDict
    auth = UserAuthDict[kook_user_id]
    #用cookie重新登录,会返回一个bool是否成功
    ret = await auth.reauthorize()
    if ret:  #会返回一个bool是否成功,成功了重新赋值
        UserAuthDict[kook_user_id] = auth
        print(base_print + "reauthorize() Successful!")
    else:
        print(base_print + "reauthorize() Failed! T-T")  #失败打印

    return ret  #正好返回一个bool


#判断是否需要重新获取token
async def check_re_auth(def_name: str = "", msg: Union[Message, str] = ''):
    """
    return value:
     - True: no need to reauthorize / get `user_id` as params & reauhorize success 
     - False: unkown err / reauthorize failed
     - send_msg: get `Message` as params & reauhorize success
    """
    user_id = "[ERR!]"  #先给userid赋值，避免下方打印的时候报错（不出意外是会被下面的语句修改的）
    try:
        user_id = msg if isinstance(msg, str) else msg.author_id  #如果是str就直接用
        auth = UserAuthDict[user_id]
        userdict = {
            'auth_user_id': auth.user_id,
            'access_token': auth.access_token,
            'entitlements_token': auth.entitlements_token
        }
        resp = await fetch_valorant_point(userdict)
        # print('[Ckeck_re_auth]', resp)
        # resp={'httpStatus': 400, 'errorCode': 'BAD_CLAIMS', 'message': 'Failure validating/decoding RSO Access Token'}
        # 如果没有这个键，会直接报错进except; 如果有这个键，就可以继续执行下面的内容
        test = resp['httpStatus']
        is_msg = isinstance(msg, Message)  #判断传入的类型是不是消息
        if is_msg:  #如果传入的是msg，则提示用户
            cm = CardMessage()
            text = f"获取「{def_name}」失败！正在尝试重新获取token，您无需操作"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.im_good_phoniex,
                                                                                 size='sm')))
            c.append(Module.Context(Element.Text(f"{resp['message']}", Types.Text.KMD)))
            cm.append(c)
            send_msg = await msg.reply(cm)

        #不管传入的是用户id还是msg，都传userid进入该函数
        ret = await login_re_auth(user_id)
        if ret == False and is_msg:  #没有正常返回
            cm = CardMessage()
            text = f"重新获取token失败，请私聊「/login」重新登录\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.crying_crab, size='sm')))
            c.append(Module.Context(Element.Text(f"Auto Reauthorize Failed!", Types.Text.KMD)))
            cm.append(c)  #如果重新获取token失败，则更新上面的消息
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
        elif ret == True and is_msg:  #正常重新登录，且传过来了消息
            return send_msg  #返回发送出去的消息（用于更新）

        return ret  #返回假
    except Exception as result:
        if 'httpStatus' in str(result):
            print(f"[Ckeck_re_auth] Au:{user_id} No need to reauthorize [{result}]")
            return True
        else:
            print(f"[Ckeck_re_auth] Unkown ERR!\n{traceback.format_exc()}")
            return False


# 测试是否已登陆
@bot.command(name="login-t")
async def test_if_login(msg: Message, *arg):
    logging(msg)
    try:
        if msg.author_id in UserAuthDict:
            flag_au = 1
            reau = await check_re_auth("测试登录", msg)
            if reau == False: return  #如果为假说明重新登录失败

            await msg.reply(
                f"您当前已登录账户 `{UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}`")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] test_if_login\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


# 退出登录
@bot.command(name='logout')
async def logout_authtoken(msg: Message, *arg):
    logging(msg)
    try:
        global UserTokenDict, UserAuthDict
        if msg.author_id not in UserAuthDict:  #使用not in判断是否不存在
            cm = CardMessage()
            text = f"你还没有登录呢！"
            c = Card(color='#fb4b57')
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.that_it, size='sm')))
            c.append(Module.Context(Element.Text(f"「/login 账户 密码」请确认您知晓这是一个风险操作", Types.Text.KMD)))
            cm.append(c)
            await msg.reply(cm)
            return

        #如果id存在， 删除id
        del UserAuthDict[msg.author_id]  #先删除auth对象
        print(
            f"Logout - Au:{msg.author_id} - {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}"
        )
        cm = CardMessage()
        text = f"已退出登录！下次再见，{UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}"
        c = Card(color='#fb4b57')
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.crying_crab, size='sm')))
        c.append(Module.Context(Element.Text(f"你会回来的，对吗？", Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)

        #最后重新执行写入
        del UserTokenDict[msg.author_id]
        with open("./log/UserAuth.json", 'w', encoding='utf-8') as fw1:
            json.dump(UserTokenDict, fw1, indent=2, sort_keys=True, ensure_ascii=False)
        fw1.close()
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] logout\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


# 不再使用定时任务，而是把所有更新封装成一个命令。
async def update_skins(msg: Message):
    try:
        global ValSkinList
        skins = await fetch_skins_all()
        ValSkinList = skins
        # 写入文件
        with open("./log/ValSkin.json", 'w', encoding='utf-8') as fw2:
            json.dump(ValSkinList, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"[{GetTime()}] update_skins finished!")
        return True
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] update_skins\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        return False


#因为下方获取物品价格的操作需要authtoken，自动更新容易遇到token失效的情况
async def update_price(msg: Message):
    try:
        global ValPriceList
        reau = await check_re_auth("物品价格", msg)
        if reau == False: return  #如果为假说明重新登录失败
        # 调用api获取价格列表
        auth = UserAuthDict[msg.author_id]
        userdict = {
            'auth_user_id': auth.user_id,
            'access_token': auth.access_token,
            'entitlements_token': auth.entitlements_token
        }
        prices = await fetch_item_price_all(userdict)
        ValPriceList = prices  # 所有价格的列表
        # 写入文件
        with open("./log/ValPrice.json", 'w', encoding='utf-8') as fw2:
            json.dump(ValPriceList, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"[{GetTime()}] update_item_price finished!")
        return True
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] update_price\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        return False


# 更新捆绑包
async def update_bundle_url(msg: Message):
    try:
        global ValBundleList
        resp = await fetch_bundles_all()  #从官方获取最新list
        if len(resp['data']) == len(ValBundleList):  #长度相同代表没有更新
            print(f"[{GetTime()}] len is the same, doesn't need update!")
            await msg.reply("BundleList_len相同，无需更新")
            return

        for b in resp['data']:
            flag = 0
            for local_B in ValBundleList:  #不在
                if b['uuid'] == local_B['uuid']:  #相同代表存在无需更新
                    flag = 1  #找到了，无需更新
                    break

            if flag != 1:  #不存在创建图片准备上传
                bg_bundle_icon = Image.open(io.BytesIO(await img_requestor(b['displayIcon'])))
                imgByteArr = io.BytesIO()
                bg_bundle_icon.save(imgByteArr, format='PNG')
                imgByte = imgByteArr.getvalue()
                print(f"Uploading - {b['displayName']}")
                bundle_img_src = await bot_upimg.client.create_asset(imgByte)
                print(f"{b['displayName']} - url: {bundle_img_src}")
                b['displayIcon2'] = bundle_img_src  #修改url
                ValBundleList.append(b)  #插入

        with open("./log/ValBundle.json", 'w', encoding='utf-8') as fw1:
            json.dump(ValBundleList, fw1, indent=2, sort_keys=True, ensure_ascii=False)

        print(f"[{GetTime()}] update_bundle_url finished!")
        return True
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] update_bundle_url\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        return False


# 手动更新商店物品和价格
@bot.command(name='update_spb')
async def update_skin_price(msg: Message):
    logging(msg)
    if msg.author_id == master_id:
        if await update_skins(msg):
            await msg.reply(f"成功更新：商店皮肤")
        if await update_price(msg):
            await msg.reply(f"成功更新：物品价格")
        if await update_bundle_url(msg):
            await msg.reply(f"成功更新：捆绑包")


#用来存放用户每天的商店
UserShopDict = {}


#计算当前时间和明天早上8点的差值
def shop_time_remain():
    today = datetime.today().strftime("%y-%m-%d %H:%M:%S")  #今天日期+时间
    tomorow = (datetime.today() + timedelta(days=1)).strftime("%y-%m-%d")  #明天日期
    #print(f"{tomorow} 08:00:00")
    times_tomorow = time.mktime(time.strptime(f"{tomorow} 08:00:00", "%y-%m-%d %H:%M:%S"))  #明天早上8点时间戳
    times_now = time.mktime(time.strptime(f"{today}", "%y-%m-%d %H:%M:%S"))  #现在的时间戳
    #print(times_tomorow)
    timeout = times_tomorow - times_now  #计算差值
    timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  #转换成可读时间
    #print(timeout)
    return timeout


def isSame_Authuuid(msg: Message):  #判断uuid是否相等
    return UserShopDict[msg.author_id]["auth_user_id"] == UserTokenDict[msg.author_id]["auth_user_id"]


#每天早上8点准时清除商店dict
@bot.task.add_cron(hour=8, minute=0, timezone="Asia/Shanghai")
async def clear_usershopdict():
    global UserShopDict
    UserShopDict = {}
    print("[BOT.TASK] clear UserShopDict finished")


# 获取每日商店的命令
async def get_daily_shop_vip_img(list_shop: dict,
                                 userdict: dict,
                                 user_id: str,
                                 is_vip: bool = True,
                                 msg: Message = None):
    """save img:
     - bg.save(f"./log/img_temp_vip/shop/{user_id}.png", format='PNG')
     
    returns dict:
     - {"status":False,"value":f"{err_str}"}
     - {"status":True,"value":bg}
    """
    global VipShopBgDict
    #vip_bg_path = f'./log/img_temp_vip/bg/{user_id}.png'
    if len_VusBg(user_id) > 0:  #如果为0则不执行自定义图片（避免空list）
        # 如果背景图片路径不存在（说明没有缓存） 现在因为在前面已经判断过，所以直接执行画图
        #if not os.path.exists(vip_bg_path):
        try:  #打开图片进行测试
            bg_vip = Image.open(io.BytesIO(await img_requestor(VipShopBgDict[user_id]["background"][0])))
            #如果图片打开没有问题，那么修改状态码
            VipShopBgDict[user_id]['status'] = True
            with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw1:
                json.dump(VipShopBgDict, fw1, indent=2, sort_keys=True, ensure_ascii=False)
        except UnidentifiedImageError as result:
            err_str = f"ERR! [{GetTime()}] vip_shop_imgck\n```\n{result}\n```"
            await replace_illegal_img(user_id, 0)  #替换图片
            # if msg != None:
            #     await msg.reply(f"当前使用的图片违规！请重新上传您的背景图\n{err_str}")
            print(err_str)  #写入文件后打印log信息
            return {"status": False, "value": f"当前使用的图片违规！请重新上传您的背景图\n{err_str}"}

        #图没有问题，则缩放后保存
        bg_vip = resize_vip(1280, 720, bg_vip)
        bg_vip = bg_vip.convert('RGBA')
        # alpha_composite才能处理透明的png。参数1是底图，参数2是需要粘贴的图片
        bg_vip = Image.alpha_composite(bg_vip, bg_main_169)
        #else:  #使用缓存好的vip图片
        #bg_vip = Image.open(vip_bg_path)
        bg = copy.deepcopy(bg_vip)  # 两种情况都需要把vip图片加载到bg中
    else:  # vip用户但是出现了空list，调用默认的16比9图片
        bg = copy.deepcopy(bg_main_vip)
    #开始画图
    x = 50
    y = 100
    ran = random.randint(1, 9999)
    global shop_img_temp_vip
    shop_img_temp_vip[ran] = []
    img_num = 0

    for skinuuid in list_shop:
        img_path = f'./log/img_temp_vip/comp/{skinuuid}.png'
        if skinuuid in weapon_icon_temp_vip:#vip用户需要用的抽屉
            shop_img_temp_vip[ran].append(weapon_icon_temp_vip[skinuuid])
        elif os.path.exists(img_path):
            shop_img_temp_vip[ran].append(Image.open(img_path))
        else:
            th = threading.Thread(target=skin_uuid_to_comp, args=(skinuuid, ran, is_vip))
            th.start()
        await asyncio.sleep(0.8)  #尝试错开网络请求
    while True:
        img_temp = [i for i in shop_img_temp_vip[ran]]
        for i in img_temp:
            shop_img_temp_vip[ran].pop(shop_img_temp_vip[ran].index(i))
            #i.save(f"./t{x}_{y}.png", format='PNG')
            bg = bg_comp(bg, i, x, y)
            if x == 50:
                x += 780
            elif x == 830:
                x = 50
                y += 279
            img_num += 1
        if img_num >= 4:
            break
        await asyncio.sleep(0.2)
    #vip用户写入vp和r点
    play_currency = await fetch_valorant_point(userdict)
    vp = play_currency["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #vp
    rp = play_currency["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]  #R点
    draw = ImageDraw.Draw(bg)
    vp_c = (f"{vp}")  #vp
    draw.text((537, 670), vp_c, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    #rp = 89
    rp_c = (f"{rp}")  #rp
    rp_pos = (710, 670)
    if rp < 100:
        rp_pos = (722, 670)
    draw.text(rp_pos, rp_c, font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf', 20), fill=font_color)
    if ran in shop_img_temp_vip:
        del shop_img_temp_vip[ran]
    #画完图之后直接执行保存
    bg.save(f"./log/img_temp_vip/shop/{user_id}.png", format='PNG')
    return {"status": True, "value": bg}


# 获取每日商店的命令
@bot.command(name='shop', aliases=['SHOP'])
async def get_daily_shop(msg: Message, *arg):
    logging(msg)
    if arg != ():
        await msg.reply(f"`/shop`命令不需要参数。您是否想`/login`？")
        return
    send_msg = None
    try:
        if msg.author_id in UserAuthDict:
            reau = await check_re_auth("每日商店", msg)
            if reau == False: return  #如果为假说明重新登录失败
            # 重新获取token成功了再提示正在获取商店
            cm = CardMessage()  #卡片侧边栏颜色
            text = "正在尝试获取您的每日商店"
            c = Card(color='#fb4b57')
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.duck, size='sm')))
            c.append(Module.Context(Element.Text("阿狸正在施法，很快就好啦！", Types.Text.KMD)))
            cm.append(c)
            if isinstance(reau, dict):  #如果传过来的是一个dict，说明重新登录成功且发送了消息
                await upd_card(reau['msg_id'], cm, channel_type=msg.channel_type)
                send_msg = reau
            else:
                send_msg = await msg.reply(cm)  #记录消息id用于后续更新

            #计算获取每日商店要多久
            start = time.perf_counter()  #开始计时
            #从auth的dict中获取对象
            auth = UserAuthDict[msg.author_id]
            userdict = {
                'auth_user_id': auth.user_id,
                'access_token': auth.access_token,
                'entitlements_token': auth.entitlements_token
            }
            log_time = ""
            global UserShopDict
            if msg.author_id in UserShopDict and isSame_Authuuid(msg):
                a_time = time.time()
                list_shop = UserShopDict[msg.author_id]["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
                timeout = shop_time_remain()
                log_time += f"[Dict_shop] {format(time.time()-a_time,'.4f')} "
            else:
                a_time = time.time()
                resp = await fetch_daily_shop(userdict)  #获取每日商店
                #resp = {"SkinsPanelLayout":{"SingleItemOffers":["4875e120-4d7d-aa2a-71c5-c0851c4af00d","5ac106cd-45ef-a26f-2058-f382f20c64db","c7695ce7-4fc9-1c79-64b3-8c8f9e21571c","f35f6e13-4b7b-da38-c0de-5c91fffd584b"],"SingleItemOffersRemainingDurationInSeconds":60193}}#用于测试的假返回值（阴间皮肤）
                list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
                timeout = resp["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]  #剩余时间
                timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  #将秒数转为标准时间
                #需要设置uuid来保证是同一个用户
                UserShopDict[msg.author_id] = {}
                UserShopDict[msg.author_id]["auth_user_id"] = UserTokenDict[msg.author_id]["auth_user_id"]
                UserShopDict[msg.author_id]["SkinsPanelLayout"] = resp["SkinsPanelLayout"]
                log_time += f"[Api_shop] {format(time.time()-a_time,'.4f')} "

            #开始画图
            draw_time = time.time()  #计算画图需要的时间
            is_vip = await vip_ck(msg.author_id) #判断VIP
            #每天8点bot遍历完之后会把vip的商店完整图存起来
            shop_path = f"./log/img_temp_vip/shop/{msg.author_id}.png"
            #用户在列表中，且状态码为true
            is_latest = (msg.author_id in VipShopBgDict and VipShopBgDict[msg.author_id]['status'])
            if is_vip and (os.path.exists(shop_path)) and is_latest:  #如果是vip而且path存在,背景图没有更改过
                bg_vip_shop = Image.open(shop_path)
                bg = copy.deepcopy(bg_vip_shop)
            elif is_vip and (msg.author_id in VipShopBgDict):  #商店路径不存在，或者状态码为false
                ret = await get_daily_shop_vip_img(list_shop, userdict, msg.author_id, is_vip, msg)
                if ret['status']:
                    bg = ret['value']  #获取图片
                else:  #出现图片违规
                    await msg.reply(ret['value'])
                    return
            else:  #普通用户，没有自定义图片的vip用户
                x = 0
                y = 0
                bg = copy.deepcopy(bg_main)
                ran = random.randint(1, 9999)#生成随机数
                # 开始后续画图操作
                global shop_img_temp
                shop_img_temp[ran] = []
                img_num = 0
                # 插入皮肤图片
                for skinuuid in list_shop:
                    img_path = f'./log/img_temp/comp/{skinuuid}.png'
                    if skinuuid in weapon_icon_temp:#普通用户需要用的抽屉
                        shop_img_temp[ran].append(weapon_icon_temp[skinuuid])
                    elif os.path.exists(img_path):
                        shop_img_temp[ran].append(Image.open(img_path))
                    else:
                        th = threading.Thread(target=skin_uuid_to_comp, args=(skinuuid, ran, False))
                        th.start()
                    await asyncio.sleep(0.8)  #尝试错开网络请求
                while True:
                    img_temp = copy.deepcopy(shop_img_temp)
                    for i in img_temp[ran]:
                        shop_img_temp[ran].pop(shop_img_temp[ran].index(i))
                        bg = bg_comp(bg, i, x, y)
                        if x == 0:
                            x += standard_length_sm
                        elif x == standard_length_sm:
                            x = 0
                            y += standard_length_sm
                        img_num += 1
                    if img_num >= 4:
                        break
                    await asyncio.sleep(0.2)
                #循环结束后删除
                if ran in shop_img_temp:
                    del shop_img_temp[ran]

            # 打印画图耗时
            log_time += f"- [Drawing] {format(time.time() - draw_time,'.4f')}"
            print(log_time)
            # bg.save(f"test.png")  #保存到本地
            imgByteArr = io.BytesIO()
            bg.save(imgByteArr, format='PNG')
            imgByte = imgByteArr.getvalue()
            dailyshop_img_src = await bot_upimg.client.create_asset(imgByte)  # 上传图片
            # 结束shop的总计时
            end = time.perf_counter()
            #结果为浮点数，保留两位小数
            using_time = format(end - start, '.2f')
            
            cm = CardMessage()
            c = Card(color='#fb4b57')
            c.append(
                Module.Header(
                    f"玩家 {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']} 的每日商店！"))
            c.append(Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {using_time}s"))
            c.append(Module.Container(Element.Image(src=dailyshop_img_src)))
            cm.append(c)
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            print(f"[{GetTime()}] Au:{msg.author_id} daily_shop reply successful [{using_time}]")
        else:
            cm = CardMessage()
            text = "您尚未登陆！请「私聊」使用login命令进行登录操作\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.whats_that, size='sm')))
            c.append(Module.Context(Element.Text("「/login 账户 密码」请确认您知晓这是一个风险操作", Types.Text.KMD)))
            cm.append(c)
            await msg.reply(cm)
            return
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] shop\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(color='#fb4b57')
        if "SkinsPanelLayout" in str(result):
            text = f"键值错误，需要重新登录"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.lagging, size='sm')))
            c.append(Module.Context(Element.Text(f"KeyError:{result}, please re-login", Types.Text.KMD)))
            cm2.append(c)
            await upd_card(send_msg['msg_id'], cm2, channel_type=msg.channel_type)
        else:
            c.append(Module.Header(f"很抱歉，发生了一些错误"))
            c.append(Module.Divider())
            c.append(Module.Section(Element.Text(f"{err_str}\n\n您可能需要重新执行/login操作", Types.Text.KMD)))
            c.append(Module.Divider())
            c.append(
                Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
            cm2.append(c)
            if send_msg != None:  # 非none则执行更新消息，而不是直接发送
                await upd_card(send_msg['msg_id'], cm2, channel_type=msg.channel_type)
            else:
                await msg.reply(cm2)


# 获取vp和r点剩余
async def get_user_vp(msg: Message, userdict, *arg):
    #userdict = UserTokenDict[msg.author_id]
    resp = await fetch_valorant_point(userdict)
    #print(resp)
    vp = resp["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #vp
    rp = resp["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]  #R点
    text = f"(emj)r点(emj)[3986996654014459/X3cT7QzNsu03k03k] RP  {rp}"
    text += "    "
    text += f"(emj)vp(emj)[3986996654014459/qGVLdavCfo03k03k] VP  {vp}\n"
    return text


# 获取玩家卡面(添加point的别名)
@bot.command(name='uinfo', aliases=['point', 'UINFO', 'POINT'])
async def get_user_card(msg: Message, *arg):
    logging(msg)
    if arg != ():
        await msg.reply(f"`/uinfo`命令不需要参数。您是否想`/login`？")
        return

    try:
        if msg.author_id in UserAuthDict:
            reau = await check_re_auth("玩家装备/通行证", msg)  #重新登录
            if reau == False: return  #如果为假说明重新登录失败

            cm = CardMessage()
            text = "正在尝试获取您的 玩家卡面/VP/R点"
            c = Card(color='#fb4b57')
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.rgx_card, size='sm')))
            c.append(Module.Context(Element.Text("阿狸正在施法，很快就好啦！", Types.Text.KMD)))
            cm.append(c)
            if isinstance(reau, dict):  #如果传过来的是一个dict，说明重新登录成功且发送了消息
                await upd_card(reau['msg_id'], cm, channel_type=msg.channel_type)
                send_msg = reau
            else:
                send_msg = await msg.reply(cm)  #记录消息id用于后续更新

            auth = UserAuthDict[msg.author_id]
            userdict = {
                'auth_user_id': auth.user_id,
                'access_token': auth.access_token,
                'entitlements_token': auth.entitlements_token
            }
            resp = await fetch_player_loadout(userdict)  #获取玩家装备栏
            #print(resp)
            player_card = await fetch_playercard_uuid(resp['Identity']['PlayerCardID'])  #玩家卡面id
            player_title = await fetch_title_uuid(resp['Identity']['PlayerTitleID'])  #玩家称号id
            if resp['Guns'] == None or resp['Sprays'] == None:  #可能遇到全新账户（没打过游戏）的情况
                cm = CardMessage()
                text = f"状态错误！您是否登录了一个全新账户？"
                c = Card(color='#fb4b57')
                c.append(
                    Module.Section(Element.Text(text, Types.Text.KMD),
                                   Element.Image(src=icon_cm.say_hello_to_camera, size='sm')))
                c.append(Module.Section(Element.Text(f"card: `{player_card}`\ntitle: `{player_title}`",
                                                     Types.Text.KMD)))
                cm.append(c)
                await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
                return

            cm = CardMessage()
            c = Card(color='#fb4b57')
            c.append(
                Module.Header(
                    f"玩家 {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']} 的个人信息"))
            c.append(Module.Container(Element.Image(src=player_card['data']['wideArt'])))  #将图片插入进去
            text = f"玩家称号：" + player_title['data']['displayName'] + "\n"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
            #cm.append(c)

            #获取玩家的vp和r点剩余
            text = await get_user_vp(msg, userdict)
            c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
            cm.append(c)
            #await msg.reply(cm)
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            print(f"[{GetTime()}] Au:{msg.author_id} uinfo reply successful!")

        else:
            cm = CardMessage()
            text = "您尚未登陆！请「私聊」使用login命令进行登录操作\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.whats_that, size='sm')))
            c.append(Module.Context(Element.Text("「/login 账户 密码」请确认您知晓这是一个风险操作", Types.Text.KMD)))
            cm.append(c)
            await msg.reply(cm)
            return

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] uinfo\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新执行login操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 获取捆绑包信息(无需登录)
@bot.command(name='bundle', aliases=['skin'])
async def get_bundle(msg: Message, *arg):
    logging(msg)
    if arg == ():
        await msg.reply(f"函数参数错误，name: `{arg}`\n")
        return
    try:
        name = " ".join(arg)  # 补全函数名
        name = zhconv.convert(name, 'zh-tw')  #将名字繁体化
        # 不能一来就在武器列表里面找，万一用户输入武器名，那就会把这个武器的所有皮肤都找出来，和该功能的需求不符合
        # bundlelist = await fetch_bundles_all()
        for b in ValBundleList:  #在本地查找
            if name in b['displayName']:
                # 确认在捆绑包里面有这个名字之后，在查找武器（这里不能使用displayName，因为有些捆绑包两个版本的名字不一样）
                weapenlist = await fetch_bundle_weapen_byname(name)
                #print(weapenlist)
                cm = CardMessage()
                c = Card(Module.Section(Element.Text(f"已为您查询到 `{name}` 相关捆绑包", Types.Text.KMD)))
                for b in ValBundleList:
                    if name in b['displayName']:  # 将图片插入 卡片消息
                        c.append(Module.Container(Element.Image(src=b['displayIcon2'])))
                if weapenlist != []:  # 遇到“再来一局”这种旧皮肤捆绑包，找不到武器名字
                    text = "```\n"
                    for w in weapenlist:
                        res_price = fetch_item_price_bylist(w['lv_uuid'])
                        if res_price != None:  # 有可能出现返回值里面找不到这个皮肤的价格的情况，比如冠军套
                            price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
                            #text += f"{w['displayName']} \t- vp {price}\n"
                            text += '%-28s\t- vp%5s\n' % (w['displayName'], price)
                        else:  # 找不到价格就直接插入武器名字
                            text += f"{w['displayName']}\n"

                    text += "```\n"  # print(text)
                    c.append(Module.Section(Element.Text(text, Types.Text.KMD)))  #插入皮肤
                cm.append(c)
                await msg.reply(cm)
                print(f"[{GetTime()}] Au:{msg.author_id} get_bundle reply successful!")
                return

        await msg.reply(f"未能查找到结果，请检查您的皮肤名拼写")
        print(f"[{GetTime()}] Au:{msg.author_id} get_bundle failed! Can't find {name}")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] get_bundle\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        await bot.client.send(debug_ch, err_str)


#用户选择列表
UserStsDict = {}
# 皮肤商店提醒记录
with open("./log/UserSkinNotify.json", 'r', encoding='utf-8') as frsi:
    SkinNotifyDict = json.load(frsi)


#独立函数，为了封装成命令+定时
async def auto_skin_notify():
    try:
        print("[BOT.TASK] auto_skin_notify Starting!")  #开始的时候打印一下
        #加载vip用户列表
        with open("./log/VipUser.json", 'r', encoding='utf-8') as frau:
            VipUserD = json.load(frau)
        #先遍历vip用户列表，获取vip用户的商店
        for vip, uinfo in VipUserD.items():
            try:
                user = await bot.client.fetch_user(vip)
                if vip in UserAuthDict:
                    if await check_re_auth("定时获取玩家商店", vip) == True:  # 重新登录,如果为假说明重新登录失败
                        start = time.perf_counter()  #开始计时
                        auth = UserAuthDict[vip]
                        userdict = {
                            'auth_user_id': auth.user_id,
                            'access_token': auth.access_token,
                            'entitlements_token': auth.entitlements_token
                        }
                        a_time = time.time()
                        resp = await fetch_daily_shop(userdict)  # 获取每日商店
                        list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
                        timeout = resp["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]  #剩余时间
                        timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  #将秒数转为标准时间
                        log_time = f"[Api_shop] {format(time.time()-a_time,'.4f')} "
                        #vip用户会提前缓存当日商店，需要设置uuid来保证是同一个游戏用户
                        global UserShopDict
                        UserShopDict[vip] = {}
                        UserShopDict[vip]["auth_user_id"] = UserTokenDict[vip]["auth_user_id"]
                        UserShopDict[vip]["SkinsPanelLayout"] = resp["SkinsPanelLayout"]
                        #直接获取商店图片
                        draw_time = time.time()  #计算画图需要的时间
                        bg_shop_ret = await get_daily_shop_vip_img(list_shop, userdict, vip, True)
                        if bg_shop_ret['status']:
                            bg_shop = bg_shop_ret['value']
                        else:  #如果图片没有正常返回，那就发送文字版本
                            text = ""
                            for skinuuid in list_shop:
                                res_item = fetch_skin_bylist(skinuuid)  # 从本地文件中查找
                                res_price = fetch_item_price_bylist(skinuuid)  # 在本地文件中查找
                                price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
                                text += f"{res_item['data']['displayName']}     - VP {price}\n"
                            cm = CardMessage()  #向用户发送当前的每日商店（文字）
                            c = Card(color='#fb4b57')
                            c.append(
                                Module.Section(Element.Text(f"早上好呀！请查收您的每日商店", Types.Text.KMD),
                                               Element.Image(src=icon_cm.shot_on_fire, size='sm')))
                            c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
                            c.append(Module.Context(Element.Text(f"这里有没有你想要的枪皮呢？", Types.Text.KMD)))
                            cm.append(c)
                            await user.send(cm)
                            continue

                        log_time += f"- [Drawing] {format(time.time() - draw_time,'.4f')}"
                        print(log_time)
                        img_shop = f"./log/img_temp_vip/shop/{vip}.png"
                        #bg_shop.save(img_shop, format='PNG')
                        dailyshop_img_src = await bot_upimg.client.create_asset(img_shop)  # 上传图片
                        # 结束shop的总计时
                        end = time.perf_counter()
                        #结果为浮点数，保留两位小数
                        using_time = format(end - start, '.2f')
                        #卡片消息发送图片
                        cm = CardMessage()
                        c = Card(color='#fb4b57')
                        c.append(
                            Module.Header(
                                f"早安！玩家 {UserTokenDict[vip]['GameName']}#{UserTokenDict[vip]['TagLine']} 的每日商店"))
                        c.append(Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {using_time}s"))
                        c.append(Module.Container(Element.Image(src=dailyshop_img_src)))
                        cm.append(c)
                        await user.send(cm)
                        print(f"[{GetTime()}] Au:{vip} notify_daily_shop successful [{using_time}]")
                    else:  #reauthorize failed!
                        print(f"[BOT.TASK] Vip_Au:{vip} user reauthorize failed")
                        await user.send(f"尊贵的vip用户，您已登录，但是登录信息失效了。请您重新`login`以查询每日商店\n注：这是无可避免的小概率事件")
                else:  #不在auth里面说明没有登录
                    print(f"[BOT.TASK] Vip_Au:{vip} user_not_in UserAuthDict")
                    await user.send(f"尊贵的vip用户，请您`login`来让每日商店提醒生效哦~")
            except Exception as result:  #这个是用来获取单个用户的问题的
                err_str = f"ERR![BOT.TASK] auto_skin_notify Au:{vip} vip_user.send\n```\n{traceback.format_exc()}\n```"
                print(err_str)
                await bot.client.send(debug_ch, err_str)  #发送消息到debug频道

        # 再遍历所有用户的皮肤提醒
        for aid, skin in SkinNotifyDict.items():
            try:
                user = await bot.client.fetch_user(aid)
                if aid in UserAuthDict:
                    if await check_re_auth("定时获取玩家商店", aid) == True:  # 重新登录,如果为假说明重新登录失败
                        auth = UserAuthDict[aid]
                        userdict = {
                            'auth_user_id': auth.user_id,
                            'access_token': auth.access_token,
                            'entitlements_token': auth.entitlements_token
                        }
                        #vip用户在前面已经获取过商店了
                        if await vip_ck(aid):
                            list_shop = UserShopDict[aid]["SkinsPanelLayout"]["SingleItemOffers"]
                        else:
                            resp = await fetch_daily_shop(userdict)  # 获取每日商店
                            list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪

                        # 然后再遍历列表查看是否有提醒皮肤
                        # 关于下面这一行参考 https://img.kookapp.cn/assets/2022-08/oYbf8PM6Z70ae04s.png
                        target_skin = [val for key, val in skin.items() if key in list_shop]
                        # print(target_skin)
                        for name in target_skin:
                            print(f"[BOT.TASK] Au:{aid} auto_skin_notify = {name}")
                            await user.send(f"[{GetTime()}] 您的每日商店刷出`{name}`了，请上号查看哦！")
                        # 打印这个说明这个用户正常遍历完了
                        print(f"[BOT.TASK] Au:{aid} auto_skin_notify = None")
                    else:  #reauthorize failed!
                        print(f"[BOT.TASK] Vip_Au:{vip} user reauthorize failed")
                        await user.send(f"您已登录，但是登录信息失效了。请您重新`login`以查询每日商店\n注：这是无可避免的小概率事件")
                else:  #不在auth里面说明没有登录
                    print(f"[BOT.TASK] Au:{aid} user_not_in UserAuthDict")
                    await user.send(
                        f"您设置了皮肤提醒，却没有登录！请尽快`login`哦~\n悄悄话: 阿狸会保存vip用户的登录信息，有兴趣[支持一下](https://afdian.net/a/128ahri?tab=shop)吗？"
                    )
            except Exception as result:  #这个是用来获取单个用户的问题的
                err_str = f"ERR![BOT.TASK] auto_skin_notify Au:{vip} user.send\n```\n{traceback.format_exc()}\n```"
                print(err_str)
                await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道

        #完成遍历后打印
        finish_str = "[BOT.TASK] auto_skin_notify Finished!"
        print(finish_str)  #正常完成
        await bot.client.send(debug_ch, finish_str)  #发送消息到debug频道
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] auto_skin_notify\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道


@bot.task.add_cron(hour=8, minute=1, timezone="Asia/Shanghai")
async def auto_skin_notify_task():
    await auto_skin_notify()


@bot.command(name='notify-test')
async def auto_skin_notify_cmd(msg: Message, *arg):
    logging(msg)
    if msg.author_id == master_id:
        await auto_skin_notify()
    else:
        await msg.reply("您没有权限执行此命令")


#设置提醒（出现xx皮肤）
@bot.command(name="notify-add", aliases=['notify-a'])
async def add_skin_notify(msg: Message, *arg):
    logging(msg)
    if arg == ():
        await msg.reply(f"你没有提供皮肤参数！skin: `{arg}`")
        return
    try:
        # 检查用户的提醒栏位（经过测试已经可以用，等vip处理代码写好后再开放）
        vip_status = await vip_ck(msg.author_id)
        if msg.author_id in SkinNotifyDict and not vip_status:
            if len(SkinNotifyDict[msg.author_id]) > 2:
                cm = CardMessage()
                c = Card(color='#fb4b57')
                c.append(
                    Module.Section(Element.Text(f"您的皮肤提醒栏位已满", Types.Text.KMD),
                                   Element.Image(src=icon_cm.rgx_broken, size='sm')))
                c.append(
                    Module.Context(
                        Element.Text(f"想解锁更多栏位，可以来[支持一下](https://afdian.net/a/128ahri?tab=shop)阿狸呢！", Types.Text.KMD)))
                cm.append(c)
                await msg.reply(cm)
                return

        #用户没有登录
        if msg.author_id not in UserAuthDict:
            cm = CardMessage()
            text = "您尚未登陆！请「私聊」使用login命令进行登录操作\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.whats_that, size='sm')))
            c.append(Module.Context(Element.Text("「/login 账户 密码」请确认您知晓这是一个风险操作\n设置了皮肤提醒之后，请勿切换已登录的账户", Types.Text.KMD)))
            cm.append(c)
            await msg.reply(cm)
            return

        name = " ".join(arg)
        name = zhconv.convert(name, 'zh-tw')  #将名字繁体化
        sklist = fetch_skin_byname_list(name)
        if sklist == []:  #空list代表这个皮肤不在里面
            await msg.reply(f"该皮肤不在列表中，请重新查询！")
            return

        retlist = list()  #用于返回的list，因为不是所有搜到的皮肤都有价格，没有价格的皮肤就是商店不刷的
        for s in sklist:
            res_price = fetch_item_price_bylist(s['lv_uuid'])
            if res_price != None:  # 有可能出现返回值里面找不到这个皮肤的价格的情况，比如冠军套
                price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
                data = {'skin': s, 'price': price}
                retlist.append(data)

        if retlist == []:  #空list代表这个皮肤没有价格
            await msg.reply(f"该皮肤不在列表中 [没有价格]，请重新查询！")
            return

        UserStsDict[msg.author_id] = retlist
        i = 0
        text = "```\n"  #模拟一个选择表
        for w in retlist:
            text += f"[{i}] - {w['skin']['displayName']}  - VP {w['price']}\n"
            i += 1
        text += "```"
        cm = CardMessage()
        c = Card(Module.Header(f"查询到 {name} 相关皮肤如下"),
                 Module.Context(Element.Text("请在下方键入序号进行选择，请不要选择已购买的皮肤", Types.Text.KMD)),
                 Module.Section(Element.Text(text + "\n\n使用 `/sts 序号` 来选择", Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] addskin\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新执行login操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


#选择皮肤（这个命令必须跟着上面的命令用）
@bot.command(name="sts")
async def select_skin_notify(msg: Message, n: str = "err", *arg):
    logging(msg)
    if n == "err" or '-' in n:
        await msg.reply(f"参数不正确！请选择您需要提醒的皮肤序号")
        return
    try:
        global SkinNotifyDict
        if msg.author_id in UserStsDict:
            num = str2int(n)  #转成int下标（不能处理负数）
            if num >= len(UserStsDict[msg.author_id]):  #下标判断，避免越界
                await msg.reply(f"您的选择越界了！请正确填写序号")
                return

            # 先发送一个私聊消息，作为测试（避免有人开了不给私信）
            user_test = await bot.client.fetch_user(msg.author_id)
            try:
                await user_test.send(f"这是一个私信测试。请不要修改您的私信权限，以免notify功能无法正常使用")
            except requester.HTTPRequester.APIRequestFailed as result:
                err_str = f"ERR! [{GetTime()}] notify-sts Au:{msg.author_id}\n"
                if '屏蔽' in str(result):#如果用户不允许bot私信，则发送提示信息
                    err_str+=f"```\n{result}\n```\nreply to inform user"
                    await msg.reply(f"阿狸无法向您发起私信，请修改您的隐私设置，或者私聊阿狸使用相关命令\n{err_str}")
                else:
                    err_str+=f"```\n{traceback.format_exc()}\n```\n"
                    await msg.reply(err_str)
                #发送信息到日志频道
                await bot.client.send(debug_ch, err_str)
                print(err_str)
                return

            S_skin = UserStsDict[msg.author_id][num]
            if msg.author_id not in SkinNotifyDict:
                SkinNotifyDict[msg.author_id] = {}
                SkinNotifyDict[msg.author_id][S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            else:  #如果存在了就直接在后面添加
                SkinNotifyDict[msg.author_id][S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            # print(SkinNotifyDict[msg.author_id])

            # 写入文件
            with open("./log/UserSkinNotify.json", 'w', encoding='utf-8') as fw2:
                json.dump(SkinNotifyDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

            del UserStsDict[msg.author_id]  #删除选择页面中的list
            text = f"设置成功！已开启`{S_skin['skin']['displayName']}`的提醒"
            # 设置成功并删除list后，再发送提醒事项设置成功的消息
            await msg.reply(text)
            print(f"[sts] Au:{msg.author_id} ", text)
        else:
            await msg.reply(f"您需要（重新）执行 `/notify-a` 来设置提醒皮肤")
    except requester.HTTPRequester.APIRequestFailed as result:
        err_str = f"ERR! [{GetTime()}] select_skin_inform\n```\n{result}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您是否开启了不允许私信？请检查您的私信权限设置\n这会影响notify功能的使用", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] select_skin_inform\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(Module.Section(Element.Text(f"{err_str}\n您可能需要重新执行操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系', Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                                                     Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 显示当前设置好了的皮肤通知
@bot.command(name="notify-list", aliases=['notify-l'])
async def list_skin_notify(msg: Message, *arg):
    logging(msg)
    try:
        if msg.author_id in SkinNotifyDict:
            text = "```\n"
            for skin, name in SkinNotifyDict[msg.author_id].items():
                text += skin + ' = ' + name + '\n'
            text += "```\n"
            text += "如果您需要添加皮肤，请使用`notify-a 皮肤名`\n"
            text += "如果您需要删除皮肤，请使用`notify-d uuid`\n"
            text += "注：`=`号前面很长的那一串就是uuid\n"
            await msg.reply(text)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] notify-list\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        await bot.client.send(debug_ch, err_str)


# 删除已有皮肤通知
@bot.command(name="notify-del", aliases=['notify-d'])
async def delete_skin_notify(msg: Message, uuid: str = "err", *arg):
    logging(msg)
    if uuid == 'err':
        await msg.reply(f"请提供正确的皮肤uuid：`{uuid}`")
        return
    try:
        global SkinNotifyDict
        if msg.author_id in SkinNotifyDict:
            if uuid in SkinNotifyDict[msg.author_id]:
                print(f"notify-d - Au:{msg.author_id} = {uuid} {SkinNotifyDict[msg.author_id][uuid]}")
                await msg.reply(f"已删除皮肤：`{SkinNotifyDict[msg.author_id][uuid]}`")
                del SkinNotifyDict[msg.author_id][uuid]
                # 写入文件
                with open("./log/UserSkinNotify.json", 'w', encoding='utf-8') as fw2:
                    json.dump(SkinNotifyDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
            else:
                await msg.reply(f"您提供的uuid不在列表中！")
                return
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] notify-del\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        await bot.client.send(debug_ch, err_str)


#当出现某些问题的时候，通知人员
@bot.command(name="inform-user")
async def inform_user(msg:Message,channel:str,user:str):
    logging(msg)
    if msg.author_id != master_id:
        await msg.reply(f"您没有权限执行此命令！")
        return
    try:
        au = await bot.client.fetch_user(user)
        text=f"以下信息来自开发者:\n用户 (met){user}(met) {au.username}#{au.identify_num}，您开启了`皮肤提醒功能`却没有允许阿狸私信您\nkook直接搜用户名搜不到人+您所在服务器没有开公开id无法直接加入，以至于我只能让阿狸在你们服务器发一个消息来提醒您。如果对服务器其他成员有所叨扰，还请海涵。"
        ch=await bot.client.fetch_public_channel(channel)
        await bot.client.send(ch,text)
        log_str=f"[inform-user] bot send to C:{channel} Au:{user}"
        await msg.reply(log_str)
        print(log_str)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] inform-user\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
    

# 开机的时候打印一次时间，记录重启时间
print(f"Start at: [%s]" % start_time)

#bot.run()是机器人的起跑线
bot.run()
