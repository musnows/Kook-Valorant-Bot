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

def init(bot:Bot,debug_ch:Channel):
    """
    - bot: main bot
    - debug_ch: channel obj
    - start_time: bot start_time
    """
    @bot.command(name='mem',case_sensitive=False)
    async def proc_memory_cmd(msg: Message, *arg):
        BotLog.logMsg(msg)
        try:
            if is_admin(msg.author_id):
                cm = await BotLog.get_proc_info(start_time)
                await msg.reply(cm)
        except:
            await BotLog.BaseException_Handler("mem",traceback.format_exc(),msg)

    _log.info("[Admin] load Admin.py")