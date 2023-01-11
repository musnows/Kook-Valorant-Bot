# encoding: utf-8:
import json
import os
import random
import time
import traceback
from datetime import datetime, timedelta
from typing import Union

import aiohttp
import khl
import requests
from khl import (Bot, Client, Event, EventTypes, Message, PrivateMessage,
                 PublicChannel, PublicMessage, requester)
from khl.card import Card, CardMessage, Element, Module, Types, Struct
from khl.command import Rule
from aiohttp import client_exceptions

from endpoints.Help import help_main,help_val,help_develop
from endpoints.BotLog import logging, log_bot_list, log_bot_user, APIRequestFailed_Handler, BaseException_Handler
from endpoints.Other import  weather
from endpoints.KookApi import (icon_cm, status_active_game,
                       status_active_music, status_delete, guild_view, upd_card)
from endpoints.GrantRoles import (Color_GrantRole,Color_SetGm,Color_SetMsg,THX_Sponser)
from endpoints.Val import *
from endpoints.Gtime import GetTime,GetTimeStampOf8AM
from endpoints.BotVip import (VipUserDict, create_vip_uuid, fetch_vip_user,
                       roll_vip_start, using_vip_uuid, vip_ck, vip_time_remain,
                       vip_time_remain_cm, vip_time_stamp)
from endpoints.Translate import ListTL,translate_main,Shutdown_TL,checkTL,Open_TL,Close_TL
from endpoints.ShopRate import SkinRateDict,get_shop_rate_cm,check_shop_rate
from endpoints.ShopImg import get_shop_img_11,get_shop_img_169

# bot的token文件
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])
# 只用来上传图片的bot
bot_upimg = Bot(token=config['img_upload_token'])

# 设置全局变量：机器人开发者id/报错频道
master_id = config['master_id']
Debug_ch = config['debug_ch']
kook_headers = {f'Authorization': f"Bot {config['token']}"}

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

#记录开机时间
start_time = GetTime()

# 拳头api调用被禁止的时候用这个变量取消所有相关命令
Login_Forbidden = False
async def Login_Forbidden_send(msg:Message):
    print(f"[Login_Forbidden] Au:{msg.author_id} Command Failed")
    await msg.reply(f"拳头api登录接口出现了一些错误，开发者已禁止所有相关功能的使用\n[https://img.kookapp.cn/assets/2022-09/oj33pNtVpi1ee0eh.png](https://img.kookapp.cn/assets/2022-09/oj33pNtVpi1ee0eh.png)")
    

# hello命令，一般用于测试阿狸在不在线
@bot.command(name='hello',aliases=['HELLO'])
async def world(msg: Message):
    logging(msg)
    await msg.reply('你好呀~')

# help命令,触发指令为 `/Ahri`,因为help指令和其他机器人冲突
@bot.command(name='Ahri', aliases=['ahri','阿狸'])
async def Ahri(msg: Message, *arg):
    logging(msg)
    try:
        cm = help_main(start_time)
        await msg.reply(cm)
    except Exception as result:
        await BaseException_Handler("ahri",traceback.format_exc(),msg,bot,None,None,"建议加入帮助频道找我康康到底是啥问题")
        err_str = f"ERR! [{GetTime()}] ahri\n```\n{traceback.format_exc()}\n```"
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# help命令(瓦洛兰特相关)
@bot.command(name='Vhelp', aliases=['vhelp'])
async def Vhelp(msg: Message, *arg):
    logging(msg)
    try:
        cm = help_val()
        await msg.reply(cm)
    except Exception as result:
        await BaseException_Handler("vhelp",traceback.format_exc(),msg,bot,None,None,"建议加入帮助频道找我康康到底是啥问题")
        err_str = f"ERR! [{GetTime()}] vhelp\n```\n{traceback.format_exc()}\n```"
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# 当有人@机器人的时候进行回复，可识别出是否为机器人作者
@bot.command(regex=r'(.+)', rules=[Rule.is_bot_mentioned(bot)])
async def atAhri(msg: Message, mention_str: str):
    logging(msg)
    try:
        if msg.author_id == master_id:
            text = help_develop()
            await msg.reply(text)
        else:
            await msg.reply(f"呀，听说有人想我了，是吗？\n输入`/ahri`打开帮助面板，和阿狸一起玩吧！")
        print(f"[atAhri] Au:{msg.author_id} msg.reply success!")
    except:
        err_str = f"ERR! [{GetTime()}] atAhri\n```\n{traceback.format_exc()}\n```"
        await msg.reply(f"{err_str}")
        print(err_str)

#################################################################################################
#################################################################################################

# 倒计时函数，单位为秒，默认60秒
@bot.command()
async def countdown(msg: Message, time: int = 60,*args):
    logging(msg)
    if args != ():
        await msg.reply(f"参数错误，countdown命令只支持1个参数\n正确用法: `/countdown 120` 生成一个120s的倒计时")
        return
    elif time<=0 or time>= 90000000:
        await msg.reply(f"倒计时时间超出范围！")
        return
    try:
        cm = CardMessage()
        c1 = Card(Module.Header('本狸帮你按下秒表喽~'), color=(198, 65, 55))  # color=(90,59,215) is another available form
        c1.append(Module.Divider())
        c1.append(Module.Countdown(datetime.now() + timedelta(seconds=time), mode=Types.CountdownMode.SECOND))
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        await BaseException_Handler("countdown",traceback.format_exc(),msg,bot,None,None,"建议加入帮助频道找我康康到底是啥问题")
        err_str = f"ERR! [{GetTime()}] countdown\n```\n{traceback.format_exc()}\n```"
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# 掷骰子 saying `!roll 1 100` in channel,or `/roll 1 100 5` to dice 5 times once
@bot.command()
async def roll(msg: Message, t_min: int = 1, t_max: int = 100, n: int = 1,*args):
    logging(msg)
    if args != ():
        await msg.reply(f"参数错误，roll命令只支持3个参数\n正确用法:\n```\n/roll 1 100 生成一个1到100之间的随机数\n/roll 1 100 3 生成三个1到100之间的随机数\n```")
        return
    elif t_min >= t_max:#范围小边界不能大于大边界
        await msg.reply(f'范围错误，必须提供两个参数，由小到大！\nmin:`{t_min}` max:`{t_max}`')
        return
    elif t_max>= 90000000:#不允许用户使用太大的数字
        await msg.reply(f"掷骰子的数据超出范围！")
        return
    try:
        result = [random.randint(t_min, t_max) for i in range(n)]
        await msg.reply(f'掷出来啦: {result}')
    except Exception as result:
        await BaseException_Handler("roll",traceback.format_exc(),msg,bot,None,None,"建议加入帮助频道找我康康到底是啥问题")
        err_str = f"ERR! [{GetTime()}] roll\n```\n{traceback.format_exc()}\n```"
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


################################以下是给用户上色功能的内容########################################

# 在不修改代码的前提下设置上色功能的服务器和监听消息
@bot.command()
async def Color_Set_GM(msg: Message, Card_Msg_id: str):
    logging(msg)
    if msg.author_id == master_id:
        await Color_SetGm(msg,Card_Msg_id)

# 判断消息的emoji回应，并给予不同角色
@bot.on_event(EventTypes.ADDED_REACTION)
async def Grant_Roles(b: Bot, event: Event):
    await Color_GrantRole(b,event)

# 给用户上色（在发出消息后，机器人自动添加回应）
@bot.command(name='Color_Set',aliases=['color_set'])
async def Color_Set(msg: Message):
    logging(msg)
    if msg.author_id == master_id:
        await Color_SetMsg(bot,msg)

# 感谢助力者（每天19点进行检查）
@bot.task.add_cron(hour=19, minute=0, timezone="Asia/Shanghai")
async def thanks_sponser():
    await THX_Sponser(bot,kook_headers)

######################################## Translate ################################################

# 普通翻译指令
@bot.command(name='TL', aliases=['tl'])
async def translation(msg: Message, *arg):
    logging(msg)
    await translate_main(msg, ' '.join(arg))

#查看当前占用的实时翻译栏位
@bot.command()
async def CheckTL(msg: Message):
    logging(msg)
    await msg.reply(f"目前已使用栏位:{checkTL()}/{len(ListTL)}")

# 关闭所有栏位的实时翻译（避免有些人用完不关）
@bot.command(name='ShutdownTL',aliases=['SDTL'])
async def ShutdownTL(msg: Message):
    logging(msg)
    if msg.author.id != master_id:
        return  #这条命令只有bot的作者可以调用
    await Shutdown_TL(bot,msg)

# 通过频道id判断是否实时翻译本频道内容
@bot.command(regex=r'(.+)')
async def TL_Realtime(msg: Message, *arg):
    if msg.ctx.channel.id in ListTL:#判断频道是否已开启实时翻译
        word = " ".join(arg)
        # 不翻译关闭实时翻译的指令
        if word == "/TLOFF" or word == "/tloff" or word == '/tlon' or word == '/TLON':
            return
        # 翻译
        logging(msg)
        await translate_main(msg, ' '.join(arg))

# 开启实时翻译功能
@bot.command(name='TLON', aliases=['tlon'])
async def TLON(msg: Message):
    logging(msg)
    await Open_TL(msg)

# 关闭实时翻译功能
@bot.command(name='TLOFF', aliases=['tloff'])
async def TLOFF(msg: Message):
    logging(msg)
    await Close_TL(msg)


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
        await BaseException_Handler("Weather",traceback.format_exc(),msg,bot,None,None,"建议加入帮助频道找我康康到底是啥问题")
        err_str = f"ERR! [{GetTime()}] Weather\n```\n{traceback.format_exc()}\n```"
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)

###########################################################################################
####################################以下是游戏相关代码区#####################################
###########################################################################################

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


# 存储用户游戏id
@bot.command()
async def saveid(msg: Message, *args):
    logging(msg)
    if args == ():
        await msg.reply(f"您没有提供您的游戏id：`{args}`")
        return
    try:
        game_id = " ".join(args)  #避免用户需要输入双引号
        await saveid_main(msg, game_id)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] saveid\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)


# 已保存id总数
@bot.command(name='saveid-a')
async def saveid_all(msg: Message):
    logging(msg)
    try:
        await saveid_count(msg)
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
        await myid_main(msg)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] myid\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await msg.reply(err_str)



# 查询游戏错误码
@bot.command(name='val', aliases=['van', 'VAN', 'VAL'])
async def val_err(msg: Message, numS: str = "-1",*arg):
    logging(msg)
    try:
        #num = int(numS)
        await val_errcode(msg, numS)
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
        LevelIcon = Image.open(io.BytesIO(requests.get(level_icon).content))  # 打开武器等级图片
        level_icon_temp[level_icon] = LevelIcon
    else:
        LevelIcon = level_icon_temp[level_icon]
    end = time.perf_counter()
    log_time += f"- [GetIters] {format(end - start, '.4f')} "
    print(log_time)

    w, h = LevelIcon.size  # 读取武器等级图片长宽
    new_w = int(w * standard_level_icon_reszie_ratio)  # 按比例缩放的长
    new_h = int(h * standard_level_icon_reszie_ratio)  # 按比例缩放的宽
    LevelIcon = LevelIcon.resize((new_w, new_h), Image.Resampling.LANCZOS)
    LevelIcon = LevelIcon.convert('RGBA')
    bg.paste(LevelIcon, standard_level_icon_position, LevelIcon)

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
        LevelIcon = Image.open(io.BytesIO(requests.get(level_icon).content))  # 打开武器等级的图片
        level_icon_temp[level_icon] = LevelIcon
    else:
        LevelIcon = level_icon_temp[level_icon]
    end = time.perf_counter()
    log_time += f"- [GetIters] {format(end - start, '.4f')} "
    print(log_time)
    LevelIcon = LevelIcon.resize((25, 25), Image.Resampling.LANCZOS)
    LevelIcon = LevelIcon.convert('RGBA')
    bg.paste(LevelIcon, (368, 11), LevelIcon)
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


###########################################vip######################################################

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
        ret = await using_vip_uuid(msg, uuid, bot,debug_ch)

    except Exception as result:
        await BaseException_Handler("vip-u",traceback.format_exc(),msg,bot,None,None,"建议加入帮助频道找我康康到底是啥问题")
        err_str = f"ERR! [{GetTime()}] vip-u\n```\n{traceback.format_exc()}\n```"
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


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
        await BaseException_Handler("vip-c",traceback.format_exc(),msg,bot,None,None,"建议加入帮助频道找我康康到底是啥问题")
        err_str = f"ERR! [{GetTime()}] vip-c\n```\n{traceback.format_exc()}\n```"
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# 看vip用户列表
@bot.command(name="vip-l")
async def list_vip_user(msg: Message, *arg):
    logging(msg)
    try:
        if msg.author_id == master_id:
            text = await fetch_vip_user()
            cm2 = CardMessage()
            c = Card(Module.Header(f"当前vip用户列表如下"), color='#e17f89')
            c.append(Module.Section(Element.Text(f"```\n{text}```", Types.Text.KMD)))
            cm2.append(c)
            await msg.reply(cm2)
        else:
            await msg.reply("您没有权限操作此命令！")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] list_vip_user\n```\n{traceback.format_exc()}\n```"
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
        log_str_user = "[BOT.TASK] check_vip_img Au:"
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
            log_str_user+=f"({vip_user})"
            #print(f"[BOT.TASK] check_vip_img Au:{vip_user} finished!")
        #所有用户成功遍历后，写入文件
        with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipShopBgDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        #打印
        print(log_str_user)
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
        await APIRequestFailed_Handler("vip_shop",traceback.format_exc(),msg,bot,None,cm)
        VipShopBgDict[msg.author_id]["background"].remove(x3)  #删掉里面的图片
        print(f"[vip_shop] Au:{msg.author_id} remove(err_img)")
    except Exception as result:
        await BaseException_Handler("vip_shop",traceback.format_exc(),msg,bot,None,cm,"建议加入帮助频道找我康康到底是啥问题")


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

        num = int(num)
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
    except requester.HTTPRequester.APIRequestFailed as result:
        await APIRequestFailed_Handler("vip_shop_s",traceback.format_exc(),msg,bot,None,cm)
    except Exception as result:
        await BaseException_Handler("vip_shop_s",traceback.format_exc(),msg,bot,None,cm,"您可能需要重新执行操作")


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

        num = int(num)
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
    except requester.HTTPRequester.APIRequestFailed as result:
        await APIRequestFailed_Handler("vip_shop_d",traceback.format_exc(),msg,bot,None,cm)
    except Exception as result:
        await BaseException_Handler("vip_shop_d",traceback.format_exc(),msg,bot,None,cm,"您可能需要重新执行操作")

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
                c=Card(Module.Section(Element.Text("恭喜您中奖阿狸vip了！", Types.Text.KMD), Element.Image(src=icon_cm.ahri_kda2, size='sm')))
                c.append(Module.Context(Element.Text(f"您抽中了{vday}天vip，可用/vhelp查看vip权益", Types.Text.KMD)))
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

        
# 给所有vip用户添加时间，避免出现某些错误的时候浪费vip时间
@bot.command(name='vip-ta')
async def vip_time_add(msg:Message,vday:int=1,*arg):
    logging(msg)
    if msg.author_id!= master_id:
        await msg.reply(f"您没有权限执行此命令！")
        return
    
    try:
        global VipUserDict
        # 给所有vip用户上天数
        for vip,vinfo in VipUserDict.items():
            time_vip = vip_time_stamp(vip, vday)
            VipUserDict[vip]['time'] = time_vip
        
        await msg.reply(f"操作完成，已给所有vip用户增加 `{vday}` 天时长")
        # 将修改存放到文件中
        with open("./log/VipUser.json", 'w', encoding='utf-8') as fw2:
            json.dump(VipUserDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"[vip_time_add] update VipUserDict")
    except:
        err_str = f"ERR! [{GetTime()}] vip_time_add\n```\n{traceback.format_exc()}\n```"
        await msg.reply(f"{err_str}")
        print(err_str)
    

##############################################################################

# 预加载用户的riot游戏id和玩家uuid（登录后Api获取）
with open("./log/UserAuthID.json", 'r', encoding='utf-8') as frau:
    UserTokenDict = json.load(frau)


# 用来存放auth对象（无法直接保存到文件）
UserAuthDict = {}
# 用来存放已保存cookie的用户id（保存在文件中）
UserCookieDict = {}
#用于限制用户操作，一分钟只能3次
login_dict = {}
#全局的速率限制，如果触发了速率限制的err，则阻止所有用户login
login_rate_limit = {'limit': False, 'time': time.time()}
#检查评分的错误用户（违规用户）
def check_rate_err_user(user_id:str):
    """(user_id in SkinRateDict['err_user'])
    """
    return (user_id in SkinRateDict['err_user'])

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



# 登录，保存用户的token
@bot.command(name='login')
async def login_authtoken(msg: Message, user: str = 'err', passwd: str = 'err',tfa=False,*arg):
    print(f"[{GetTime()}] Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = /login {tfa}")
    log_bot_user(msg.author_id) #这个操作只是用来记录用户和cmd总数的
    global Login_Forbidden
    if not isinstance(msg, PrivateMessage): # 不是私聊的话，禁止调用本命令
        await msg.reply(f"为了避免您的账户信息泄漏，请「私聊」使用本命令！\n用法：`/login 账户 密码`")
        return
    elif passwd == 'err' or user == 'err':
        await msg.reply(f"参数不完整，请提供您的账户密码！\naccount: `{user}` passwd: `{passwd}`\n正确用法：`/login 账户 密码`")
        return
    elif arg != ():
        await msg.reply(f"您给予了多余的参数，请检查后重试\naccount: `{user}` passwd: `{passwd}`\n多余参数: `{arg}`\n正确用法：`/login 账户 密码`")
        return
    elif Login_Forbidden:
        await Login_Forbidden_send(msg)
        return

    global login_rate_limit, UserTokenDict, UserAuthDict
    try:
        cm0 = CardMessage()
        c = Card(color='#fb4b57')  #卡片侧边栏颜色

        # 全局请求超速
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
        # 用户请求超速
        if await check_user_login_rate(msg):
            print(f"Login  - Au:{msg.author_id} - raise user_login_rate_limit")
            return

        text = "正在尝试获取您的riot账户token"
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.val_logo_gif, size='sm')))
        c.append(Module.Context(Element.Text("小憩一下，很快就好啦！", Types.Text.KMD)))
        cm0.append(c)
        send_msg = await msg.reply(cm0)  #记录消息id用于后续更新

        # 获取用户的token
        res_auth = None
        if not tfa:
            res_auth = await authflow(user, passwd)
        else:
            res_auth = await auth2fa(msg,user,passwd)
        UserTokenDict[msg.author_id] = {'auth_user_id': res_auth.user_id, 'GameName':'None', 'TagLine':'0000'} 
        userdict = {
            'auth_user_id': res_auth.user_id,
            'access_token': res_auth.access_token,
            'entitlements_token': res_auth.entitlements_token
        }
        res_gameid = await fetch_user_gameID(userdict)  # 获取用户玩家id
        UserTokenDict[msg.author_id]['GameName'] = res_gameid[0]['GameName']
        UserTokenDict[msg.author_id]['TagLine'] = res_gameid[0]['TagLine']
        UserAuthDict[msg.author_id] = { "auth":res_auth,"2fa":tfa}  #将对象插入

        info_text = "当前token有效期为2~3天，有任何问题请[点我](https://kook.top/gpbTwZ)"
        if tfa:
            info_text = "由于后台实现的限制，您每次登录的时候都需要提供验证码，见谅T.T\n有任何问题请[点我](https://kook.top/gpbTwZ)"

        cm = CardMessage()
        text = f"登陆成功！欢迎回来，{UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}"
        c = Card(color='#fb4b57')
        c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.correct, size='sm')))
        c.append(Module.Context(Element.Text(info_text, Types.Text.KMD)))
        cm.append(c)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)

        # 修改/新增都需要写入文件
        with open("./log/UserAuthID.json", 'w', encoding='utf-8') as fw2:
            json.dump(UserTokenDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

        # 如果是vip用户，则执行下面的代码
        if await vip_ck(msg.author_id):
            global VipShopBgDict #因为换了用户，所以需要修改状态码重新获取商店
            if msg.author_id in VipShopBgDict:
                VipShopBgDict[msg.author_id]['status']=False
                #为了保险起见，保存一下状态信息到文件
                with open("./log/VipUserShopBg.json", 'w', encoding='utf-8') as fw1:
                    json.dump(VipShopBgDict, fw1, indent=2, sort_keys=True, ensure_ascii=False)
            if not tfa:#如果没有使用2fa接口，那就保存cookie
                cookie_path = f"./log/cookie/{msg.author_id}.cke"#用于保存cookie的路径
                res_auth._cookie_jar.save(cookie_path)#保存

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
        text = f"若您开始了邮箱双重验证，请使用「/login 账户 密码 1」来登录"
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
    except client_exceptions.ClientResponseError as result:
        err_str = f"[Login] aiohttp ERR!\n```\n{traceback.format_exc()}\n```\n"
        if 'auth.riotgames.com' and '403' in str(result):
            Login_Forbidden = True
            err_str+= f"[Login] 403 err! set Login_Forbidden = True"
        elif '404' in str(result):
            err_str+= f"[Login] 404 err! network err, try again"
        else:
            err_str+= f"[Login] Unkown aiohttp ERR!"
        
        print(err_str)
        await bot.client.send(debug_ch,err_str)
        await upd_card(send_msg['msg_id'], ret_cm, channel_type=msg.channel_type)
    except KeyError as result:
        print(f"ERR! [{GetTime()}] login - KeyError:{result}")
        cm = CardMessage()
        c = Card(color='#fb4b57')
        if '0' in str(result):
            text = f"遇到不常见的KeyError，可能👊Api服务器炸了"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.that_it, size='sm')))
            c.append(Module.Context(Element.Text("KeyError, maybe API Offline", Types.Text.KMD)))
            cm.append(c)
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
        else:
            text = f"遇到未知的KeyError，请[联系](https://kook.top/gpbTwZ)阿狸的主人哦~"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.that_it, size='sm')))
            c.append(Module.Context(Element.Text("Unkown KeyError, please contact bot developer", Types.Text.KMD)))
            cm.append(c)
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except requester.HTTPRequester.APIRequestFailed as result: #卡片消息发送失败
        await APIRequestFailed_Handler("login",traceback.format_exc(),msg,bot,send_msg,cm)
    except Exception as result: # 其他错误
        await BaseException_Handler("login",traceback.format_exc(),msg,bot,send_msg,cm)

from endpoints.EzAuth import User2faCode

@bot.command(name='tfa')
async def auth_2fa(msg:Message,tfa:str,*arg):
    print(f"[{GetTime()}] Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = /2fa")
    if len(tfa)!=6:
        await msg.reply(f"邮箱验证码长度错误，请确认您输入了正确的6位验证码\n当前参数：{tfa}")
        return
    
    try:
        global User2faCode
        if msg.author_id in User2faCode:
            User2faCode[msg.author_id]['vcode'] = tfa
            User2faCode[msg.author_id]['status'] = True
            await msg.reply(f"两步验证码获取成功，请等待……") 
        else:
            await msg.reply(f"您不在2fa用户列表中，请重新login")

    except Exception as result: # 其他错误
        await BaseException_Handler("tfa",traceback.format_exc(),msg,bot)


# 重新登录
async def login_re_auth(kook_user_id: str):
    base_print = f"[{GetTime()}] Au:{kook_user_id} = "
    print(base_print + "auth_token failure,trying reauthorize()")
    global UserAuthDict
    auth = UserAuthDict[kook_user_id]['auth']
    #用cookie重新登录,会返回一个bool是否成功
    ret = await auth.reauthorize()
    if ret:  #会返回一个bool是否成功,成功了重新赋值
        UserAuthDict[kook_user_id]['auth'] = auth
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
     - send_msg(dict): get `Message` as params & reauhorize success
    """
    user_id = "[ERR!]"  #先给userid赋值，避免下方打印的时候报错（不出意外是会被下面的语句修改的）
    try:
        user_id = msg if isinstance(msg, str) else msg.author_id  #如果是str就直接用
        if UserAuthDict[user_id]['2fa']:
            return True #先判断是否为2fa账户，如果是，那就不进行reauthrize操作
        auth = UserAuthDict[user_id]['auth']
        userdict = {
            'auth_user_id': auth.user_id,
            'access_token': auth.access_token,
            'entitlements_token': auth.entitlements_token
        }
        resp = await fetch_valorant_point(userdict)
        # print('[Check_re_auth]', resp)
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
    
    except client_exceptions.ClientResponseError as result:
        err_str = f"[Check_re_auth] aiohttp ERR!\n```\n{traceback.format_exc()}\n```\n"
        if 'auth.riotgames.com' and '403' in str(result):
            global Login_Forbidden
            Login_Forbidden = True
            err_str+= f"[Check_re_auth] 403 err! set Login_Forbidden = True"
        elif '404' in str(result):
            err_str+= f"[Check_re_auth] 404 err! network err, try again"
        else:
            err_str+= f"[Check_re_auth] Unkown aiohttp ERR!"
        
        print(err_str)
        await bot.client.send(debug_ch,err_str)
        return False
    except Exception as result:
        if 'httpStatus' in str(result):
            print(f"[Check_re_auth] Au:{user_id} No need to reauthorize [{result}]")
            return True
        else:
            print(f"[Check_re_auth] Unkown ERR!\n{traceback.format_exc()}")
            await bot.client.send(debug_ch,f"[Check_re_auth] Unkown ERR!\n{traceback.format_exc()}")
            return False


# 测试是否已登陆
@bot.command(name="login-t")
async def login_test(msg: Message, *arg):
    logging(msg)
    if Login_Forbidden:
        await Login_Forbidden_send(msg)
        return
    try:
        if msg.author_id in UserAuthDict:
            reau = await check_re_auth("测试登录", msg)
            if reau == False: return  #如果为假说明重新登录失败

            await msg.reply(
                f"您当前已登录账户 `{UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}`")
    except Exception as result: # 其他错误
        await BaseException_Handler("login-t",traceback.format_exc(),msg,bot)


# 退出登录
@bot.command(name='logout')
async def logout_authtoken(msg: Message, *arg):
    logging(msg)
    if Login_Forbidden:
        await Login_Forbidden_send(msg)
        return
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
        #del UserTokenDict[msg.author_id] # 没必要删除此键值
        with open("./log/UserAuthID.json", 'w', encoding='utf-8') as fw1:
            json.dump(UserTokenDict, fw1, indent=2, sort_keys=True, ensure_ascii=False)
        fw1.close()
    except Exception as result: # 其他错误
        await BaseException_Handler("logout",traceback.format_exc(),msg,bot)


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
        auth = UserAuthDict[msg.author_id]['auth']
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
@bot.command(name='update_spb',aliases=['update','upd'])
async def update_skin_price_bundle(msg: Message):
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

#判断uuid是否相等
def isSame_Authuuid(msg: Message):  
    return UserShopDict[msg.author_id]["auth_user_id"] == UserTokenDict[msg.author_id]["auth_user_id"]

# 获取vip用户每日商店的图片
async def get_daily_shop_vip_img(list_shop: dict,userdict: dict,user_id: str,is_vip: bool = True, msg: Message = None):
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

# 判断缓存好的图片是否可用
def is_CacheLatest(kook_user_id:str):
    # 判断vip用户是否在背景图中，且没有 切换登录用户/切换背景图
    if kook_user_id in VipShopBgDict:
        is_Status = VipShopBgDict[kook_user_id]['status'] # 如果有切换登录用户/背景图，此为false
        # 判断图片是不是今天的（可能出现早八提醒的时候出错，导致缓存没有更新，是昨天的图）
        is_Today = (VipShopBgDict[kook_user_id]['cache_time']-GetTimeStampOf8AM())>=0 
        return is_Today and is_Status # 有一个为false，结果就是false
    return False 

# 获取每日商店的命令
@bot.command(name='shop', aliases=['SHOP'])
async def get_daily_shop(msg: Message, *arg):
    logging(msg)
    if arg != ():
        await msg.reply(f"`/shop`命令不需要参数。您是否想`/login`？")
        return
    elif Login_Forbidden:
        await Login_Forbidden_send(msg)
        return
    send_msg = None
    try:
        if msg.author_id in UserAuthDict:
            reau = await check_re_auth("每日商店", msg)
            if reau == False: return  #如果为假说明重新登录失败
            # 重新获取token成功，从dict中获取玩家id
            player_gamename = f"{UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']}"
            # 获取玩家id成功了，再提示正在获取商店
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
            auth = UserAuthDict[msg.author_id]['auth']
            userdict = {
                'auth_user_id': auth.user_id,
                'access_token': auth.access_token,
                'entitlements_token': auth.entitlements_token
            }
            log_time = ""
            a_time = time.time()
            global UserShopDict # UserShopDict每天早八会被清空，如果用户在里面且玩家id一样，那么说明已经获取过当日商店了
            if msg.author_id in UserShopDict and isSame_Authuuid(msg): #直接使用本地已有的当日商店
                list_shop = UserShopDict[msg.author_id]["SkinsPanelLayout"]["SingleItemOffers"] # 商店刷出来的4把枪
                timeout = shop_time_remain() # 通过当前时间计算商店剩余时间
                log_time += f"[Dict_shop] {format(time.time()-a_time,'.4f')} "
            else:
                resp = await fetch_daily_shop(userdict)  #本地没有，api获取每日商店
                list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
                timeout = resp["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"] # 剩余时间
                timeout = time.strftime("%H:%M:%S", time.gmtime(timeout)) # 将秒数转为标准时间
                # 需要设置uuid来保证是同一个用户，方便同日的下次查询
                UserShopDict[msg.author_id] = {}
                UserShopDict[msg.author_id]["auth_user_id"] = UserTokenDict[msg.author_id]["auth_user_id"]
                UserShopDict[msg.author_id]["SkinsPanelLayout"] = resp["SkinsPanelLayout"]
                log_time += f"[Api_shop] {format(time.time()-a_time,'.4f')} "

            # 开始画图
            draw_time = time.time()  #计算画图需要的时间
            is_vip = await vip_ck(msg.author_id) #判断用户是否为VIP
            img_ret = {'status':True,'value':None}
            # 每天8点bot遍历完之后会把vip的商店结果图存起来
            shop_path = f"./log/img_temp_vip/shop/{msg.author_id}.png"
            # 如果是vip而且path存在,背景图/登录用户没有更改过,图片缓存时间正确
            if is_vip and (os.path.exists(shop_path)) and is_CacheLatest(msg.author_id):  
                bg_vip_shop = Image.open(shop_path) #直接使用本地已经画好的图片
                bg = copy.deepcopy(bg_vip_shop)
                img_ret['value'] = bg # 放入返回值
            elif is_vip and (msg.author_id in VipShopBgDict): #本地缓存路径不存在，或者缓存过期
                play_currency = await fetch_valorant_point(userdict)#获取用户的vp和rp
                vp = play_currency["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #vp
                rp = play_currency["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]  #R点
                img_ret = await get_shop_img_169(list_shop,vp=vp,rp=rp,bg_img_src=VipShopBgDict[msg.author_id]["background"][0])
            else:# 普通用户/没有自定义图片的vip用户
                img_ret = await get_shop_img_11(list_shop)

            if img_ret['status']: #true
                bg = img_ret['value'] #获取图片
            else:  #出现背景图片违规或其他问题
                await msg.reply(img_ret['value'])
                print(f"[GetShopImg] Au:{msg.author_id} {img_ret['value']}")
                return

            # 获取图片成功，打印画图耗时
            log_time += f"- [Drawing] {format(time.time() - draw_time,'.4f')} - [Au] {msg.author_id}"
            print(log_time)
            # bg.save(f"test.png")  #保存到本地
            imgByteArr = io.BytesIO()
            bg.save(imgByteArr, format='PNG')
            imgByte = imgByteArr.getvalue()
            dailyshop_img_src = await bot_upimg.client.create_asset(imgByte)  # 上传图片
            # 结束shop的总计时
            end = time.perf_counter()
            # 结果为浮点数，保留两位小数
            shop_using_time = format(end - start, '.2f')
            
            # 商店的图片
            cm = CardMessage()
            c = Card(color='#fb4b57')
            c.append(Module.Header(f"玩家 {player_gamename} 的每日商店！"))
            c.append(Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {shop_using_time}s"))
            c.append(Module.Container(Element.Image(src=dailyshop_img_src)))
            cm.append(c)
            
            #皮肤评分和评价，用户不在rate_err_user里面才显示(在评论中发表违规言论的用户)
            if not check_rate_err_user(msg.author_id):
                cm = await get_shop_rate_cm(list_shop,msg.author_id,cm=cm)
                end = time.perf_counter()#计算获取评分的时间
            # 更新消息
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            # 结束，打印结果
            print(f"[{GetTime()}] Au:{msg.author_id} daily_shop reply successful [{shop_using_time}/{format(end - start, '.2f')}]")
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
        
    except requester.HTTPRequester.APIRequestFailed as result: #卡片消息发送失败
        await APIRequestFailed_Handler("shop",traceback.format_exc(),msg,bot,send_msg,cm)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] shop\n```\n{traceback.format_exc()}\n```"
        cm2 = CardMessage()
        c = Card(color='#fb4b57')
        if "SkinsPanelLayout" in str(result):
            print(err_str,resp)
            text = f"键值错误，需要重新登录"
            btext = f"KeyError:{result}, please re-login\n如果此问题重复出现，请[联系开发者](https://kook.top/gpbTwZ)"
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.lagging, size='sm')))
            c.append(Module.Context(Element.Text(btext, Types.Text.KMD)))
            cm2.append(c)
            await upd_card(send_msg['msg_id'], cm2, channel_type=msg.channel_type)
        else:
            await BaseException_Handler("shop",traceback.format_exc(),msg,bot,send_msg,cm)


# 判断夜市有没有开
NightMarketOff = False
ValItersEmoji ={
    'Deluxe':'3986996654014459/98pGl6Tixp074074',
    'Premium':'3986996654014459/ZT2et4zNSa074074',
    'Select':'3986996654014459/HOGPjGnwoT074074',
    'Ultra':'3986996654014459/5MPICFpxsa074074',
    'Exclusive':'3986996654014459/5pj9z3T8sL074074'
}
# 获取夜市
@bot.command(name='night', aliases=['NIGHT'])
async def get_night_market(msg: Message, *arg):
    logging(msg)
    global NightMarketOff
    if arg != ():
        await msg.reply(f"`/night`命令不需要参数。您是否想`/login`？")
        return
    elif Login_Forbidden:
        await Login_Forbidden_send(msg)
        return
    elif NightMarketOff:
        await msg.reply(f"夜市暂未开放！请等开放了之后再使用本命令哦~")
        return
    
    send_msg = None
    try:
        if msg.author_id in UserAuthDict:
            reau = await check_re_auth("夜市", msg)
            if reau == False: return  #如果为假说明重新登录失败
            
            # 重新获取token成功了再提示正在获取夜市
            cm0 = CardMessage()  #卡片侧边栏颜色
            text = "正在尝试获取您的夜市"
            c = Card(color='#fb4b57')
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.duck, size='sm')))
            c.append(Module.Context(Element.Text("阿狸正在施法，很快就好啦！", Types.Text.KMD)))
            cm0.append(c)
            if isinstance(reau, dict):  #如果传过来的是一个dict，说明重新登录成功且发送了消息
                await upd_card(reau['msg_id'], cm0, channel_type=msg.channel_type)
                send_msg = reau
            else:
                send_msg = await msg.reply(cm0)  #记录消息id用于后续更新
            
            #计算获取时间
            start = time.perf_counter() #开始计时
            auth = UserAuthDict[msg.author_id]['auth']
            userdict = {
                'auth_user_id': auth.user_id,
                'access_token': auth.access_token,
                'entitlements_token': auth.entitlements_token
            }
            resp = await fetch_daily_shop(userdict) #获取商店（夜市是相同接口）
            if "BonusStore" not in resp: # 如果没有这个字段，说明夜市取消了
                NightMarketOff = False
                cm1 = CardMessage()
                text = f"嗷~ 夜市已关闭 或 Api没能正确返回结果"
                c = Card(color='#fb4b57')
                c.append(
                    Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.whats_that, size='sm')))
                c.append(Module.Context(Element.Text("night_market closed! 'BonusStore' not in resp", Types.Text.KMD)))
                cm1.append(c)
                await upd_card(send_msg['msg_id'], cm1, channel_type=msg.channel_type)
                print("[night_market] night_market closed! 'BonusStore' not in resp")
                return
            
            timeout = resp["BonusStore"]["BonusStoreRemainingDurationInSeconds"] #剩余时间
            timeout = time.strftime("%d %H:%M:%S", time.gmtime(timeout))  #将秒数转为标准时间
            
            cm = CardMessage()
            c = Card(color='#fb4b57')
            c.append(
                Module.Header(
                    f"玩家 {UserTokenDict[msg.author_id]['GameName']}#{UserTokenDict[msg.author_id]['TagLine']} 的夜市！"))
            for Bonus in resp["BonusStore"]["BonusStoreOffers"]:
                skin = fetch_skin_bylist(Bonus["Offer"]["OfferID"])
                skin_icon = skin["data"]['levels'][0]["displayIcon"]
                skin_name = skin["data"]["displayName"]
                for it in ValSkinList['data']:#查找皮肤的等级
                    if it['levels'][0]['uuid'] == Bonus["Offer"]["OfferID"]:
                        res_iters = fetch_item_iters_bylist(it['contentTierUuid'])
                        break
                iter_emoji = ValItersEmoji[res_iters['data']['devName']]
                basePrice = Bonus["Offer"]["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"] #原价
                discPercent = Bonus["DiscountPercent"] # 打折百分比
                discPrice = Bonus["DiscountCosts"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"] #打折后的价格
                text = f"(emj){res_iters['data']['uuid']}(emj)[{iter_emoji}] {skin_name}\n"
                text+= f"(emj)vp(emj)[3986996654014459/qGVLdavCfo03k03k] {discPrice} ~~{basePrice}~~ {discPercent}%Off"
                #c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=skin_icon, size='sm')))
                c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
            
            # 结束计时
            end = time.perf_counter()
            using_time = format(end - start, '.2f')
            c.append(Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {using_time}s"))
            cm.append(c)
            #print(json.dumps(cm2))
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            print(f"[night_market] Au:{msg.author_id} night_market reply success! [{using_time}]")
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
        
    except requester.HTTPRequester.APIRequestFailed as result: #卡片消息发送失败
        await APIRequestFailed_Handler("night",traceback.format_exc(),msg,bot,send_msg,cm)
    except Exception as result: # 其他错误
        await BaseException_Handler("night",traceback.format_exc(),msg,bot,send_msg,cm)


# 设置全局变量，打开/关闭夜市
@bot.command(name='open-nm')
async def open_night_market(msg: Message, *arg):
    logging(msg)
    try:
        if msg.author_id == master_id:
            global NightMarketOff
            if NightMarketOff:
                NightMarketOff = False
            else:
                NightMarketOff = True
                
            await msg.reply(f"夜市状态修改！NightMarketOff: {NightMarketOff}")
        else:
            await msg.reply("您没有权限执行本命令！")
    except:
        err_str = f"ERR! [{GetTime()}] open-nm\n```\n{traceback.format_exc()}\n```"
        await msg.reply(f"{err_str}")
        print(err_str)
        

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
    elif Login_Forbidden:
        await Login_Forbidden_send(msg)
        return
    send_msg = None
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
            else: # 如果不需要重新登录，则直接发消息
                send_msg = await msg.reply(cm)  #记录消息id用于后续更新

            auth = UserAuthDict[msg.author_id]['auth']
            userdict = {
                'auth_user_id': auth.user_id,
                'access_token': auth.access_token,
                'entitlements_token': auth.entitlements_token
            }
            resp = await fetch_player_loadout(userdict)  #获取玩家装备栏
            #print(resp)
            player_card = await fetch_playercard_uuid(resp['Identity']['PlayerCardID'])  #玩家卡面id
            player_title = await fetch_title_uuid(resp['Identity']['PlayerTitleID'])  #玩家称号id
            if 'data' not in player_card or player_card['status'] != 200:
                player_card = {'data':{'wideArt':'https://img.kookapp.cn/assets/2022-09/PDlf7DcoUH0ck03k.png'}}
                print(f"ERR![player_card]  Au:{msg.author_id} uuid:{resp['Identity']['PlayerCardID']}")
            if 'data' not in player_title or player_title['status'] != 200:
                player_title = {'data':{
                    "displayName":f"未知玩家卡面uuid！\nUnknow uuid: `{resp['Identity']['PlayerTitleID']}`"
                }}
                print(f"ERR![player_title] Au:{msg.author_id} uuid:{resp['Identity']['PlayerTitleID']}")
            #print(player_card,player_title)
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

    except requester.HTTPRequester.APIRequestFailed as result: #卡片消息发送失败
        await APIRequestFailed_Handler("uinfo",traceback.format_exc(),msg,bot,send_msg,cm)
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] uinfo\n```\n{traceback.format_exc()}\n```"
        cm2 = CardMessage()
        res_str = str(result)
        if "Identity" in res_str or "Balances" in res_str:
            print(err_str)
            text = f"键值错误，需要重新登录"
            c = Card(color='#fb4b57')
            c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=icon_cm.lagging, size='sm')))
            c.append(Module.Context(Element.Text(f"KeyError:{result}, please re-login", Types.Text.KMD)))
            cm2.append(c)
            await upd_card(send_msg['msg_id'], cm2, channel_type=msg.channel_type)
        else:
            await BaseException_Handler("uinfo",traceback.format_exc(),msg,bot,send_msg,cm)

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

#用户给皮肤评分的选择列表
UserRtsDict = {}
# 设置rate的错误用户
@bot.command(name='ban-r')
async def set_rate_err_user(msg:Message,user_id:str):
    global SkinRateDict
    if msg.author_id != master_id:
        await msg.reply(f"您没有权限执行此命令！")
        return
    if user_id in SkinRateDict['err_user']:
        await msg.reply(f"该用户已在SkinRateDict['err_user']列表中")
    elif user_id in SkinRateDict['data']:
        for skin,info in SkinRateDict['data'][user_id].items():
            i=0
            while(i<len(SkinRateDict['rate'][skin]['cmt'])) :
                #找到这条评论，将其删除
                if info['cmt'] == SkinRateDict['rate'][skin]['cmt'][i]:
                    SkinRateDict['rate'][skin]['cmt'].pop(i)
                    break
                i+=1
            #如果删除评论之后，链表为空，说明该链表中只有这一个评论
            if not SkinRateDict['rate'][skin]['cmt']:#空列表视为false
                #删除掉这个皮肤的rate
                del SkinRateDict['rate'][skin]
                
        #删除完该用户的所有评论之后，将其放入err_user        
        temp_user = copy.deepcopy(SkinRateDict['data'][user_id])
        del SkinRateDict['data'][user_id]
        SkinRateDict['err_user'][user_id]=temp_user
        #写入文件
        with open("./log/ValSkinRate.json", 'w', encoding='utf-8') as fw2:
            json.dump(SkinRateDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        await msg.reply(f"用户 {user_id} 已被加入SkinRateDict['err_user']列表")
        print(f"[rate_err_user] add Au:{user_id}, file save success")
 
# 每月1日删除用户
@bot.task.add_cron(day=1, timezone="Asia/Shanghai")
async def clear_rate_err_user():
    global SkinRateDict
    SkinRateDict['err_user']={}
    #写入文件
    with open("./log/ValSkinRate.json", 'w', encoding='utf-8') as fw2:
        json.dump(SkinRateDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
    print(f"[BOT.TASK] clear_rate_err_user at {GetTime()}")
        
# 给一个皮肤评分（灵感来自微信小程序”瓦的小卖铺“）
@bot.command(name="rate", aliases=['评分'])
async def rate_skin_add(msg: Message, *arg):
    logging(msg)
    if check_rate_err_user(msg.author_id):
        await msg.reply(f"您有过不良评论记录，阿狸现已不允许您使用相关功能\n后台存放了所有用户的评论内容和评论时间。在此提醒，请不要在评论的时候发送不雅言论！")
        return
    elif arg == ():
        await msg.reply(f"你没有提供皮肤参数！skin: `{arg}`\n正确用法：`/rate 您想评价的皮肤名`")
        return
    try:
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
        
        UserRtsDict[msg.author_id] = retlist
        sum = 0
        usrin = msg.author_id in SkinRateDict['data']
        if usrin:
            sum = len(SkinRateDict['data'][msg.author_id])
        i = 0
        text = "```\n"  #模拟一个选择表
        for w in retlist:
            text += f"[{i}] - {w['skin']['displayName']}  - VP {w['price']}"
            i += 1
            if usrin and w['skin']['lv_uuid'] in SkinRateDict['data'][msg.author_id]:
                text+=" √\n"
            elif w['skin']['lv_uuid'] in SkinRateDict['rate']:
                text+=" +\n"
            else:
                text+=" -\n"
            
        text += "```"
        cm = CardMessage()
        c = Card(Module.Header(f"查询到 {name} 相关皮肤如下"),
                 Module.Section(Element.Text(text, Types.Text.KMD)),
                 Module.Section(Element.Text("请使用以下命令对皮肤进行评分; √代表您已评价过该皮肤，+代表已有玩家评价，-代表无人评价\n", Types.Text.KMD)))
        text1  = "```\n/rts 序号 评分 吐槽\n"
        text1 += "序号：上面列表中的皮肤序号\n"
        text1 += "评分：给皮肤打分，范围0~100\n"
        text1 += "吐槽：说说你对这个皮肤的看法\n"
        text1 += "吐槽的时候请注意文明用语！\n```\n"
        text1 +=f"您已经评价过了 {sum} 个皮肤"
        c.append(Module.Section(Element.Text(text1, Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)
        
    except requester.HTTPRequester.APIRequestFailed as result: #卡片消息发送失败
        await APIRequestFailed_Handler("rate",traceback.format_exc(),msg,bot,None,cm)
    except Exception as result: # 其他错误
        await BaseException_Handler("rate",traceback.format_exc(),msg,bot,None,cm)
        
#选择皮肤（这个命令必须跟着上面的命令用）
@bot.command(name="rts")
async def rate_skin_select(msg: Message, index: str = "err", rating:str = "err",*arg):
    logging(msg)
    if check_rate_err_user(msg.author_id):
        await msg.reply(f"您有过不良评论记录，阿狸现已不允许您使用相关功能\n后台存放了所有用户的评论内容和评论时间。在此提醒，请不要在评论的时候发送不雅言论！")
        return
    elif index == "err" or '-' in index:
        await msg.reply(f"参数不正确！请正确选择您需要评分的皮肤序号\n正确用法：`/rts 序号 评分 吐槽`")
        return
    elif rating == "err" or '-' in rating:
        await msg.reply(f"参数不正确！请正确提供您给该皮肤的打分，范围0~100\n正确用法：`/rts 序号 评分 吐槽`")
        return
    elif arg == ():
        await msg.reply(f"您似乎没有评论此皮肤呢，多少说点什么吧~\n正确用法：`/rts 序号 评分 吐槽`")
        return
    try:
        if msg.author_id in UserRtsDict:
            _index = int(index)  #转成int下标（不能处理负数）
            _rating = int(rating) #转成分数
            if _index >= len(UserRtsDict[msg.author_id]):  #下标判断，避免越界
                await msg.reply(f"您的选择越界了！请正确填写序号")
                return
            elif _rating <0 or _rating>100:
                await msg.reply(f"您的评分有误，正确范围为0~100")
                return

            S_skin = UserRtsDict[msg.author_id][_index]
            skin_uuid = S_skin['skin']['lv_uuid']
            comment = " ".join(arg)#用户对此皮肤的评论
            text1="";text2=""
            # 如果rate里面没有，先创立键值
            if skin_uuid not in SkinRateDict['rate']:
                SkinRateDict['rate'][skin_uuid] = {}
                SkinRateDict['rate'][skin_uuid]['pit'] = 0
                SkinRateDict['rate'][skin_uuid]['cmt'] = list()
            if SkinRateDict['rate'][skin_uuid]['pit']==0:
                point = float(_rating)
            elif abs(float(_rating)-SkinRateDict['rate'][skin_uuid]['pit']) <= 32: 
                #用户的评分和皮肤平均分差值不能超过32，避免有人乱刷分
                point = (SkinRateDict['rate'][skin_uuid]['pit'] + float(_rating))/2
            else:#差值过大，不计入皮肤平均值
                point = SkinRateDict['rate'][skin_uuid]['pit']
                text2+=f"由于您的评分和皮肤平均分差值大于32，所以您的评分不会计入皮肤平均分，但您的评论会进行保留\n"
            # 设置皮肤的评分和评论
            SkinRateDict['rate'][skin_uuid]['pit'] = point
            SkinRateDict['rate'][skin_uuid]['name']=S_skin['skin']['displayName']
            SkinRateDict['rate'][skin_uuid]['cmt'].append(comment)
            # data内是记录xx用户评论了xx皮肤
            if msg.author_id in SkinRateDict['data']:
                #如果用户之前已经评论过这个皮肤，则需要删除之前的评论
                if skin_uuid in SkinRateDict['data'][msg.author_id]:
                    i=0
                    while(i<len(SkinRateDict['rate'][skin_uuid]['cmt'])) :
                        #找到这条评论，将其删除
                        if SkinRateDict['data'][msg.author_id][skin_uuid]['cmt'] == SkinRateDict['rate'][skin_uuid]['cmt'][i]:
                            SkinRateDict['rate'][skin_uuid]['cmt'].pop(i)
                            text1+="更新"
                            break
                        i+=1
            else:#用户不存在，创建用户的dict
                SkinRateDict['data'][msg.author_id] = {}
            #无论用户在不在，都设置键值
            SkinRateDict['data'][msg.author_id][skin_uuid] = {}
            SkinRateDict['data'][msg.author_id][skin_uuid]['name'] = S_skin['skin']['displayName']
            SkinRateDict['data'][msg.author_id][skin_uuid]['cmt']  = comment
            SkinRateDict['data'][msg.author_id][skin_uuid]['pit']  = point
            SkinRateDict['data'][msg.author_id][skin_uuid]['time']  = GetTime()
            SkinRateDict['data'][msg.author_id][skin_uuid]['msg_id'] = msg.id

            # 写入文件
            with open("./log/ValSkinRate.json", 'w', encoding='utf-8') as fw2:
                json.dump(SkinRateDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)

            #del UserRtsDict[msg.author_id]  #删除选择页面中的list
            text1+= f"评价成功！{S_skin['skin']['displayName']}"
            text2+= f"您的评分：{_rating}\n"
            text2+= f"皮肤平均分：{SkinRateDict['rate'][skin_uuid]['pit']}\n"
            text2+= f"您的评语：{comment}"
            cm = CardMessage()
            c=Card(Module.Header(text1),
                   Module.Divider(),
                   Module.Section(Element.Text(text2,Types.Text.KMD)))
            cm.append(c)
            # 设置成功并删除list后，再发送提醒事项设置成功的消息
            await msg.reply(cm)
            print(f"[rts] Au:{msg.author_id} ", text1)
        else:
            await msg.reply(f"您需要执行 `/rate 皮肤名` 来查找皮肤\n再使用 `/rts` 进行选择")
            
    except requester.HTTPRequester.APIRequestFailed as result: #卡片消息发送失败
        await APIRequestFailed_Handler("rts",traceback.format_exc(),msg,bot,None,cm)
    except Exception as result: # 其他错误
        await BaseException_Handler("rts",traceback.format_exc(),msg,bot,None,cm)

# 查看昨日牛人/屌丝
@bot.command(name="kkn")
async def rate_skin_select(msg: Message):
    logging(msg)
    if check_rate_err_user(msg.author_id):
        await msg.reply(f"您有过不良评论记录，阿狸现已不允许您使用相关功能\n后台存放了所有用户的评论内容和评论时间。在此提醒，请不要在评论的时候发送不雅言论！")
        return
    try:
        cm = CardMessage()
        c=Card(Module.Header(f"来看看昨日天选之子和丐帮帮主吧！"),Module.Divider())
        # best
        text=""
        c.append(Module.Section(Element.Text(f"**天选之子** 综合评分 {SkinRateDict['kkn']['best']['pit']}",Types.Text.KMD)))
        for sk in SkinRateDict['kkn']['best']['skin']:
            if sk in SkinRateDict['rate']:
                skin_name = f"「{SkinRateDict['rate'][sk]['name']}」"
                text+=f"%-50s\t\t评分: {SkinRateDict['rate'][sk]['pit']}\n"%skin_name
        c.append(Module.Section(Element.Text(text,Types.Text.KMD)))
        c.append(Module.Divider())
        # worse
        text=""
        c.append(Module.Section(Element.Text(f"**丐帮帮主** 综合评分 {SkinRateDict['kkn']['worse']['pit']}",Types.Text.KMD)))
        for sk in SkinRateDict['kkn']['worse']['skin']:
            if sk in SkinRateDict['rate']:
                skin_name = f"「{SkinRateDict['rate'][sk]['name']}」"
                text+=f"%-50s\t\t评分: {SkinRateDict['rate'][sk]['pit']}\n"%skin_name
        c.append(Module.Section(Element.Text(text,Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)
        
        # 写入文件(这里保存是为了增多保存次数)
        with open("./log/ValSkinRate.json", 'w', encoding='utf-8') as fw2:
            json.dump(SkinRateDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"[kkn] SkinRateDict save success!")
    except requester.HTTPRequester.APIRequestFailed as result: #卡片消息发送失败
        await APIRequestFailed_Handler("rts",traceback.format_exc(),msg,bot,None,cm)
    except Exception as result: # 其他错误
        await BaseException_Handler("rts",traceback.format_exc(),msg,bot,None,cm)


#用户选择列表
UserStsDict = {}
# 皮肤商店提醒记录
with open("./log/UserSkinNotify.json", 'r', encoding='utf-8') as frsi:
    SkinNotifyDict = json.load(frsi)

# 检查用户是否在错误用户里面
async def check_notify_err_user(msg:Message):
    """Return(bool):
     - True: user in SkinNotifyDict['err_user']
     - False: user not in, everythings is good
    """
    global SkinNotifyDict
    if msg.author_id in SkinNotifyDict['err_user']:
        try:
            user = await bot.client.fetch_user(msg.author_id)
            await user.send(f"这是一个私聊测试，请忽略此条消息")#先测试是否能发私聊
            # 可以发起，在err_user列表中删除该用户
            del SkinNotifyDict['err_user'][msg.author_id]
            return False 
        except:
            err_cur = str(traceback.format_exc())
            err_str = f"ERR![{GetTime()}] err_Au:{msg.author_id} user.send\n```\n{err_cur}\n```"
            if '屏蔽' in err_cur or '无法发起' in err_cur:
                await msg.reply(f"您之前屏蔽了阿狸，或阿狸无法向您发起私信\n您的皮肤提醒信息已经被`删除`，请在解除对阿狸的屏蔽后重新操作！\n{err_str}")
            else:
                err_str+="\n如果此错误多次出现，请[联系](https://kook.top/gpbTwZ)开发者"
                await msg.reply(err_str)
            # 不管出现什么错误，都返回True代表无法私信
            return True
    else:
        return False
    

#独立函数，为了封装成命令+定时
async def auto_skin_notify():
    global SkinNotifyDict, SkinRateDict, UserShopDict
    try:
        print(f"[BOT.TASK.NOTIFY] Start at {GetTime()}")  #开始的时候打印一下
        UserShopDict = {}#清空用户的商店
        #清空昨日最好/最差用户的皮肤表
        SkinRateDict["kkn"] = copy.deepcopy(SkinRateDict["cmp"])
        SkinRateDict["cmp"]["best"]["skin"]=list()
        SkinRateDict["cmp"]["best"]["pit"]=0
        SkinRateDict["cmp"]["worse"]["skin"]=list()
        SkinRateDict["cmp"]["worse"]["pit"]=100
        print("[BOT.TASK.NOTIFY] SkinRateDict/UserShopDict clear, sleep(15)")
        #睡15s再开始遍历（避免时间不准）
        await asyncio.sleep(15)
        print("[BOT.TASK.NOTIFY] auto_skin_notify Start")
        #加载vip用户列表
        VipUserD = copy.deepcopy(VipUserDict)
        err_count = 0 # 设置一个count来计算出错的用户数量
        log_vip_failed  = f"[BOT.TASK.NOTIFY] reauthorize failed  = VAu: "
        log_vip_not_login = f"[BOT.TASK.NOTIFY] not_in UserAuthDict = VAu: "
        #先遍历vip用户列表，获取vip用户的商店
        for vip, uinfo in VipUserD.items():
            try:
                user = await bot.client.fetch_user(vip)
                if vip in UserAuthDict:
                    if await check_re_auth("定时获取玩家商店", vip) == True:  # 重新登录,如果为假说明重新登录失败
                        start = time.perf_counter()  #开始计时
                        auth = UserAuthDict[vip]['auth']
                        userdict = {
                            'auth_user_id': auth.user_id,
                            'access_token': auth.access_token,
                            'entitlements_token': auth.entitlements_token
                        }
                        a_time = time.time()
                        resp = await fetch_daily_shop(userdict)  # 获取每日商店
                        
                        # 判断夜市有没有开，只会判断一次
                        global NightMarketOff #true代表夜市没有开启
                        if NightMarketOff and "BonusStore" in resp:#夜市字段存在
                            NightMarketOff = False #夜市开启！
                        
                        list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
                        timeout = resp["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]  #剩余时间
                        timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  #将秒数转为标准时间
                        log_time = f"[Api_shop] {format(time.time()-a_time,'.4f')} "
                        await check_shop_rate(vip,list_shop)#计算用户商店得分
                        #vip用户会提前缓存当日商店，需要设置uuid来保证是同一个游戏用户
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

                        log_time += f"- [Drawing] {format(time.time() - draw_time,'.4f')}  - [Au] {vip}"
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
                        print(f"[BOT.TASK.NOTIFY] [{GetTime()}] VAu:{vip} notify_shop success [{using_time}]")
                    else:  #reauthorize failed!
                        log_vip_failed+=f"({vip})"
                        await user.send(f"尊贵的vip用户，您已登录，但是登录信息失效了。请您重新`login`以查询每日商店\n注：这是无可避免的小概率事件")
                else:  #不在auth里面说明没有登录
                    log_vip_not_login+=f"({vip})"
                    await user.send(f"尊贵的vip用户，请您`login`来让每日商店提醒生效哦~\n[注] 如果您在早8:10之后收到此条消息，请忽略。开发者在进行bug测试")
            except Exception as result:  #这个是用来获取单个用户的问题的
                err_cur = str(traceback.format_exc())
                err_str = f"ERR![BOT.TASK.NOTIFY] VAu:{vip} vip_user.send\n```\n{err_cur}\n```"
                print(err_str)
                err_count+=1
                if '屏蔽' in err_cur or '无法发起' in err_cur:
                    SkinNotifyDict['err_user'][vip] = GetTime()
                    err_str+=f"\nadd to ['err_user']"
                
                await bot.client.send(debug_ch, err_str)  #发送消息到debug频道
        #打印vip的log信息
        print(log_vip_failed)
        print(log_vip_not_login)
        
        # 再遍历所有用户的皮肤提醒
        log_failed  =   f"[BOT.TASK.NOTIFY] reauthorize failed  = Au: "
        log_not_login = f"[BOT.TASK.NOTIFY] not_in UserAuthDict = Au: "
        temp_SkinNotifyDict = copy.deepcopy(SkinNotifyDict)
        for aid, skin in temp_SkinNotifyDict['data'].items():
            try:
                user = await bot.client.fetch_user(aid)
                if aid in UserAuthDict:
                    if await check_re_auth("定时获取玩家商店", aid) == True:  # 重新登录,如果为假说明重新登录失败
                        auth = UserAuthDict[aid]['auth']
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
                            await check_shop_rate(vip,list_shop)#计算非vip用户商店得分

                        # 然后再遍历列表查看是否有提醒皮肤
                        # 关于下面这一行参考 https://img.kookapp.cn/assets/2022-08/oYbf8PM6Z70ae04s.png
                        target_skin = [val for key, val in skin.items() if key in list_shop]
                        for name in target_skin:
                            print(f"[BOT.TASK.NOTIFY] Au:{aid} auto_skin_notify = {name}")
                            await user.send(f"[{GetTime()}] 您的每日商店刷出`{name}`了，请上号查看哦！")
                        # 打印这个说明这个用户正常遍历完了
                        print(f"[BOT.TASK.NOTIFY] Au:{aid} auto_skin_notify = None")
                    else:  #reauthorize failed!
                        log_failed+=f"({aid})"
                        await user.send(f"您已登录，但是登录信息失效了。请您重新`login`以查询每日商店\n注：这是无可避免的小概率事件")
                else:  #不在auth里面说明没有登录
                    log_not_login+=f"({aid})"
                    await user.send(
                        f"您设置了皮肤提醒，却没有登录！请尽快`login`哦~\n[悄悄话] 阿狸会保存vip用户的登录信息，有兴趣[支持一下](https://afdian.net/a/128ahri?tab=shop)吗？\n[注] 如果您在早8:10之后收到此条消息，请忽略。开发者在进行bug测试")
            except Exception as result:  #这个是用来获取单个用户的问题的
                err_cur = str(traceback.format_exc())
                err_str = f"ERR![BOT.TASK.NOTIFY] Au:{aid} user.send\n```\n{err_cur}\n```"
                err_count+=1
                if '屏蔽' in err_cur or '无法发起' in err_cur:
                    del SkinNotifyDict['data'][aid] #直接粗暴解决，删除用户
                    SkinNotifyDict['err_user'][aid] = GetTime()
                    err_str+=f"\ndel SkinNotifyDict['data'][{aid}],add to ['err_user']"
                    
                print(err_str)
                await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道

        #打印普通用户的log信息
        print(log_failed)
        print(log_not_login)
        #完成遍历后，如果有删除才重新保存dict
        if temp_SkinNotifyDict != SkinNotifyDict:
            with open("./log/UserSkinNotify.json", 'w', encoding='utf-8') as fw1:
                json.dump(SkinNotifyDict, fw1, indent=2, sort_keys=True, ensure_ascii=False)
            print("[BOT.TASK.NOTIFY] save SkinNotifyDict")
            
        # 将当日最高最低用户写入文件
        with open("./log/ValSkinRate.json", 'w', encoding='utf-8') as fw2:
            json.dump(SkinRateDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)            
        finish_str = f"[BOT.TASK.NOTIFY] Finish at {GetTime()} [ERR {err_count}]"
        print(finish_str)  #正常完成
        await bot.client.send(debug_ch, finish_str)  #发送消息到debug频道
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] auto_skin_notify\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道


@bot.task.add_cron(hour=8, minute=0, timezone="Asia/Shanghai")
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
        if await check_notify_err_user(msg):
            return
        # 检查用户的提醒栏位
        vip_status = await vip_ck(msg.author_id)
        if msg.author_id in SkinNotifyDict['data'] and not vip_status:
            if len(SkinNotifyDict['data'][msg.author_id]) > 2:
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
            num = int(n)  #转成int下标（不能处理负数）
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
            if msg.author_id not in SkinNotifyDict['data']:
                SkinNotifyDict['data'][msg.author_id] = {}
                SkinNotifyDict['data'][msg.author_id][S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            else:  #如果存在了就直接在后面添加
                SkinNotifyDict['data'][msg.author_id][S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            # print(SkinNotifyDict['data'][msg.author_id])

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
        if await check_notify_err_user(msg):
            return
        if msg.author_id in SkinNotifyDict['data']:
            text = "```\n"
            for skin, name in SkinNotifyDict['data'][msg.author_id].items():
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
        if await check_notify_err_user(msg):
            return
        global SkinNotifyDict
        if msg.author_id in SkinNotifyDict['data']:
            if uuid in SkinNotifyDict['data'][msg.author_id]:
                print(f"notify-d - Au:{msg.author_id} = {uuid} {SkinNotifyDict['data'][msg.author_id][uuid]}")
                await msg.reply(f"已删除皮肤：`{SkinNotifyDict['data'][msg.author_id][uuid]}`")
                del SkinNotifyDict['data'][msg.author_id][uuid]
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

@bot.command(name='lf')
async def Login_Forbidden_Change(msg:Message):
    logging(msg)
    if msg.author_id == master_id:
        global Login_Forbidden
        if Login_Forbidden == True:
            Login_Forbidden = False
        else:
            Login_Forbidden = True
        
        await msg.reply(f"Update Login_Forbidden status: {Login_Forbidden}")
    else:
        await msg.reply(f"您没有权限执行此命令！")
        return
    
# 显示当前阿狸加入了多少个服务器，以及用户数量
@bot.command(name='log-list',aliases=['log-l','log'])
async def bot_log_list(msg:Message,*arg):
    logging(msg)
    try:
        if msg.author_id == master_id:
            retDict = await log_bot_list(msg)
            i=1
            text_name = "No  服务器名\n"
            text_user = "用户数\n"
            for gu,ginfo in retDict['guild']['data'].items():
                #Gret = await guild_view(gu)
                Gname = ginfo['name']
                if len(Gname) >12:
                    text = Gname[0:11]
                    text += "…"
                    Gname = text
                # 追加text
                text_name+=f"[{i}]  {Gname}\n"
                text_user+=f"{len(ginfo['user'])}\n"
                i+=1
            
            cm = CardMessage()
            c = Card(
                Module.Header(f"来看看阿狸当前的用户记录吧！"),
                Module.Context(f"服务器总数: {retDict['guild']['guild_total']}  活跃服务器: {retDict['guild']['guild_active']}  用户数: {retDict['user']['user_total']}  cmd: {retDict['cmd_total']}"),
                Module.Divider())
            log_img_src = await bot_upimg.client.create_asset("../screenshot/log.png")
            c.append(Module.Container(Element.Image(src=log_img_src)))
            c.append(
                Module.Section(
                    Struct.Paragraph(2,
                               Element.Text(f"{text_name[:5000]}",Types.Text.KMD),
                               Element.Text(f"{text_user[:5000]}",Types.Text.KMD))))#限制字数才能发出来
            cm.append(c)
            await msg.reply(cm)
        else:
            await msg.reply(f"您没有权限执行此命令！")
    except:
        err_str = f"ERR! [{GetTime()}] log-list\n```\n{traceback.format_exc()}\n```"
        await msg.reply(f"{err_str}")
        print(err_str)

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

    if Login_Forbidden:
        print(f"[BOT.TASK] Login_Forbidden: {Login_Forbidden}")
        return
    
    print("[BOT.TASK] loading cookie start")
    global UserAuthDict
    log_str_success = "[BOT.TASK] load cookie success  = Au:"
    log_str_failed =  "[BOT.TASK] load cookie failed!  = Au:"
    log_not_exits =   "[BOT.TASK] cookie path not exists = Au:"
    #遍历用户列表
    for user, uinfo in VipUserDict.items():
        cookie_path = f"./log/cookie/{user}.cke"
        #如果路径存在，那么说明已经保存了这个vip用户的cookie
        if os.path.exists(cookie_path):
            auth = RiotAuth()  #新建一个对象
            auth._cookie_jar.load(cookie_path)  #加载cookie
            ret_bool = await auth.reauthorize()  #尝试登录
            if ret_bool:  # True登陆成功
                UserAuthDict[user] = { "auth":auth,"2fa":False}  #将对象插入
                log_str_success +=f"({user})"
                #print(f"[BOT.TASK] Au:{user} - load cookie success!")
                #不用重新修改UserTokenDict里面的游戏名和uuid
                #因为UserTokenDict是在login的时候保存的，只要用户没有切换账户
                #那么玩家id和uuid都是不会变化的，也没必要重新加载
            else:
                log_str_failed += f"({user}) "
                #print(f"[BOT.TASK] Au:{user} - load cookie failed!")
                continue
        else:
            log_not_exits += f"({user}) "
            continue
    #结束任务
    print(log_str_success)#打印正常的用户
    print(log_str_failed) #打印失败的用户
    print(log_not_exits)  #打印路径不存在的用户
    print("[BOT.TASK] loading cookie finished")

# 开机的时候打印一次时间，记录重启时间
print(f"Start at: [%s]" % start_time)
# 开机
bot.run()
