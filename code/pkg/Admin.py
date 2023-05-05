import json
import traceback
import os
from khl import (Bot, Event, EventTypes, Message, PrivateMessage, requester, Channel)
from khl.card import Card, CardMessage, Element, Module, Types, Struct

from .utils.file.Files import config,_log,start_time,LoginForbidden
from .utils.file.FileManage import save_all_file
from .utils import Gtime,KookApi
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
    
    @bot.command(name='kill',case_sensitive=False)
    async def kill_bot_cmd(msg: Message, at_text = '', *arg):
        """`/kill @机器人` 下线bot"""
        BotLog.logMsg(msg)
        try:
            # 如果不是管理员直接退出，不要提示
            if msg.author_id != master_id:
                return
            # 必须要at机器人，或者私聊机器人
            cur_bot = await bot.client.fetch_me()
            if isinstance(msg,PrivateMessage) or f"(met){cur_bot.id}(met)" in at_text:
                # 保存所有文件
                await save_all_file(False)
                cm = CardMessage(Card(Module.Section(
                    Element.Text(f"[KILL] 保存全局变量成功，bot下线\n当前时间：{Gtime.getTime()}", Types.Text.KMD))))
                await msg.reply(cm)
                res = await KookApi.bot_offline()  # 调用接口下线bot
                _log.info(f"KILL | bot-off: {res}\n")
                os._exit(0)  # 退出程序
            else:
                _log.info(f"[kill] invalid kill = {msg.content}")
        except:
            await BotLog.BaseException_Handler("kill",traceback.format_exc(),msg)
    
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
    async def bot_log_list_cmd(msg: Message, *arg):
        """显示当前阿狸加入了多少个服务器，以及用户数量"""
        BotLog.logMsg(msg)
        try:
            if not is_admin(msg.author_id):return
            
            ret_dict = await BotLog.log_bot_list(msg)  # 获取用户/服务器列表
            res_text = await BotLog.log_bot_list_text(ret_dict,bot)  # 获取text

            cm = CardMessage()
            c = Card(
                Module.Header(f"来看看阿狸当前的用户记录吧！"),
                Module.Context(
                    f"服务器总数: {ret_dict['guild']['guild_total']}  活跃服务器: {ret_dict['guild']['guild_active']}  用户数: {ret_dict['user']['user_total']}  cmd: {ret_dict['cmd_total']}"
                ), Module.Divider())
            log_img_src = await bot_upd_img.client.create_asset("../screenshot/log.png")
            c.append(Module.Container(Element.Image(src=log_img_src)))
            c.append(Module.Section(Element.Text(res_text, Types.Text.KMD)))
            # 之前使用的是分列卡片，会导致错位，现在不使用分列
            # c.append(Module.Section(Struct.Paragraph(2, Element.Text(f"{res_text['name'][:5000]}", Types.Text.KMD),
            #                             Element.Text(f"{res_text['user'][:5000]}", Types.Text.KMD))))  #限制字数才能发出来
            cm.append(c)
            await msg.reply(cm)           
        except:
            await BotLog.BaseException_Handler("log-list",traceback.format_exc(),msg)

    @bot.command(name='lf')
    async def login_forbidden_status_cmd(msg: Message):
        """手动设置禁止登录的全局变量状态"""
        try:
            BotLog.logMsg(msg)
            if not is_admin(msg.author_id):return

            global LoginForbidden
            LoginForbidden = False if LoginForbidden else True
            # 回复消息
            cm = await KookApi.get_card_msg(f"Update LoginForbidden status: {LoginForbidden}")
            await msg.reply(cm)
            _log.info(f"Au:{msg.author_id} | LoginForbidden status change to {LoginForbidden}")
        except:
            await BotLog.BaseException_Handler("lf",traceback.format_exc(),msg)

    _log.info("[Admin] load Admin.py")