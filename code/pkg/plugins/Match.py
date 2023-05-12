import time
import traceback
import requests

from khl import (Bot, Message, requester, Channel)
from khl.card import Card, CardMessage, Element, Module, Types, Struct
from ..utils.valorant import Reauth
from ..utils.valorant.api import Riot,Assets
from ..utils.valorant.EzAuth import EzAuth,EzAuthExp,RiotUserToken
from ..utils.KookApi import get_card_msg,icon_cm,upd_card
from ..utils.log import BotLog
from ..utils.file.Files import UserAuthCache,_log


async def fetch_match_histroy(ru:RiotUserToken,startIndex=0,endIndex=20) -> dict:
    """获取玩家的战绩历史

    Docs: https://valapidocs.techchrism.me/endpoint/match-history
    
    Args:
    - startIndex (Optional)
        The index of the first match to return. Defaults to 0
    - endIndex (Optional)
        The index of the last match to return. Defaults to 20
    """
    url = f"https://pd.ap.a.pvp.net/match-history/v1/history/{ru.user_id}?startIndex={startIndex}&endIndex={endIndex}"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
    }
    res = requests.get(url, headers=headers)
    res = res.json()
    return res

async def fetch_match_details(ru:RiotUserToken,match_id:str) -> dict:
    """获取某一场比赛的详细信息"""
    url = f"https://pd.ap.a.pvp.net/match-details/v1/matches/{match_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": ru.entitlements_token,
        "Authorization": "Bearer " + ru.access_token,
    }
    res = requests.get(url, headers=headers)
    res = res.json()
    return res



async def get_match_detail_text(ru:RiotUserToken,match:dict) ->dict:
    """解析一个战绩历史，获取到其文字形式的结果
    Args:{
        "MatchID":"uuid",
        "GameStartTime": int,
        "QueueID": "unrated/ggteam/spikerush/..."
    }

    Return: {"match_agent":match_agent,"match_team":match_team,
    "damage_agv":damage_agv,"map_info":map_info,"match_player":match_player}
    """
    match_detail = await Riot.fetch_match_details(ru,match["MatchID"]) # 获取比赛信息
    map_url = match_detail["matchInfo"]["mapId"]
    map_info = await Assets.fetch_maps_url(map_url) # 获取地图信息
    # 获取玩家在比赛中的表现
    match_player = {}
    for p in match_detail["players"]:
        if p["subject"] == ru.user_id:
            match_player = p
            break
    _log.debug(f"{ru.user_id} | match_player: {match_player}")
    # 获取玩家的队伍
    match_team = {"enermy":{},"team":{}}
    for t in match_detail["teams"]:
        if t["teamId"] == match_player["teamId"]:
            match_team["team"] = t
        else:
            match_team["enermy"] = t
    _log.debug(f"{ru.user_id} | match_team: {match_team}")
    # 计算玩家的场均伤害(死斗是没有roundDamage的)
    damage_sum = 0
    damage_agv = -1
    if match_player["roundDamage"]:
        for r in match_player["roundDamage"]:
            damage_sum += r["damage"]
        damage_agv =  damage_sum // match_team["team"]["roundsPlayed"] # type: ignore
    # 获取玩家用的英雄
    match_agent = await Assets.fetch_agents(match_player["characterId"])
    return {"match_agent":match_agent,"match_team":match_team,"damage_agv":damage_agv,"map_info":map_info,"match_player":match_player}

async def get_match_detail_card(ru:RiotUserToken,match:dict) -> Card:
    """解析一个战绩历史，获取到其卡片
    {
        "MatchID":"uuid",
        "GameStartTime": int,
        "QueueID": "unrated/ggteam/spikerush/..."
    }
    """
    ret = await get_match_detail_text(ru,match)
    match_team = ret["match_team"] # 比赛的两个队伍
    match_player = ret["match_player"] # 玩家在比赛中表现
    match_agent = ret["match_agent"] # 比赛所用英雄
    map_name = ret["map_info"]["displayName"] # 地图名字
    damage_agv = ret["damage_agv"] # 比赛场均伤害
    # 文字
    kd = match_player['stats']['kills']/match_player['stats']['deaths']
    kd = format(kd,'.2f')
    text = f"{map_name} |  {match_team['team']['roundsWon']}-{match_team['enermy']['roundsWon']}  |  "
    text+= f"{match_player['stats']['kills']}/{match_player['stats']['deaths']}/{match_player['stats']['assists']}\n"
    sub_text = f"模式 {match['QueueID']} | 得分 {match_player['stats']['score']} | 场均伤害 {damage_agv} | KD {kd}"
    # 赢了绿色 输了红色
    card_color = "#98FB98" if match_team["team"]["won"] else "#FF6A6A" 
    c = Card(color=card_color)
    c.append(Module.Section(Element.Text(text, Types.Text.KMD),
                            Element.Image(src=match_agent["data"]["displayIconSmall"], size="sm")))
    c.append(Module.Context(Element.Text(sub_text, Types.Text.KMD)))
    return c


def init(bot:Bot,debug_ch:Channel):
    @bot.command(name='match',case_sensitive=False)
    async def match(msg:Message,index:str="0",*arg):
        BotLog.log_msg(msg)
        if Reauth.LoginForbidden:
            return Reauth.login_forbidden_send(msg)
        # index参数是下标，应该为一个正整数
        elif "-" in index or "." in index:
            await msg.reply(f"index 参数错误，请使用「/login-l」查看您需要查询的商店账户，并指定正确的编号（默认为0，即第一个账户）")
            return
        # 提前初始化变量
        send_msg = {'msg_id':''}
        cm = CardMessage()
        try:
            # 1.如果用户不在Authdict里面，代表没有登录，直接退出
            if msg.author_id not in UserAuthCache['kook']:
                await msg.reply(await get_card_msg("您尚未登陆！请「私聊」使用login命令进行登录操作", f"「/login 账户 密码」请确认您知晓这是一个风险操作", icon_cm.whats_that)) # type:ignore
                return

            # 2.判断下标是否合法，默认下标为0
            _index = int(index)
            # 2.2 下标非法（越界），发送报错信息
            if _index >= len(UserAuthCache['kook'][msg.author_id]):
                await msg.reply(await get_card_msg("您提供的下标超出范围！请检查您的输入，或不提供本参数","使用「/login-l」查看您当前登录的账户",icon_cm.dont_do_that)) # type:ignore
                return 
            # 2.2 下标合法，获取需要进行操作的Riot用户id
            riot_user_id = UserAuthCache['kook'][msg.author_id][_index]

            # 3.执行cookie重登
            start = time.perf_counter()
            reau = await Reauth.check_reauth("战绩",msg.author_id,riot_user_id,debug_ch,msg)
            if reau == False: return  # 如果为假说明重新登录失败，退出
            # 3.1 重新获取token成功了再提示正在获取夜市
            cm = await get_card_msg("正在尝试获取您近五场战绩", "战绩查询需要较久时间，耐心等待一下哦！", icon_cm.duck)
            if isinstance(reau, dict):  #如果传过来的是一个dict，说明重新登录成功且发送了消息
                await upd_card(reau['msg_id'], cm, channel_type=msg.channel_type) # type: ignore
                send_msg = reau
            else:
                send_msg = await msg.reply(cm)  # 记录消息id用于后续更新

            # 4.获取auth对象
            auth = UserAuthCache['data'][riot_user_id]['auth']
            assert isinstance(auth, EzAuth)
            
            # 5.获取比赛历史
            riot_user_token = auth.get_riotuser_token()
            match_histroy = await Riot.fetch_match_histroy(riot_user_token)
            # 6.遍历前5个，获取每一个的卡片消息(卡片最多5个)
            i=5
            cm = CardMessage()
            for match in match_histroy["History"]:
                c = await get_match_detail_card(riot_user_token,match)
                cm.append(c)
                if i<=1: break
                else: i-=1

            # 结束计时，发送给用户
            using_time = format(time.perf_counter() - start, '.2f')
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            _log.info(f"Au:{msg.author_id} | match reply success! | {using_time}s")
        except requester.HTTPRequester.APIRequestFailed as result:  # 卡片消息发送失败
            await BotLog.api_request_failed_handler("uinfo", traceback.format_exc(), msg, bot, cm, send_msg=send_msg)
        except Exception as result:
            await BotLog.base_exception_handler("match",traceback.format_exc(),msg)

    _log.info("[plugins] load match.py")