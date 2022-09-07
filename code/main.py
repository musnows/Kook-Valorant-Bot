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
from khl import (Bot, Client, Event, EventTypes, Message,
                 PrivateMessage, PublicChannel, PublicMessage)
from khl.card import Card, CardMessage, Element, Module, Types
from khl.command import Rule

from upd_msg import icon, upd_card

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])

Botoken = config['token']
kook = "https://www.kookapp.cn"
headers = {f'Authorization': f"Bot {Botoken}"}

# 设置全局变量：机器人开发者id/报错频道
master_id = '1961572535'
Debug_ch = '6248953582412867'


# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api = "http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid': 'a87ebe9c-1319-4394-9704-0ad2c70e2567'}
    # r = requests.post(api,headers=headers)
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)


##########################################################################################
##########################################################################################


def GetTime():  #将获取当前时间封装成函数方便使用
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())


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
@bot.command(name='Ahri', aliases=['阿狸'])
async def Ahri(msg: Message, *arg):
    logging(msg)
    try:
        # msg 触发指令为 `/Ahri`,因为help指令和其他机器人冲突
        cm = CardMessage()
        c3 = Card(
            Module.Header('你可以用下面这些指令呼叫本狸哦！'),
            Module.Context(
                Element.Text(
                    "开源代码见[Github](https://github.com/Aewait/Valorant-Kook-Bot)，更多玩耍方式上线中...",
                    Types.Text.KMD)))
        #c3.append(Module.Section(Element.Text('用`/hello`来和阿狸打个招呼吧！',Types.Text.KMD))) #实现卡片的markdown文本
        c3.append(Module.Section('「/hello」来和本狸打个招呼吧！\n「/Ahri」 帮助指令\n'))
        c3.append(Module.Divider())
        c3.append(Module.Header('上号，瓦一把！'))
        c3.append(
            Module.Section(
                Element.Text(
                    "「/val 错误码」 游戏错误码的解决方法，0为已包含的val报错码信息\n「/dx」 关于DirectX Runtime报错的解决方案\n「/saveid 游戏id」 保存(修改)您的游戏id\n「/myid」 让阿狸说出您的游戏id\n「`/vhelp`」瓦洛兰特游戏查询相关功能的帮助",
                    Types.Text.KMD)))
        c3.append(Module.Divider())
        c3.append(Module.Header('和阿狸玩小游戏吧~ '))
        c3.append(
            Module.Section(
                '「/roll 1 100」掷骰子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个骰子\n「/countdown 秒数」倒计时，默认60秒\n「/TL 内容」翻译内容，支持多语译中和中译英\n「/TLON」 在本频道打开实时翻译\n「/TLOFF」在本频道关闭实时翻译\n「/we 城市」查询城市未来3天的天气情况\n「更多…」还有一些隐藏指令哦~\n'
            ))
        c3.append(Module.Divider())
        c3.append(
            Module.Section(
                ' 游戏打累了？想来本狸的家坐坐吗~',
                Element.Button('让我康康', 'https://kook.top/gpbTwZ',
                               Types.Click.LINK)))
        cm.append(c3)

        await msg.reply(cm)

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] Ahri - {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(debug_channel, err_str)


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
                Element.Text(
                    "开源代码见[Github](https://github.com/Aewait/Valorant-Kook-Bot)，更多查询功能上线中...",
                    Types.Text.KMD)))
        c3.append(
            Module.Section(
                Element.Text(
                    "使用前，请确认您知晓相关功能可能有风险：\n1.阿狸的后台不会做任何`打印/保存`您的游戏账户密码的操作，若在使用相关功能后被盗号，阿狸可不承担任何责任;\n2.目前查询功能稳定性未知，可能有`封号`风险，建议使用小号测试;\n若担心相关风险，请不要使用如下功能\n",
                    Types.Text.KMD)))
        c3.append(Module.Divider())
        help_1 = "「/bundle 皮肤名」 查询皮肤系列包含什么枪械\n"
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
        c3.append(
            Module.Section(
                '若有任何问题，欢迎加入帮助频道',
                Element.Button('来狸', 'https://kook.top/gpbTwZ',
                               Types.Click.LINK)))
        cm.append(c3)
        await msg.reply(cm)

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] vhelp - {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(debug_channel, err_str)


#################################################################################################
#################################################################################################


# 倒计时函数，单位为秒，默认60秒
@bot.command()
async def countdown(msg: Message, time: int = 60):
    logging(msg)
    try:
        cm = CardMessage()
        c1 = Card(Module.Header('本狸帮你按下秒表喽~'),
                  color=(198, 65,
                         55))  # color=(90,59,215) is another available form
        c1.append(Module.Divider())
        c1.append(
            Module.Countdown(datetime.now() + timedelta(seconds=time),
                             mode=Types.CountdownMode.SECOND))
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] countdown\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(debug_channel, err_str)


# 掷骰子 saying `!roll 1 100` in channel,or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int = 1, t_max: int = 100, n: int = 1):
    logging(msg)
    try:
        result = [random.randint(t_min, t_max) for i in range(n)]
        await msg.reply(f'掷出来啦: {result}')
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] roll\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(debug_channel, err_str)


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
        json.dump(ColorIdDict,
                  fw2,
                  indent=2,
                  sort_keys=True,
                  ensure_ascii=False)

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
        print(f"[{now_time}] React:{event.body}"
              )  # 这里的打印eventbody的完整内容，包含emoji_id

        channel = await bot.client.fetch_public_channel(event.body['channel_id'])  #获取事件频道
        s = await bot.client.fetch_user(event.body['user_id'])  #通过event获取用户id(对象)
        # 判断用户回复的emoji是否合法
        emoji = event.body["emoji"]['id']
        flag = 0
        for line in EmojiLines:
            v = line.strip().split(':')
            if emoji == v[0]:
                flag = 1  #确认用户回复的emoji合法
                ret = save_userid_color(
                    event.body['user_id'],
                    event.body["emoji"]['id'])  # 判断用户之前是否已经获取过角色
                if ret == 1:  #已经获取过角色
                    await b.client.send(channel,
                                 f'你已经设置过你的ID颜色啦！修改要去找管理员哦~',
                                 temp_target_id=event.body['user_id'])
                    return
                else:
                    role = int(v[1])
                    await g.grant_role(s, role)
                    await b.client.send(channel,
                                 f'阿狸已经给你上了 {emoji} 对应的颜色啦~',
                                 temp_target_id=event.body['user_id'])

        if flag == 0:  #回复的表情不合法
            await b.client.send(channel,
                         f'你回应的表情不在列表中哦~再试一次吧！',
                         temp_target_id=event.body['user_id'])


# 给用户上色（在发出消息后，机器人自动添加回应）
@bot.command()
async def Color_Set(msg: Message):
    logging(msg)
    if msg.author_id != master_id:
        await msg.reply("您没有权限执行这条命令！")
        return
    cm = CardMessage()
    c1 = Card(Module.Header('在下面添加回应，来设置你的id颜色吧！'),
              Module.Context('五颜六色等待上线...'))
    c1.append(Module.Divider())
    c1.append(
        Module.Section(
            '「:pig:」粉色  「:heart:」红色\n「:black_heart:」黑色  「:yellow_heart:」黄色\n'))
    c1.append(
        Module.Section(
            '「:blue_heart:」蓝色  「:purple_heart:」紫色\n「:green_heart:」绿色  「:+1:」默认\n'
        ))
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
        json.dump(SponsorDict,
                  fw2,
                  indent=2,
                  sort_keys=True,
                  ensure_ascii=False)

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
            channel = await bot.client.fetch_public_channel("8342620158040885"
                                                     )  #发送感谢信息的文字频道
            await bot.client.send(channel, f"感谢 (met){its['id']}(met) 对本服务器的助力")
            print(f"[%s] 感谢{its['nickname']}对本服务器的助力" % GetTime())


######################################## Translate ################################################

from translate import caiyun_translate, is_CN, youdao_translate


# 单独处理met和rol消息，不翻译这部分内容
def deleteByStartAndEnd(s, start, end):
    # 找出两个字符串在原始字符串中的位置
    # 开始位置是：开始始字符串的最左边第一个位置；
    # 结束位置是：结束字符串的最右边的第一个位置
    while s.find(start) != -1:
        x1 = s.find(start)
        x2 = s.find(end, x1 + 5) + len(
            end)  # s.index()函数算出来的是字符串的最左边的第一个位置，所以需要加上长度找到末尾
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
        c1 = Card(
            Module.Section(
                Element.Text(f"**翻译结果(Result):** {youdao_translate(word)}",
                             Types.Text.KMD)), Module.Context('来自: 有道翻译'))
        cm.append(c1)
        #await msg.ctx.channel.send(cm)
        await msg.reply(cm)
    except:
        cm = CardMessage()
        if is_CN(word):
            c1 = Card(
                Module.Section(
                    Element.Text(
                        f"**翻译结果(Result):** {await caiyun_translate(word,'auto2en')}",
                        Types.Text.KMD)), Module.Context('来自: 彩云小译，中译英'))
        else:
            c1 = Card(
                Module.Section(
                    Element.Text(
                        f"**翻译结果(Result):** {await caiyun_translate(word,'auto2zh')}",
                        Types.Text.KMD)), Module.Context('来自: 彩云小译，英译中'))

        cm.append(c1)
        await msg.reply(cm)


# 普通翻译指令
@bot.command(name='TL', aliases=['tl'])
async def translate1(msg: Message, *arg):
    logging(msg)
    await translate(msg, ' '.join(arg))


# 实时翻译栏位
ListTL = ['0', '0', '0', '0']


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
    await msg.reply(
        f"Real-Time Translation ON\n阿狸现在会实时翻译本频道的对话啦！\n目前栏位: {ret}/{len(ListTL)}，使用`/TLOFF`可关闭实时翻译哦~"
    )


# 关闭实时翻译功能
@bot.command(name='TLOFF', aliases=['tloff'])
async def TLOFF(msg: Message):
    logging(msg)
    global ListTL
    i = 0
    while i < len(ListTL):
        if ListTL[i] == msg.ctx.channel.id:
            ListTL[i] = '0'
            await msg.reply(
                f"Real-Time Translation OFF！目前栏位: {checkTL()}/{len(ListTL)}")
            return
        i += 1
    await msg.reply(f"本频道并没有开启实时翻译功能！目前栏位: {checkTL()}/{len(ListTL)}")


######################################## Other ################################################

from other import history, weather


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
    c1 = Card(Module.Header('在下面添加回应，来设置你的段位吧！'),
              Module.Context('段位更改功能等待上线...'))
    c1.append(
        Module.Section(
            '「:question:」黑铁 「:eyes:」青铜\n「:sweat_drops:」白银 「:yellow_heart:」黄金\n'
        ))
    c1.append(
        Module.Section(
            '「:blue_heart:」铂金 「:purple_heart:」钻石\n「:green_heart:」翡翠 「:heart:」神话\n'
        ))
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
        '本狸才不喜欢`又硬又细`的人呢~\n[https://s1.ax1x.com/2022/06/24/jFGjHA.png](https://s1.ax1x.com/2022/06/24/jFGjHA.png)'
    )


###########################################################################################
####################################以下是游戏相关代码区#####################################
###########################################################################################

from status import (server_status, status_active_game, status_active_music,
                    status_delete)
from val import (authflow, dx123, fetch_buddies_uuid,
                 fetch_bundle_weapen_byname, fetch_bundles_all,
                 fetch_contract_uuid, fetch_daily_shop, fetch_item_iters,
                 fetch_item_price_all, fetch_item_price_uuid,
                 fetch_player_contract, fetch_player_loadout,
                 fetch_playercard_uuid, fetch_skinlevel_uuid, fetch_skins_all,
                 fetch_spary_uuid, fetch_title_uuid, fetch_user_gameID,
                 fetch_valorant_point, kda123, lead123, myid123, saveid123,
                 saveid_1, saveid_2, skin123, val123)


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
    return reduce(
        lambda x, y: x * 10 + y,
        map(
            lambda s: {
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
from riot_auth import auth_exceptions
import zhconv  # 用于繁体转简体（因为部分字体不支持繁体
from PIL import Image, ImageDraw, ImageFont  # 用于合成图片

standard_length = 1000  #图片默认边长
# 用math.floor 是用来把float转成int 我也不晓得为啥要用 但是不用会报错（我以前不用也不会）
# 所有的数都  * standard_length / 1000 是为了当标准边长变动时这些参数会按照比例缩放
standard_length_sm = int(standard_length / 2)  # 组成四宫格小图的边长
stardard_blank_sm = 60 * standard_length / 1000  # 小图左边的留空
stardard_icon_resize_ratio = 0.59 * standard_length / 1000  # 枪的默认缩放
standard_icon_top_blank = int(180 * standard_length / 1000)  # 枪距离图片顶部的像素
standard_text_position = (int(124 * standard_length / 1000),
                          int(317 * standard_length / 1000))  # 默认文字位置
standard_price_position = (int(280 * standard_length / 1000),
                           int(120 * standard_length / 1000))  # 皮肤价格文字位置
standard_level_icon_reszie_ratio = 0.13 * standard_length / 1000  # 等级icon图标的缩放
standard_level_icon_position = (int(350 * standard_length / 1000),
                                int(120 * standard_length / 1000)
                                )  # 等级icon图标的坐标


async def img_requestor(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as r:
            return await r.read()


font_color = '#ffffff'  # 文字颜色：白色


@bot.task.add_date()
async def fetch_bg():
    global bg_main
    bg_main = Image.open(
        io.BytesIO(await img_requestor(
            'https://img.kookapp.cn/assets/2022-08/WsjGI7PYuf0rs0rs.png'
        )))  # 背景


# 缩放图片，部分皮肤图片大小不正常
def resize(standard_x, img):
    log_info = "[shop] "
    w, h = img.size
    log_info += f"原始图片大小:({w},{h}) - "
    ratio = w / h
    sizeco = w / standard_x
    log_info += f"缩放系数:{format(sizeco,'.3f')} - "
    w_s = int(w / sizeco)
    h_s = int(h / sizeco)
    log_info += f"缩放后大小:({w_s},{h_s})"
    print(log_info)
    img = img.resize((w_s, h_s), Image.Resampling.LANCZOS)
    return img


level_icon_temp = {}
weapon_icon_temp = {}


def sm_comp(icon, name, price, level_icon, skinuuid):
    bg = Image.new(mode='RGBA',
                   size=(standard_length_sm, standard_length_sm))  # 新建一个画布
    # 处理武器图片
    start = time.perf_counter()  #开始计时

    if os.path.exists(f'./log/img_temp/weapon/{skinuuid}.png'):
        layer_icon = Image.open(
            f'./log/img_temp/weapon/{skinuuid}.png')  # 打开武器图片
    else:
        layer_icon = Image.open(io.BytesIO(
            requests.get(icon).content))  # 打开武器图片
        layer_icon.save(f'./log/img_temp/weapon/{skinuuid}.png', format='PNG')
    end = time.perf_counter()
    log_time=f"[GetWeapen] {format(end - start, '.4f')} "
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
    # if level_icon not in level_icon_temp:
    #     if os.path.exists(f'./log/img_temp/level/{level_icon}.png'):
    #         LEVEL_Icon = Image.open(f'./log/img_temp/level/{skinuuid}.png')
    #     else:
    #         LEVEL_Icon = Image.open(io.BytesIO(requests.get(level_icon).content))  # 打开武器图片
    #         LEVEL_Icon.save(f'./log/img_temp/level/{level_icon}',format='PNG')
    #     level_icon_temp[level_icon] = LEVEL_Icon
    # else:
    #     LEVEL_Icon = level_icon_temp[level_icon]
    if level_icon not in level_icon_temp:
        LEVEL_Icon = Image.open(io.BytesIO(
            requests.get(level_icon).content))  # 打开武器图片
        level_icon_temp[level_icon] = LEVEL_Icon
    else:
        LEVEL_Icon = level_icon_temp[level_icon]
    end = time.perf_counter()
    log_time+=f"- [GetIters] {format(end - start, '.4f')} "
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
              font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf',
                                      30),
              fill=font_color)
    text = f"{price}"  # 价格
    draw.text(standard_price_position,
              text,
              font=ImageFont.truetype('./config/SourceHanSansCN-Regular.otf',
                                      30),
              fill=font_color)
    # bg.show() #测试用途，展示图片(linux貌似不可用)
    if not os.path.exists(f'./log/img_temp/comp/{skinuuid}.png'):
        bg.save(f'./log/img_temp/comp/{skinuuid}.png')
    global weapon_icon_temp
    if skinuuid not in weapon_icon_temp:
        weapon_icon_temp[skinuuid] = bg
    return bg


def bg_comp(bg, img, x, y):
    position = (x, y)
    bg.paste(img, position, img)  #如sm—comp中一样，向bg粘贴img
    return bg


shop_img_temp = {}
img_save_temp = {}


def uuid_to_comp(skinuuid, ran):
    res_item = fetch_skin_bylist(skinuuid)  # 从本地文件中查找
    res_price = fetch_item_price_bylist(skinuuid)  # 在本地文件中查找
    price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
    for it in ValSkinList['data']:
        if it['levels'][0]['uuid'] == skinuuid:
            # res_iters = await fetch_item_iters(it['contentTierUuid'])
            res_iters = fetch_item_iters_bylist(it['contentTierUuid'])
            break
    img = sm_comp(res_item["data"]['levels'][0]["displayIcon"],
                  res_item["data"]["displayName"], price,
                  res_iters['data']['displayIcon'], skinuuid)
    global shop_img_temp
    shop_img_temp[ran].append(img)


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

# 用来存放auth对象
UserAuthDict = {}


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
            data = {
                'displayName': skin['displayName'],
                'lv_uuid': skin['levels'][0]['uuid']
            }
            wplist.append(data)
    return wplist


#查询当前有多少用户登录了
@bot.command(name="ckau")
async def check_UserAuthDict_len(msg: Message):
    logging(msg)
    sz = len(UserAuthDict)
    res = f"UserAuthDict_len: `{sz}`"
    print(res)
    await msg.reply(res)



login_dict={}#用于限制用户操作，一分钟只能3次
#全局的速率限制，如果触发了速率限制的err，则阻止所有用户login
login_rate_limit={'limit':False,
                  'time':time.time()} 

#遇到全局速率限制统一获取卡片消息
def get_login_rate_cm(time_diff=None):
    if time_diff != None:
        text = f"阿狸的登录请求超速！请在 {format(240.0-time_diff, '.1f')}s 后重试"
    else:
        text = f"阿狸的登录请求超速！请在 240.0s 后重试"
    cm = CardMessage()
    c = Card(color='#fb4b57')
    c.append(Module.Section(Element.Text(text, Types.Text.KMD),
                        Element.Image(src=icon.lagging, size='sm')))
    c.append(Module.Context(Element.Text("raise RiotRatelimitError, please try again later",Types.Text.KMD)))
    cm.append(c)
    return cm

#检查是否存在用户请求超速
async def check_user_login_rate(msg:Message):
    """
    Returns:
     - True: UserRatelimitError
     - False: good_to_go
    """
    global login_dict #检查用户请求次数，避免超速
    if msg.author_id in login_dict:
        time_stap = time.time()
        time_diff = time_stap - login_dict[msg.author_id]['time']
        if login_dict[msg.author_id]['nums']>=3 and time_diff<=70.0:
            # 思路是第一次请求超速后，要过70s才能执行下一次
            if login_dict[msg.author_id]['nums']==3: #第一次请求超速
                login_dict[msg.author_id]['time'] = time_stap #更新时间戳
                time_diff = 0 #更新diff
            
            login_dict[msg.author_id]['nums'] += 1
            time_remain = format(70.0-time_diff, '.1f')#剩余需要等待的时间
            text = f"用户登录请求超速，请在 {time_remain}s 后重试"
            cm0 = CardMessage()
            c = Card(color='#fb4b57')  #卡片侧边栏颜色
            c.append(Module.Section(Element.Text(text, Types.Text.KMD),
                            Element.Image(src=icon.powder, size='sm')))
            c.append(Module.Context(Element.Text(f"raise UserRatelimitError, please try again after {time_remain}s", Types.Text.KMD)))
            cm0.append(c)
            await msg.reply(cm0)
            return True
        elif time_diff>70.0: #请求次数超限，但是已经过了70s
            login_dict[msg.author_id]['nums'] = 1 #重置为1
            login_dict[msg.author_id]['time'] = time_stap
            return False
        else: # login_dict[msg.author_id]['nums']<3 and time_diff<=60.0
            login_dict[msg.author_id]['nums'] += 1
            return False
    else:
        login_dict[msg.author_id]={'time':time.time(),'nums':1}
        return False


# 登录，保存用户的token
@bot.command(name='login')
async def login_authtoken(msg: Message,
                          user: str = 'err',
                          passwd: str = 'err',
                          *arg):
    print(
        f"[{GetTime()}] Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = /login"
    )
    if passwd == 'err' or user == 'err':
        await msg.reply(
            f"参数不完整，请提供您的账户和密码！\naccout: `{user}` passwd: `{passwd}`")
        return
    elif arg != ():
        await msg.reply(
            f"您给予了多余的参数！\naccout: `{user}` passwd: `{passwd}`\n多余参数: `{arg}`")
        return

    global login_rate_limit
    try:
        cm0 = CardMessage()
        c = Card(color='#fb4b57')  #卡片侧边栏颜色
        global UserTokenDict, UserAuthDict
        if msg.author_id in UserAuthDict:  #用in判断dict是否存在这个键，如果用户id已有，则不进行操作
            text = "您已经登陆，无需重复操作"
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.shaka, size='sm')))
            c.append(
                Module.Context(
                    Element.Text("如需重新登录，请先logout退出当前登录", Types.Text.KMD)))
            cm0.append(c)
            await msg.reply(cm0)
            return
        
        #全局请求超速
        if login_rate_limit['limit']:
            time_stap = time.time()
            time_diff = time_stap - login_rate_limit['time']
            if time_diff <= 240.0: #240s内无法使用login
                ret_cm = get_login_rate_cm(time_diff)
                await msg.reply(ret_cm)
                print(f"Login  - Au:{msg.author_id} - raise global_login_rate_limit")
                return
            else:#超过240s，解除限制
                login_rate_limit['limit'] = False
                login_rate_limit['time'] = time_stap
                
        if await check_user_login_rate(msg):
            print(f"Login  - Au:{msg.author_id} - raise user_login_rate_limit")
            return

        
        text = "正在尝试获取您的riot账户token"
        c.append(
            Module.Section(Element.Text(text, Types.Text.KMD),
                           Element.Image(src=icon.val_logo_gif, size='sm')))
        c.append(Module.Context(Element.Text("小憩一下，很快就好啦！", Types.Text.KMD)))
        cm0.append(c)
        send_msg = await msg.reply(cm0)  #记录消息id用于后续更新

        # 不在其中才进行获取token的操作（耗时)
        res_auth = await authflow(user, passwd)
        UserTokenDict[msg.author_id] = {
            'auth_user_id': res_auth.user_id
        }  #先创建基本信息 dict[键] = 值
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
        c.append(
            Module.Section(Element.Text(text, Types.Text.KMD),
                           Element.Image(src=icon.correct, size='sm')))
        c.append(
            Module.Context(
                Element.Text(
                    "当前token失效时间为1h，有任何问题请[点我](https://kook.top/gpbTwZ)",
                    Types.Text.KMD)))
        cm.append(c)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)

        # 修改/新增都需要写入文件
        with open("./log/UserAuth.json", 'w', encoding='utf-8') as fw2:
            json.dump(UserTokenDict,
                      fw2,
                      indent=2,
                      sort_keys=True,
                      ensure_ascii=False)
        print(
            f"Login  - Au:{msg.author_id} - {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}"
        )
    
    except auth_exceptions.RiotAuthenticationError as result:
        print(f"ERR! [{GetTime()}] login - {result}")
        cm = CardMessage()
        c = Card(color='#fb4b57')
        text = f"当前的账户密码真的对了吗？"
        c.append(
            Module.Section(Element.Text(text, Types.Text.KMD),
                            Element.Image(src=icon.dont_do_that,
                                            size='sm')))
        c.append(
            Module.Context(
                Element.Text("Make sure username and password are correct",
                                Types.Text.KMD)))
        cm.append(c)
        await upd_card(send_msg['msg_id'],
                        cm,
                        channel_type=msg.channel_type)
    except auth_exceptions.RiotMultifactorError as result:
        print(f"ERR! [{GetTime()}] login - {result}")
        text = f"当前不支持开启了`邮箱双重验证`的账户"
        cm = CardMessage()
        c = Card(color='#fb4b57')
        c.append(
            Module.Section(Element.Text(text, Types.Text.KMD),
                            Element.Image(src=icon.that_it, size='sm')))
        c.append(
            Module.Context(
                Element.Text(
                    "Multi-factor authentication is not currently supported",
                    Types.Text.KMD)))
        cm.append(c)
        await upd_card(send_msg['msg_id'],
                        cm,
                        channel_type=msg.channel_type)
    except auth_exceptions.RiotRatelimitError as result:
        print(f"ERR! [{GetTime()}] login - riot_auth.auth_exceptions.RiotRatelimitError")
         #更新全局速率限制
        login_rate_limit['limit'] = True
        login_rate_limit['time'] = time.time()
        ret_cm = get_login_rate_cm()#这里是第一个出现速率限制err的用户
        await upd_card(send_msg['msg_id'],
                        ret_cm,
                        channel_type=msg.channel_type)
    except:
        err_str = f"ERR! [{GetTime()}] login\n ```\n{traceback.format_exc()}\n```"
        print(err_str) #只有不认识的报错消息才打印结果
        c.append(Module.Header(f"很抱歉，发生了未知错误"))
        c.append(Module.Divider())
        c.append(
            Module.Section(
                Element.Text(f"{err_str}\n\n您可能需要重新执行/login操作",
                                Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(
            Module.Section(
                '有任何问题，请加入帮助服务器与我联系',
                Element.Button('帮助', 'https://kook.top/gpbTwZ',
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
                Module.Section(
                    Element.Text(text, Types.Text.KMD),
                    Element.Image(src=icon.im_good_phoniex, size='sm')))
            c.append(
                Module.Context(
                    Element.Text(f"{resp['message']}", Types.Text.KMD)))
            cm.append(c)
            send_msg = await msg.reply(cm)

        #不管传入的是用户id还是msg，都传userid进入该函数
        ret = await login_re_auth(user_id)
        if ret == False and is_msg:  #没有正常返回
            cm = CardMessage()
            text = f"重新获取token失败，请私聊「/login」重新登录\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.crying_crab, size='sm')))
            c.append(
                Module.Context(
                    Element.Text(f"Auto Reauthorize Failed!", Types.Text.KMD)))
            cm.append(c)  #如果重新获取token失败，则更新上面的消息
            await upd_card(send_msg['msg_id'],
                           cm,
                           channel_type=msg.channel_type)
        elif ret == True and is_msg:  #正常重新登录，且传过来了消息
            return send_msg  #返回发送出去的消息（用于更新）

        return ret  #返回假
    except Exception as result:
        if 'httpStatus' in str(result):
            print(f"[Ckeck_re_auth] No need to reauthorize. [{result}]")
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
                f"您当前已登录账户 `{UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}`"
            )
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
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.that_it, size='sm')))
            c.append(
                Module.Context(
                    Element.Text(f"「/login 账户 密码」请确认您知晓这是一个风险操作",
                                 Types.Text.KMD)))
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
        c.append(
            Module.Section(Element.Text(text, Types.Text.KMD),
                           Element.Image(src=icon.crying_crab, size='sm')))
        c.append(Module.Context(Element.Text(f"你会回来的，对吗？", Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)

        #最后重新执行写入
        del UserTokenDict[msg.author_id]
        with open("./log/UserAuth.json", 'w', encoding='utf-8') as fw1:
            json.dump(UserTokenDict,
                      fw1,
                      indent=2,
                      sort_keys=True,
                      ensure_ascii=False)
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
            json.dump(ValSkinList,
                      fw2,
                      indent=2,
                      sort_keys=True,
                      ensure_ascii=False)
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
            json.dump(ValPriceList,
                      fw2,
                      indent=2,
                      sort_keys=True,
                      ensure_ascii=False)
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
                bg_bundle_icon = Image.open(
                    io.BytesIO(requests.get(b['displayIcon']).content))
                imgByteArr = io.BytesIO()
                bg_bundle_icon.save(imgByteArr, format='PNG')
                imgByte = imgByteArr.getvalue()
                print(f"Uploading - {b['displayName']}")
                bundle_img_src = await bot.client.create_asset(imgByte)
                print(f"{b['displayName']} - url: {bundle_img_src}")
                b['displayIcon2'] = bundle_img_src  #修改url
                ValBundleList.append(b)  #插入

        with open("./log/ValBundle.json", 'w', encoding='utf-8') as fw1:
            json.dump(ValBundleList,
                      fw1,
                      indent=2,
                      sort_keys=True,
                      ensure_ascii=False)

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
UserShopDict={}

#计算当前时间和明天早上8点的差值
def shop_time_remain():
    today = datetime.today().strftime("%y-%m-%d %H:%M:%S")#今天日期+时间
    tomorow = (datetime.today()+timedelta(days=1)).strftime("%y-%m-%d")#明天日期
    #print(f"{tomorow} 08:00:00")
    times_tomorow = time.mktime(time.strptime(f"{tomorow} 08:00:00","%y-%m-%d %H:%M:%S"))#明天早上8点时间戳
    times_now = time.mktime(time.strptime(f"{today}","%y-%m-%d %H:%M:%S"))#现在的时间戳
    #print(times_tomorow)
    timeout = times_tomorow - times_now#计算差值
    timeout = time.strftime("%H:%M:%S",time.gmtime(timeout))#转换成可读时间
    #print(timeout)
    return timeout

def isSame_Authuuid(msg:Message):#判断uuid是否相等
    return UserShopDict[msg.author_id]["auth_user_id"] == UserTokenDict[msg.author_id]["auth_user_id"]

#每天早上8点准时清除商店dict
@bot.task.add_cron(hour=8, minute=0, timezone="Asia/Shanghai")
async def clear_usershopdict():
    global UserShopDict
    UserShopDict={}
    print("[BOT.TASK] clear UserShopDict finished")

# 获取每日商店的命令
@bot.command(name='shop', aliases=['SHOP'])
async def get_daily_shop(msg: Message, *arg):
    logging(msg)
    if arg != ():
        await msg.reply(f"`/shop`命令不需要参数。您是否想`/login`？")
        return

    try:
        if msg.author_id in UserAuthDict:
            reau = await check_re_auth("每日商店", msg)
            if reau == False: return  #如果为假说明重新登录失败
            # 重新获取token成功了再提示正在获取商店
            cm = CardMessage()  #卡片侧边栏颜色
            text = "正在尝试获取您的每日商店"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.duck, size='sm')))
            c.append(
                Module.Context(Element.Text("阿狸正在施法，很快就好啦！", Types.Text.KMD)))
            cm.append(c)
            if isinstance(reau, dict):  #如果传过来的是一个dict，说明重新登录成功且发送了消息
                await upd_card(reau['msg_id'],
                               cm,
                               channel_type=msg.channel_type)
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
            log_time=""
            global UserShopDict
            if msg.author_id in UserShopDict and isSame_Authuuid(msg):
                a_time = time.time()
                list_shop = UserShopDict[msg.author_id]["SkinsPanelLayout"][
                    "SingleItemOffers"]  # 商店刷出来的4把枪
                timeout = shop_time_remain()
                log_time+=f"[Dict_shop] {format(time.time()-a_time,'.4f')} "
            else:
                a_time = time.time()
                resp = await fetch_daily_shop(userdict)  #获取每日商店
                list_shop = resp["SkinsPanelLayout"][
                    "SingleItemOffers"]  # 商店刷出来的4把枪
                timeout = resp["SkinsPanelLayout"][
                    "SingleItemOffersRemainingDurationInSeconds"]  #剩余时间
                timeout = time.strftime("%H:%M:%S",
                                        time.gmtime(timeout))  #将秒数转为标准时间
                #需要设置uuid来保证是同一个用户
                UserShopDict[msg.author_id]={}
                UserShopDict[msg.author_id]["auth_user_id"]=UserTokenDict[msg.author_id]["auth_user_id"]
                UserShopDict[msg.author_id]["SkinsPanelLayout"]=resp["SkinsPanelLayout"]
                log_time+=f"[Api_shop] {format(time.time()-a_time,'.4f')} "
            
            #开始画图
            draw_time = time.time()  #计算画图需要的时间
            x = 0
            y = 0
            bg = copy.deepcopy(bg_main)
            ran = random.randint(1, 9999)
            global shop_img_temp
            shop_img_temp[ran] = []
            img_num = 0

            for skinuuid in list_shop:
                img_path = f'./log/img_temp/comp/{skinuuid}.png'
                if skinuuid in weapon_icon_temp:
                    shop_img_temp[ran].append(weapon_icon_temp[skinuuid])
                elif os.path.exists(img_path):
                    shop_img_temp[ran].append(Image.open(img_path))

                else:
                    th = threading.Thread(target=uuid_to_comp,
                                          args=(skinuuid, ran))
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

            #打印画图耗时
            log_time+=f"- [Drawing] {format(time.time() - draw_time,'.4f')}"
            print(log_time)
            #bg.save(f"test.png")  #保存到本地
            imgByteArr = io.BytesIO()
            bg.save(imgByteArr, format='PNG')
            imgByte = imgByteArr.getvalue()
            dailyshop_img_src = await bot.client.create_asset(imgByte)
            #结束总计时
            end = time.perf_counter()
            using_time = end - start  #结果为 浮点数
            using_time = format(end - start, '.2f')  #保留两位小数

            cm = CardMessage()
            c = Card(color='#fb4b57')
            c.append(
                Module.Header(
                    f"玩家 {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']} 的每日商店！"
                ))
            c.append(
                Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {using_time}s"))
            c.append(Module.Container(Element.Image(src=dailyshop_img_src)))
            cm.append(c)
            await upd_card(send_msg['msg_id'],
                           cm,
                           channel_type=msg.channel_type)
            print(
                f"[{GetTime()}] Au:{msg.author_id} daily_shop reply successful [{using_time}]"
            )
        else:
            cm = CardMessage()
            text = "您尚未登陆！请「私聊」使用login命令进行登录操作\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.whats_that, size='sm')))
            c.append(
                Module.Context(
                    Element.Text("「/login 账户 密码」请确认您知晓这是一个风险操作",
                                 Types.Text.KMD)))
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
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.lagging, size='sm')))
            c.append(
                Module.Context(
                    Element.Text(f"KeyError:{result}, please re-login",
                                 Types.Text.KMD)))
            cm2.append(c)
            await upd_card(send_msg['msg_id'],
                           cm2,
                           channel_type=msg.channel_type)
        else:
            c.append(Module.Header(f"很抱歉，发生了一些错误"))
            c.append(Module.Divider())
            c.append(
                Module.Section(
                    Element.Text(f"{err_str}\n\n您可能需要重新执行/login操作",
                                 Types.Text.KMD)))
            c.append(Module.Divider())
            c.append(
                Module.Section(
                    '有任何问题，请加入帮助服务器与我联系',
                    Element.Button('帮助', 'https://kook.top/gpbTwZ',
                                   Types.Click.LINK)))
            cm2.append(c)
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


# 获取不同奖励的信息
async def get_reward(reward):
    reward_type = reward['reward']['type']
    print("get_reward() ", reward_type)
    if reward_type == 'PlayerCard':  #玩家卡面
        return await fetch_playercard_uuid(reward['reward']['uuid'])
    elif reward_type == 'Currency':  #代币
        # 拳头通行证返回值里面没有数量，我谢谢宁
        return {
            'data': {
                "assetPath":
                "ShooterGame/Content/Currencies/Currency_UpgradeToken_DataAsset",
                "displayIcon":
                "https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png",
                "displayName": "輻能點數",
                "displayNameSingular": "輻能點數",
                "largeIcon":
                "https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/largeicon.png",
                "uuid": "e59aa87c-4cbf-517a-5983-6e81511be9b7"
            }
        }
    elif reward_type == 'EquippableSkinLevel':  #皮肤
        return fetch_skin_bylist(reward['reward']['uuid'])
    elif reward_type == 'Spray':  #喷漆
        return await fetch_spary_uuid(reward['reward']['uuid'])
    elif reward_type == 'EquippableCharmLevel':  #吊坠
        return await fetch_buddies_uuid(reward['reward']['uuid'])
    elif reward_type == 'Title':  #玩家头衔
        return await fetch_title_uuid(reward['reward']['uuid'])

    return None


# 创建一个玩家任务和通信证的卡片消息
async def create_cm_contract(msg: Message):
    userdict = UserTokenDict[msg.author_id]
    # 获取玩家当前任务和通行证情况
    player_mision = await fetch_player_contract(userdict)
    print(player_mision)
    interval_con = len(player_mision['Contracts'])
    battle_pass = player_mision['Contracts'][interval_con - 1]
    print(battle_pass, '\n')
    contract = await fetch_contract_uuid(battle_pass["ContractDefinitionID"])
    print(contract, '\n')
    cur_chapter = battle_pass['ProgressionLevelReached'] // 5  #计算出当前的章节
    remain_lv = battle_pass['ProgressionLevelReached'] % 5  #计算出在当前章节的位置
    print(cur_chapter, ' - ', remain_lv)
    if remain_lv:  #说明还有余度
        cur_chapter += 1  #加1
    else:  #为0的情况，需要修正为5。比如30级是第六章节的最后一个
        remain_lv = 5

    reward_list = contract['data']['content']['chapters'][cur_chapter -
                                                          1]  #当前等级所属章节
    print(reward_list, '\n')
    reward = reward_list['levels'][remain_lv - 1]  #当前所处的等级和奖励
    print(reward)
    reward_next = ""  #下一个等级的奖励
    if remain_lv < 5:
        reward_next = reward_list['levels'][remain_lv]  #下一级
    elif remain_lv >= 5 and cur_chapter < 11:  #避免越界
        reward_next = contract['data']['content']['chapters'][cur_chapter][
            'levels'][0]  #下一章节的第一个
    print(reward_next, '\n')

    c1 = Card(Module.Header(f"通行证 - {contract['data']['displayName']}"),
              Module.Divider())
    reward_res = await get_reward(reward)
    reward_nx_res = await get_reward(reward_next)
    print(reward_res, '\n', reward_nx_res, '\n')

    cur = f"当前等级：{battle_pass['ProgressionLevelReached']}\n"
    cur += f"当前奖励：{reward_res['data']['displayName']}\n"
    cur += f"奖励类型：{reward['reward']['type']}\n"
    cur += f"经验XP：{reward['xp']-battle_pass['ProgressionTowardsNextLevel']}/{reward['xp']}\n"
    c1.append(Module.Section(cur))
    if 'displayIcon' in reward_res['data']:  #有图片才插入
        c1.append(
            Module.Container(
                Element.Image(
                    src=reward_res['data']['displayIcon'])))  #将图片插入进去
    next = f"下一奖励：{reward_nx_res['data']['displayName']}  - 类型:{reward_next['reward']['type']}\n"
    c1.append(Module.Context(Element.Text(next, Types.Text.KMD)))
    return c1


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
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.rgx_card, size='sm')))
            c.append(
                Module.Context(Element.Text("阿狸正在施法，很快就好啦！", Types.Text.KMD)))
            cm.append(c)
            if isinstance(reau, dict):  #如果传过来的是一个dict，说明重新登录成功且发送了消息
                await upd_card(reau['msg_id'],
                               cm,
                               channel_type=msg.channel_type)
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
            player_card = await fetch_playercard_uuid(
                resp['Identity']['PlayerCardID'])  #玩家卡面id
            player_title = await fetch_title_uuid(
                resp['Identity']['PlayerTitleID'])  #玩家称号id
            if resp['Guns'] == None or resp[
                    'Sprays'] == None:  #可能遇到全新账户（没打过游戏）的情况
                cm = CardMessage()
                text = f"状态错误！您是否登录了一个全新账户？"
                c = Card(color='#fb4b57')
                c.append(
                    Module.Section(
                        Element.Text(text, Types.Text.KMD),
                        Element.Image(src=icon.say_hello_to_camera,
                                      size='sm')))
                c.append(
                    Module.Section(
                        Element.Text(
                            f"card: `{player_card}`\ntitle: `{player_title}`",
                            Types.Text.KMD)))
                cm.append(c)
                await upd_card(send_msg['msg_id'],
                               cm,
                               channel_type=msg.channel_type)
                return

            cm = CardMessage()
            c = Card(color='#fb4b57')
            c.append(
                Module.Header(
                    f"玩家 {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']} 的个人信息"
                ))
            c.append(
                Module.Container(
                    Element.Image(
                        src=player_card['data']['wideArt'])))  #将图片插入进去
            text = f"玩家称号：" + player_title['data']['displayName'] + "\n"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
            #cm.append(c)

            #获取玩家的vp和r点剩余
            text = await get_user_vp(msg, userdict)
            c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
            cm.append(c)
            #await msg.reply(cm)
            await upd_card(send_msg['msg_id'],
                           cm,
                           channel_type=msg.channel_type)
            print(f"[{GetTime()}] Au:{msg.author_id} uinfo reply successful!")

        else:
            cm = CardMessage()
            text = "您尚未登陆！请「私聊」使用login命令进行登录操作\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.whats_that, size='sm')))
            c.append(
                Module.Context(
                    Element.Text("「/login 账户 密码」请确认您知晓这是一个风险操作",
                                 Types.Text.KMD)))
            cm.append(c)
            await msg.reply(cm)
            return

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] uinfo\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(
            Module.Section(
                Element.Text(f"{err_str}\n您可能需要重新执行login操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(
            Module.Section(
                '有任何问题，请加入帮助服务器与我联系',
                Element.Button('帮助', 'https://kook.top/gpbTwZ',
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
                c = Card(
                    Module.Section(
                        Element.Text(f"已为您查询到 `{name}` 相关捆绑包",
                                     Types.Text.KMD)))
                for b in ValBundleList:
                    if name in b['displayName']:  # 将图片插入 卡片消息
                        c.append(
                            Module.Container(
                                Element.Image(src=b['displayIcon2'])))
                if weapenlist != []:  # 遇到“再来一局”这种旧皮肤捆绑包，找不到武器名字
                    text = "```\n"
                    for w in weapenlist:
                        res_price = fetch_item_price_bylist(w['lv_uuid'])
                        if res_price != None:  # 有可能出现返回值里面找不到这个皮肤的价格的情况，比如冠军套
                            price = res_price['Cost'][
                                '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
                            text += f"{w['displayName']}   - vp {price}\n"
                        else:  # 找不到价格就直接插入武器名字
                            text += f"{w['displayName']}\n"

                    text += "```\n"  # print(text)
                    c.append(Module.Section(Element.Text(
                        text, Types.Text.KMD)))  #插入皮肤
                cm.append(c)
                await msg.reply(cm)
                print(
                    f"[{GetTime()}] Au:{msg.author_id} get_bundle reply successful!"
                )
                return

        await msg.reply(f"未能查找到结果，请检查您的皮肤名拼写")
        print(
            f"[{GetTime()}] Au:{msg.author_id} get_bundle failed! Can't find {name}"
        )
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] get_bundle\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        ch = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(ch, err_str)


#用户选择列表
UserStsDict = {}
# 皮肤商店提醒记录
with open("./log/UserSkinNotify.json", 'r', encoding='utf-8') as frsi:
    SkinNotifyDict = json.load(frsi)


@bot.task.add_cron(hour=8, minute=2, timezone="Asia/Shanghai")
async def auto_skin_inform():
    try:
        print("[BOT.TASK] auto_skin_inform Starting!")  #开始的时候打印一下
        for aid, skin in SkinNotifyDict.items():
            user = await bot.client.fetch_user(aid)
            if aid in UserAuthDict:
                if await check_re_auth("定时获取玩家商店",
                                       aid) == True:  # 重新登录,如果为假说明重新登录失败
                    auth = UserAuthDict[aid]
                    userdict = {
                        'auth_user_id': auth.user_id,
                        'access_token': auth.access_token,
                        'entitlements_token': auth.entitlements_token
                    }
                    resp = await fetch_daily_shop(userdict)  # 获取每日商店
                    list_shop = resp["SkinsPanelLayout"][
                        "SingleItemOffers"]  # 商店刷出来的4把枪
                    timeout = resp["SkinsPanelLayout"][
                        "SingleItemOffersRemainingDurationInSeconds"]  #剩余时间
                    timeout = time.strftime("%H:%M:%S",
                                            time.gmtime(timeout))  #将秒数转为标准时间
                    text = ""
                    for skinuuid in list_shop:
                        res_item = fetch_skin_bylist(skinuuid)  # 从本地文件中查找
                        res_price = fetch_item_price_bylist(
                            skinuuid)  # 在本地文件中查找
                        price = res_price['Cost'][
                            '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
                        text += f"{res_item['data']['displayName']}     - VP {price}\n"

                    cm = CardMessage()  #向用户发送当前的每日商店（文字）
                    c = Card(color='#fb4b57')
                    c.append(
                        Module.Section(
                            Element.Text(f"请查收您的每日商店", Types.Text.KMD),
                            Element.Image(src=icon.shot_on_fire, size='sm')))
                    c.append(Module.Section(Element.Text(text,
                                                         Types.Text.KMD)))
                    c.append(
                        Module.Context(
                            Element.Text(f"这里有没有你想要的枪皮呢？", Types.Text.KMD)))
                    cm.append(c)
                    await user.send(cm)

                    # 然后再遍历列表查看是否有提醒皮肤
                    # 关于下面这一行：https://img.kookapp.cn/assets/2022-08/oYbf8PM6Z70ae04s.png
                    target_skin = [
                        val for key, val in skin.items() if key in list_shop
                    ]
                    # print(target_skin)
                    for name in target_skin:
                        print(f"[BOT.TASK] Au:{aid} auto_skin_inform = {name}")
                        await user.send(
                            f"[{GetTime()}] 您的每日商店刷出`{name}`了，请上号查看哦！")
                    print(f"[BOT.TASK] Au:{aid} auto_skin_inform = None"
                          )  #打印这个说明这个用户正常遍历完了
            else:  #不在auth里面说明没有登录
                print(f"[BOT.TASK] Au:{aid} user_not_in UserAuthDict")
                await user.send(f"您设置了皮肤提醒，却没有登录！请尽快`login`哦~")
        #完成遍历后打印
        finish_str = "[BOT.TASK] auto_skin_inform Finished!"
        print(finish_str)  #正常完成
        ch = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(ch, finish_str)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] auto_skin_inform\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        ch = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(ch, err_str)


#设置提醒（出现xx皮肤）
@bot.command(name="notify-add", aliases=['notify-a'])
async def add_skin_notify(msg: Message, *arg):
    logging(msg)
    if arg == ():
        await msg.reply(f"你没有提供皮肤参数！skin: `{arg}`")
        return
    try:
        #用户没有登录
        if msg.author_id not in UserAuthDict:
            cm = CardMessage()
            text = "您尚未登陆！请「私聊」使用login命令进行登录操作\n"
            c = Card(color='#fb4b57')
            c.append(
                Module.Section(Element.Text(text, Types.Text.KMD),
                               Element.Image(src=icon.whats_that, size='sm')))
            c.append(
                Module.Context(
                    Element.Text(
                        "「/login 账户 密码」请确认您知晓这是一个风险操作\n设置了皮肤提醒之后，请勿切换已登录的账户",
                        Types.Text.KMD)))
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
                price = res_price['Cost'][
                    '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
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
        c = Card(
            Module.Header(f"查询到 {name} 相关皮肤如下"),
            Module.Context(
                Element.Text("请在下方键入序号进行选择，请不要选择已购买的皮肤", Types.Text.KMD)),
            Module.Section(
                Element.Text(text + "\n\n使用 `/sts 序号` 来选择", Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] addskin\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(
            Module.Section(
                Element.Text(f"{err_str}\n您可能需要重新执行login操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(
            Module.Section(
                '有任何问题，请加入帮助服务器与我联系',
                Element.Button('帮助', 'https://kook.top/gpbTwZ',
                               Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


#选择皮肤（这个命令必须跟着上面的命令用）
@bot.command(name="sts")
async def select_skin_notify(msg: Message, n: str = "err",*arg):
    logging(msg)
    if n == "err" or '-' in n:
        await msg.reply(f"参数不正确！请选择您需要提醒的皮肤序号")
        return
    try:
        global SkinNotifyDict
        if msg.author_id in UserStsDict:
            num = str2int(n)  #转成int下标（不能处理负数）
            if num >= len(UserStsDict[msg.author_id]):#下标判断，避免越界
                await msg.reply(f"您的选择越界了！请正确填写序号")
                return
                
            S_skin = UserStsDict[msg.author_id][num]
            if msg.author_id not in SkinNotifyDict:
                SkinNotifyDict[msg.author_id] = {}
                SkinNotifyDict[msg.author_id][
                    S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            else:  #如果存在了就直接在后面添加
                SkinNotifyDict[msg.author_id][
                    S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            # print(SkinNotifyDict[msg.author_id])
            # 写入文件
            with open("./log/UserSkinNotify.json", 'w',
                      encoding='utf-8') as fw2:
                json.dump(SkinNotifyDict,
                          fw2,
                          indent=2,
                          sort_keys=True,
                          ensure_ascii=False)

            del UserStsDict[msg.author_id]  #删除选择页面中的list
            text = f"设置成功！已开启`{S_skin['skin']['displayName']}`的提醒"
            print(f"Au:{msg.author_id} ", text)
            await msg.reply(text)
        else:
            await msg.reply(f"您需要（重新）执行`/notify-a`来设置提醒皮肤")

    except Exception as result:
        err_str = f"ERR! [{GetTime()}] select_skin_inform\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"), Module.Divider())
        c.append(
            Module.Section(
                Element.Text(f"{err_str}\n您可能需要重新执行操作", Types.Text.KMD)))
        c.append(Module.Divider())
        c.append(
            Module.Section(
                '有任何问题，请加入帮助服务器与我联系',
                Element.Button('帮助', 'https://kook.top/gpbTwZ',
                               Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 显示当前设置好了的皮肤通知
@bot.command(name="notify-list", aliases=['notify-l'])
async def list_skin_notify(msg: Message,*arg):
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
        ch = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(ch, err_str)


# 删除已有皮肤通知
@bot.command(name="notify-del", aliases=['notify-d'])
async def delete_skin_notify(msg: Message, uuid: str = "err",*arg):
    logging(msg)
    if uuid == 'err':
        await msg.reply(f"请提供正确的皮肤uuid：`{uuid}`")
        return
    try:
        global SkinNotifyDict
        if msg.author_id in SkinNotifyDict:
            if uuid in SkinNotifyDict[msg.author_id]:
                print(
                    f"notify-d - Au:{msg.author_id} = {uuid} {SkinNotifyDict[msg.author_id][uuid]}"
                )
                await msg.reply(
                    f"已删除皮肤：`{SkinNotifyDict[msg.author_id][uuid]}`")
                del SkinNotifyDict[msg.author_id][uuid]
                # 写入文件
                with open("./log/UserSkinNotify.json", 'w',
                          encoding='utf-8') as fw2:
                    json.dump(SkinNotifyDict,
                              fw2,
                              indent=2,
                              sort_keys=True,
                              ensure_ascii=False)
            else:
                await msg.reply(f"您提供的uuid不在列表中！")
                return
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] notify-del\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)
        ch = await bot.client.fetch_public_channel(Debug_ch)
        await bot.client.send(ch, err_str)


# 开机的时候打印一次时间，记录重启时间
print(f"Start at: [%s]" % GetTime())

#bot.run()是机器人的起跑线
bot.run()
