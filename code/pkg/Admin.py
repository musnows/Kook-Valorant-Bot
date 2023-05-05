import json
import traceback
import os
from khl import (Bot, Event, EventTypes, Message, PrivateMessage, requester, Channel)
from khl.card import Card, CardMessage, Element, Module, Types, Struct

from .utils.file.Files import config,_log,start_time
from .utils import Gtime
from .utils.log import BotLog

master_id = config['master_id']
"""机器人开发者用户id"""

def is_admin(user_id:str):
    """是管理员返回True"""
    return user_id == master_id

def init(bot:Bot,bot_upd_img:Bot,debug_ch:Channel):
    """Admin command
    - bot: main bot
    - bot_upd_img: bot for img upload
    - debug_ch: channel obj
    """
    
    @bot.command(name='mem',case_sensitive=False)
    async def proc_memory_cmd(msg: Message, *arg):
        """机器人负载（cpu/内存占用）查询命令"""
        try:
            BotLog.logMsg(msg)
            if is_admin(msg.author_id):
                cm = await BotLog.get_proc_info(start_time)
                await msg.reply(cm)
        except:
            await BotLog.BaseException_Handler("mem",traceback.format_exc(),msg)

    @bot.command(name='log-list', aliases=['log'],case_sensitive=False)
    async def bot_log_list(msg: Message, *arg):
        """显示当前阿狸加入了多少个服务器，以及用户数量"""
        BotLog.logMsg(msg)
        try:
            if not is_admin(msg.author_id):return
            
            retDict = await BotLog.log_bot_list(msg)  # 获取用户/服务器列表
            res_text = await BotLog.log_bot_list_text(retDict)  # 获取text

            cm = CardMessage()
            c = Card(
                Module.Header(f"来看看阿狸当前的用户记录吧！"),
                Module.Context(
                    f"服务器总数: {retDict['guild']['guild_total']}  活跃服务器: {retDict['guild']['guild_active']}  用户数: {retDict['user']['user_total']}  cmd: {retDict['cmd_total']}"
                ), Module.Divider())
            log_img_src = await bot_upd_img.client.create_asset("../screenshot/log.png")
            c.append(Module.Container(Element.Image(src=log_img_src)))
            c.append(
                Module.Section(
                    Struct.Paragraph(2, Element.Text(f"{res_text['name'][:5000]}", Types.Text.KMD),
                                        Element.Text(f"{res_text['user'][:5000]}", Types.Text.KMD))))  #限制字数才能发出来
            cm.append(c)
            await msg.reply(cm)           
        except:
            await BotLog.BaseException_Handler("log-list",traceback.format_exc(),msg)

    _log.info("[Admin] load Admin.py")