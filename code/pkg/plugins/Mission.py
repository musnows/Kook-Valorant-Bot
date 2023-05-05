import traceback
from khl import (Bot, Message, PrivateMessage, requester, Channel)
from khl.card import Card, CardMessage, Element, Module, Types, Struct

from ..utils.log import BotLog
from ..utils.file.FileManage import write_file
from ..utils.file.Files import UserAuthCache,ValMissionDict,_log
from ..utils.valorant.EzAuth import EzAuth,EzAuthExp
from ..utils.valorant import Reauth
from ..utils.valorant.api import Riot
from ..utils import Gtime,KookApi


def get_sub_text(text:str):
    """提供 用户任务日志信息，返回提示用户的sub_text"""
    sub_text = f"[说明](https://img.kookapp.cn/assets/2023-03/bOHjyLGtAc10f0sm.png) -> "
    sub_text+= "请转到[金山表单](https://f.wps.cn/g/Fipjms3w/)填写相关信息\n"
    sub_text+= "填写表单时，提供下方=右侧编号即可，感谢！\n"
    sub_text+= f"```\n{text}\n```"
    return sub_text


def init(bot:Bot,debug_ch:Channel):
    @bot.command(name='mission',case_sensitive=False)
    async def mission(msg:Message,*arg):
        BotLog.log_msg(msg)
        send_msg = {'msg_id':''}
        cm = CardMessage()
        try:
            # 1.如果用户不在Authdict里面，代表没有登录，直接退出
            if msg.author_id not in UserAuthCache['kook']:
                await msg.reply(await KookApi.get_card_msg("您尚未登陆！请「私聊」使用login命令进行登录操作", f"「/login 账户 密码」请确认您知晓这是一个风险操作", KookApi.icon_cm.whats_that)) # type:ignore
                return

            # 2.直接使用for循环来获取不同用户的信息
            mission_cm = CardMessage()
            log_m_text = "" # 记录save到本地的用户战绩信息，用于收集id
            save_flag = False # 是否要保存到本地（如果存在未录入的就保存）
            for riot_user_id in UserAuthCache['kook'][msg.author_id]:
                try:
                    # 3.执行cookie重登
                    reau = await Reauth.check_reauth("玩家任务",msg.author_id,riot_user_id,debug_ch,msg)
                    if reau == False: return  #如果为假说明重新登录失败
                    # 3.2 获取玩家id成功了，再提示正在获取商店
                    cm = await KookApi.get_card_msg("正在尝试获取您的每日任务", "阿狸正在施法，很快就好啦！", KookApi.icon_cm.duck)
                    # 3.2.1 如果reauth函数return的是dict，说明重新登录成功且发送了消息，则更新卡片
                    if isinstance(reau, dict):  
                        await KookApi.upd_card(reau['msg_id'], cm, channel_type=msg.channel_type)
                        send_msg = reau
                    # 3.2.1 不是dict，说明不需要重登，也没有发送提示信息
                    else:
                        send_msg = await msg.reply(cm)  #记录消息id用于后续更新

                    auth = UserAuthCache['data'][riot_user_id]['auth']
                    assert isinstance(auth, EzAuth)
                    # 获取玩家任务
                    ret = await Riot.fetch_player_contract(auth.get_riotuser_token())
                    mission_list = ret["Missions"] # 任务列表
                    mission_meta = ret["MissionMetadata"] # 任务重置信息
                    # 构造任务信息
                    save_flag = False
                    m_text = ""
                    for m in mission_list:
                        if m["ID"] not in ValMissionDict:
                            save_flag = True
                            continue
                        m_info = ValMissionDict[m["ID"]]
                        m_text+=f"[{m_info['MissionType']}] {m_info['DisplayName']}\n"
                        m_text+=f"[进度] {m['Objectives'][m_info['ObjectivesID']]}/{m_info['Total']}\n"
                        
                    # 构造卡片(只要m_text不为空就构造)
                    if m_text:
                        c = Card(Module.Header(f"玩家「{auth.Name}#{auth.Tag}」的任务"))
                        c.append(Module.Section(Element.Text(f"```\n{m_text}```\n",Types.Text.KMD)))
                        c.append(Module.Context(Element.Text(f"每周任务重制时间 {mission_meta['WeeklyRefillTime']}",Types.Text.KMD)))
                        mission_cm.append(c)

                    # 保存到本地（记录未录入的任务）
                    if save_flag:
                        id_text = f"{auth.user_id}_{int(Gtime.time.time())}"
                        log_m_text += f"{auth.Name}#{auth.Tag} = {id_text}\n"
                        write_file(f'./log/mission/{id_text}.json',ret)
                    # 结束
                    _log.info(f"Au:{msg.author_id} | get {riot_user_id} mission success")
                except KeyError as result:
                    if "Missions" in str(result):
                        _log.exception(f"KeyErr while Au:{msg.author_id} | Ru:{riot_user_id}")
                        cm2 = await KookApi.get_card_msg(f"键值错误，需要重新登录", 
                                                         f"KeyError:{result}, please re-login", KookApi.icon_cm.lagging)
                        await KookApi.upd_card(send_msg['msg_id'], cm2, channel_type=msg.channel_type)
                    else:raise result
            
            # 多个账户都获取完毕，发送卡片并输出结果
            cm = mission_cm
            if save_flag: # 该用户尚有未处理的任务id
                cm.append(await KookApi.get_card("您账户的任务尚未完全收录!", get_sub_text(log_m_text)))
            await KookApi.upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            _log.info(f"Au:{msg.author_id} | mission reply successful!")
        except requester.HTTPRequester.APIRequestFailed as result:
            await BotLog.api_request_failed_handler("mission",traceback.format_exc(),msg,bot,cm)
        except Exception as result:
            await BotLog.base_exception_handler("mission",traceback.format_exc(),msg)

    _log.info("[plugins] load mission")