import copy
import traceback
import os
import time
import asyncio
from khl import (Bot, Event, EventTypes, Message, PrivateMessage, requester, Channel)
from khl.card import Card, CardMessage, Element, Module, Types, Struct

from .utils.file.Files import config,_log,StartTime,SkinRateDict,UserAuthCache,BotUserDict
from .utils.file.FileManage import save_all_file
from .utils.log import BotLog
from .utils.valorant.Reauth import LoginForbidden,NightMarketOff
from .utils import Gtime,KookApi,ShopRate
# 画图缓存
from .utils.ShopImg import weapon_icon_temp_11,weapon_icon_temp_169,skin_level_icon_temp,IMG_MEMORY_CACHE

master_id = config['master_id']
"""机器人开发者用户id"""
IN_ACTIVATE_GUILD = 2
"""将命令数小于此数的服务器视作不活跃服务器，退出"""

def is_admin(user_id:str):
    """是管理员返回True"""
    return user_id == master_id

def init(bot:Bot,bot_upd_img:Bot,debug_ch:Channel):
    """Admin command
    - bot: main bot
    - bot_upd_img: bot for img upload
    - debug_ch: channel obj
    - LoginForbidden: global value from .utils.file.Files
    - NightMarketOff: global value from .utils.file.Files
    """

    @bot.command(name='kill',case_sensitive=False)
    async def kill_bot_cmd(msg: Message, at_text = '', *arg):
        """`/kill @机器人` 下线bot"""
        BotLog.log_msg(msg)
        try:
            # 如果不是管理员直接退出，不要提示
            if not is_admin(msg.author_id):return
            # 必须要at机器人，或者私聊机器人
            cur_bot = await bot.client.fetch_me()
            if isinstance(msg,PrivateMessage) or f"(met){cur_bot.id}(met)" in at_text:
                # 保存所有文件
                await save_all_file(False)
                cm = CardMessage(Card(Module.Section(
                    Element.Text(f"[KILL] 保存全局变量成功，bot下线\n当前时间：{Gtime.get_time()}", Types.Text.KMD))))
                await msg.reply(cm)
                res = "webhook"
                if config['kook']['bot']['ws']: # 用的是ws才需要调用
                    res = await KookApi.bot_offline()  # 调用接口下线bot
                # 打印日志
                _log.info(f"KILL | bot-off: {res}\n")
                os._exit(0)  # 退出程序
            else:
                _log.info(f"[kill] invalid kill = {msg.content}")
        except:
            await BotLog.base_exception_handler("kill",traceback.format_exc(),msg)

    @bot.command(name="ckc",aliases=['ckau'],case_sensitive=False)
    async def check_user_auth_len_cmd(msg: Message,*arg):
        """查询当前有多少用户登录了，以及画图的缓存"""
        BotLog.log_msg(msg)
        try:
            if not is_admin(msg.author_id):return

            c = Card(Module.Header("当前机器人缓存情况"),Module.Context(f"记录于：{Gtime.get_time()}"),Module.Divider())
            text = "EzAuth登录缓存\n```\n"
            text+= f"bot: {len(UserAuthCache['kook'])}\napi: {len(UserAuthCache['api'])}\n```\n"
            text+= "商店画图 内存缓存\n```\n"
            text+= f"皮肤单图  1-1：{len(weapon_icon_temp_11)}\n"
            text+= f"皮肤单图 16-9：{len(weapon_icon_temp_169)}\n"
            text+= f"皮肤等级图：   {len(skin_level_icon_temp)}\n"
            text+= "```"
            if not IMG_MEMORY_CACHE:
                text+= "\n当前内存缓存处于关闭状态"
            c.append(Module.Section(Element.Text(text,Types.Text.KMD)))
            cm = CardMessage(c)
            await msg.reply(cm)
            _log.info(f"Au:{msg.author_id} | ckc reply")
        except:
            await BotLog.base_exception_handler("ckc",traceback.format_exc(),msg)
    
    @bot.command(name='mem',case_sensitive=False)
    async def proc_memory_cmd(msg: Message, *arg):
        """机器人负载（cpu/内存占用）查询命令"""
        try:
            BotLog.log_msg(msg)
            if is_admin(msg.author_id):
                cm = await BotLog.get_proc_info(StartTime)
                await msg.reply(cm)
        except:
            await BotLog.base_exception_handler("mem",traceback.format_exc(),msg)

    @bot.command(name='log-list', aliases=['log'],case_sensitive=False)
    async def bot_log_list_cmd(msg: Message, *arg):
        """显示当前阿狸加入了多少个服务器，以及用户数量"""
        BotLog.log_msg(msg)
        try:
            if not is_admin(msg.author_id):return
            
            ret_dict = await BotLog.log_bot_list()  # 获取用户/服务器列表
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
            await BotLog.base_exception_handler("log-list",traceback.format_exc(),msg)

    @bot.command(name='vstatus')
    async def valorant_global_status_cmd(msg: Message,option="",*arg):
        """手动设置全局变量状态
        - -lf login_forbidden
        - -nm 打开/关闭夜市
        """
        try:
            BotLog.log_msg(msg)
            if not is_admin(msg.author_id):return

            if "-lf" in option.lower():
                lf = LoginForbidden.reverse()
                # 回复消息
                cm = await KookApi.get_card_msg(f"登录状态修改 | LoginForbidden: `{lf}`","该字段为True时，禁止登录命令")
                await msg.reply(cm)
                _log.info(f"Au:{msg.author_id} | LoginForbidden status change to {lf}")
            elif '-nm' in option.lower():
                nm = NightMarketOff.reverse()
                text = f"夜市状态修改 | NightMarketOff: `{nm}`"
                sub_text= "该字段表示夜市是否关闭\nFalse (on,夜市开着) | True (off,夜市关闭)"
                cm = await KookApi.get_card_msg(text,sub_text=sub_text)
                await msg.reply(cm)
                _log.info(f"Au:{msg.author_id} | NightMarketOff status change to {nm}")
            
            else:
                await msg.reply(await KookApi.get_card_msg("选项无效\n* `-lf` LoginForbidden\n* `-nm` NightMarketOff"))
                _log.info(f"Au:{msg.author_id} | invalid option")
        except:
            await BotLog.base_exception_handler("valorant_global_status_cmd",traceback.format_exc(),msg)

    @bot.command(name='ban-r')
    async def ban_rate_user_cmd(msg: Message, user = "",*arg):
        """设置皮肤评价的违规用户"""
        try:
            BotLog.log_msg(msg)            
            if not is_admin(msg.author_id):return
            if not user: return
            
            text = ""
            # 除了可以直接添加用户id，还可以通过@用户的方式添加
            user_id = user if "(met)" not in user else user.replace("(met)","")
            global SkinRateDict
            # 1.判断用户id是否在错误用户中
            if user_id in SkinRateDict['err_user']:
                cm = await KookApi.get_card_msg(f"该用户已在 `SkinRateDict['err_user'] `列表中")
                return await msg.reply(cm)
            # 2.判断用户id是否在评论日志中
            elif user_id in SkinRateDict['data']:
                # 遍历所有皮肤的评论列表，删除违规用户的所有评论
                for skin, info in SkinRateDict['data'][user_id].items():
                    # 找到这条评论，将其删除
                    if not await ShopRate.remove_user_rate(skin, user_id):
                        text += f"删除评论 {skin} [{info['name']}] 错误\n"
                        continue

                # 删除完该用户的所有评论之后，将其放入err_user
                temp_user_dict = copy.deepcopy(SkinRateDict['data'][user_id])
                del SkinRateDict['data'][user_id] # 删除键值
                SkinRateDict['err_user'][user_id] = temp_user_dict
                # 发送信息
                cm = await KookApi.get_card_msg(f"用户 {user_id} 已被加入 `SkinRateDict['err_user']` 列表\n{text}")
                await msg.reply(cm)
                _log.info(f"rate_err_user | ban Au:{user_id}")
            else:
                # 这个用户之前没有评论过，跳过
                cm = await KookApi.get_card_msg(f"用户 {user_id} 没有发表过皮肤评论，请检查id是否正确")
                await msg.reply(cm)
                _log.info(f"rate_err_user | invalid Au:{user_id}")

        except Exception as result:
            await BotLog.base_exception_handler("ban-r", traceback.format_exc(), msg)

    @bot.task.add_cron(day=1, timezone="Asia/Shanghai")
    async def clear_rate_err_user():
        """每月1日删除皮肤评价的违规用户"""
        try:
            global SkinRateDict
            SkinRateDict['err_user'] = {}
            SkinRateDict.save()# 写入文件
            _log.info(f"[BOT.TASK] clear_rate_err_user")
        except:
            _log.exception(f"ERR in clear_rate_err_user")


    @bot.command(name='exit-g',aliases=['退出服务器'])
    async def exit_guild_cmd(msg:Message,guild="",*arg):
        """让机器人退出日志中没有记录过的服务器"""
        send_msg = {'msg_id':''}
        try:
            BotLog.log_msg(msg)
            if not is_admin(msg.author_id):return
            # 指定了服务器
            if guild:
                ret = await KookApi.guild_leave(guild)
                cm = await KookApi.get_card_msg(f"退出服务器 {guild}",f"{ret}")
                await msg.reply(cm)
                _log.info(f"Au:{msg.author_id} | guild_leave {guild} | {ret}")
            # 没有指定，退出不活跃的服务器
            else:
                cm = await KookApi.get_card_msg("收到命令，开始退出不活跃服务器",img_url=KookApi.icon_cm.rgx_card)
                send_msg = await msg.reply(cm)
                start_time = time.perf_counter()
                i,good,err =0,0,0
                guild_text = ""
                for g,ginfo in BotUserDict['guild']['data'].items():
                    try:
                        if ginfo['cmd'] > IN_ACTIVATE_GUILD:
                            continue
                        # 走到这里是不活跃服务器
                        ret = await KookApi.guild_leave(g)
                        if ret['code'] !=0: # 有错误
                            raise Exception(f"guild_leave Err | {ret}")
                        i += 1
                        good+=1
                        guild_text+= f"({g})"
                        await asyncio.sleep(0.4)
                        if i>=100:# 超过100个多睡一会
                            cm = await KookApi.get_card_msg(f"已处理 [g{good}/e{err}]",guild_text[0:4800])
                            await KookApi.upd_card(send_msg['msg_id'],cm) # 更新消息
                            await asyncio.sleep(20)
                            i = 0
                    except:
                        err+=1
                        _log.exception(f"Err while G:{g}")
                        await asyncio.sleep(5) # 有错误也多睡一会
                        continue
                
                # 处理完毕
                time_diff = format(time.perf_counter()-start_time,".2f")
                text = "退出不活跃服务器处理完毕\n"
                text+= f"用时 {time_diff}s [g{good}/e{err}]\n"
                text+= f"命令使用<{IN_ACTIVATE_GUILD} 的服务器视作不活跃"
                cm = await KookApi.get_card_msg(text,sub_text=guild_text[0:4800])
                await KookApi.upd_card(send_msg['msg_id'],cm) # 更新卡片
                _log.info(f"Au:{msg.author_id} | guild_leave {time_diff}s [g{good}/e{err}] | {guild_text}")
        except:
            await BotLog.base_exception_handler("exit-g",traceback.format_exc(),msg,send_msg=send_msg)

    _log.info("[Admin] load Admin.py")