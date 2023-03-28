# encoding: utf-8:
import os, io
import time
import json
import traceback
import aiohttp
import copy
import zhconv
import asyncio
from khl import (Bot, Event, EventTypes, Message, PrivateMessage, requester, Channel)
from khl.card import Card, CardMessage, Element, Module, Types, Struct
from aiohttp import client_exceptions

from pkg.utils import ShopRate, ShopImg, Help, BotVip
from pkg.utils.log import BotLog
from pkg.utils.log.Logging import _log
from pkg.utils.valorant import Reauth,AuthCache
from pkg.utils.KookApi import icon_cm, bot_offline, upd_card, get_card,get_card_msg
from pkg.utils.valorant.api import Assets,Riot,Local
from pkg.utils.valorant.EzAuth import EzAuth, EzAuthExp
from pkg.utils.Gtime import getTime, getTimeStampOf8AM,shop_time_remain,getTimeFromStamp,getDate

# bot的token文件
from pkg.utils.file.FileManage import FileManage,save_all_file,write_file
from pkg.utils.file.Files import config, bot, ApiAuthLog, LoginForbidden,NightMarketOff
# 只用来上传图片的bot
bot_upimg = Bot(token=config['token']['img_upload_token'])
"""用来上传图片的bot"""
master_id = config['master_id']
"""机器人开发者用户id"""

# 在bot一开机的时候就获取log频道作为全局变量
debug_ch: Channel
"""发送错误信息的日志频道"""
cm_send_test: Channel
"""进行卡片消息发送测试的频道"""
NOTIFY_NUM = 3 
"""非vip用户皮肤提醒栏位"""
RATE_LIMITED_TIME = 180 
"""全局登录速率超速等待秒数"""
LOGIN_LIMITED = 3
"""所有用户最多都只能登录3个riot账户"""
start_time = getTime()
"""记录开机时间"""


# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api = "http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid': 'a87ebe9c-1319-4394-9704-0ad2c70e2567'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)


# 每5分钟保存一次文件
@bot.task.add_interval(minutes=5)
async def Save_File_Task():
    try:
        await save_all_file()
    except:
        err_cur = f"ERR! [{getTime()}] [Save.File.Task]\n```\n{traceback.format_exc()}\n```"
        _log.exception("ERR in Save_File_Task")
        await bot.client.send(debug_ch, err_cur) # type: ignore


@bot.command(name='kill')
async def KillBot(msg: Message, num: str = '124124', *arg):
    BotLog.logMsg(msg)
    try:
        if msg.author_id == master_id and int(num) == config['no']:
            # 保存所有文件
            await save_all_file(False)
            await msg.reply(f"[KILL] 保存全局变量成功，bot下线")
            res = await bot_offline()  # 调用接口下线bot
            _log.info(f"KILL | bot-off: {res}\n")
            os._exit(0)  # 退出程序
        else:
            await msg.reply(f"您没有权限或参数错误！\n本Bot编号为：{config['no']}")
    except:
        await BotLog.BaseException_Handler("kill",traceback.format_exc(),msg)


##########################################################################################
########################################  help  ##########################################


# hello命令，一般用于测试阿狸在不在线
@bot.command(name='hello', aliases=['HELLO'])
async def world(msg: Message):
    BotLog.logMsg(msg)
    await msg.reply('你好呀~')


# help命令,触发指令为 `/Ahri`,因为help指令和其他机器人冲突
@bot.command(name='Ahri', aliases=['ahri', '阿狸'])
async def Ahri(msg: Message, *arg):
    BotLog.logMsg(msg)
    try:
        cm = Help.help_main(start_time)
        await msg.reply(cm)
    except Exception as result:
        await BotLog.BaseException_Handler("ahri", traceback.format_exc(), msg, debug_send=debug_ch)


# help命令(瓦洛兰特相关)
@bot.command(name='Vhelp', aliases=['vhelp'])
async def Vhelp(msg: Message, *arg):
    BotLog.logMsg(msg)
    try:
        cm = Help.help_val()
        await msg.reply(cm)
    except Exception as result:
        await BotLog.BaseException_Handler("vhelp", traceback.format_exc(), msg, debug_send=debug_ch)


# 当有人@机器人的时候进行回复，可识别出是否为机器人作者
@bot.on_message()
async def atAhri(msg: Message):
    try:
        # kook系统通知
        if msg.author_id == "3900775823":
            return
        if f"(met){bot.client.me.id}(met)" in msg.content:
            BotLog.logMsg(msg)
            if msg.author_id == master_id:
                text = Help.help_develop()
                await msg.reply(text)
            else:
                await msg.reply(f"呀，听说有人想我了，是吗？\n输入`/ahri` 或 `/vhelp` 打开帮助面板，和阿狸一起玩吧！")
            _log.info(f"Au:{msg.author_id} | msg.reply success!")
    except:
        await BotLog.BaseException_Handler("at_help", traceback.format_exc(), msg)


# 手动设置禁止登录的全局变量状态
@bot.command(name='lf')
async def LoginForbidden_Change(msg: Message):
    BotLog.logMsg(msg)
    if msg.author_id == master_id:
        global LoginForbidden
        if LoginForbidden:
            LoginForbidden = False
        else:
            LoginForbidden = True

        await msg.reply(f"Update LoginForbidden status: {LoginForbidden}")

async def LoginForbidden_send(msg: Message):
    """拳头api调用被禁止的时候，发送提示信息"""
    _log.info(f"Au:{msg.author_id} Command Failed | LF")
    await msg.reply(
        f"拳头api登录接口出现了一些错误，开发者已禁止所有相关功能的使用\n[https://img.kookapp.cn/assets/2022-09/oj33pNtVpi1ee0eh.png](https://img.kookapp.cn/assets/2022-09/oj33pNtVpi1ee0eh.png)"
    )

#####################################################################################

# 预加载用户的riot游戏id和玩家uuid（登录后Api获取）
from pkg.utils.file.Files import (SkinNotifyDict, SkinRateDict, ValBundleList,UserAuthCache,UserPwdReauth,ValItersEmoji,
                              UserStsDict,UserRtsDict,UserShopCache,login_rate_limit,VipUserDict,VipAuthLog,VipShopBgDict)

def check_rate_err_user(kook_user_id: str)-> bool:
    """检查皮肤评分的错误用户（违规用户）
    - kook_user_id in SkinRateDict['err_user']
    """
    return (kook_user_id in SkinRateDict['err_user'])


def isClear_UserShopCache() -> bool:
    """判断UserShopCache["data"]是否在当日早八被清空（避免定时任务没有正常执行）
    - True: 如果已经清空，则返回True且啥都不做
    - False: 如果没有清空，则清空并返回False（这一次请求需要调用api获取商店）
    """
    # 判断清空的时间戳是否大于当日早上8点时间戳
    global UserShopCache
    if UserShopCache["clear_time"] >= getTimeStampOf8AM():
        return True
    else: # 如果不大于，则代表定时任务没有正常执行，清空dict并返回FALSE
        UserShopCache["data"] = {}
        return False

def is_CacheLatest(kook_user_id: str,riot_user_id:str) -> bool:
    """判断vip用户缓存好的图片是否可用，需要满足几个条件：
    - vip用户有配置自定义背景图
    - vip用户没有切换登录账户/切换背景图
    - 当前需要获取商店的拳头用户id在缓存中
    """
    is_Status = False
    # 1.判断vip用户是否在背景图配置中，且没有切换登录用户/切换背景图
    if kook_user_id in VipShopBgDict['bg']:
        is_Status = VipShopBgDict['bg'][kook_user_id]['status']  # 如果有切换登录用户/背景图，此为false
    # 2.拳头用户在vip缓存中
    if riot_user_id in VipShopBgDict['cache']:
        # 判断图片是不是今天的（可能出现早八提醒的时候出错，导致缓存没有更新，是昨天的图）
        is_Today = (VipShopBgDict['cache'][riot_user_id]['cache_time'] - getTimeStampOf8AM()) > 0
        return is_Today and is_Status  # 有一个为false，结果就是false

    return False


# 检查全局用户登录速率
async def check_GloginRate():
    global login_rate_limit
    if login_rate_limit['limit']:
        if (time.time() - login_rate_limit['time']) > RATE_LIMITED_TIME:
            login_rate_limit['limit'] = False  #超出180s解除
        else:  #未超出240s
            raise EzAuthExp.RatelimitError
    return True

# 缓存vip用户的信息
async def cache_vip_auth(kook_user_id:str,auth:EzAuth):
    global VipShopBgDict,VipAuthLog 
    # 因为换了用户，所以需要修改状态码重新获取商店
    if kook_user_id in VipShopBgDict['bg']:
        VipShopBgDict['bg'][kook_user_id]['status'] = False
    # 用于保存cookie的路径,保存vip用户登录信息
    if kook_user_id not in VipAuthLog: 
        VipAuthLog[kook_user_id] = []
    # 如果这个uuid不在，再插入
    if auth.user_id not in VipAuthLog[kook_user_id]:
        VipAuthLog[kook_user_id].append(auth.user_id) # 插入键值
    # 保存cookie到本地
    auth.save_cookies(f"./log/cookie/{auth.user_id}.cke")
    _log.info(f"save cookies | './log/cookie/{auth.user_id}.cke'")

#查询当前有多少用户登录了
@bot.command(name="ckau")
async def check_UserAuthCache_len(msg: Message):
    BotLog.logMsg(msg)
    try:
        text = f"bot: `{len(UserAuthCache['kook'])}` | api: {len(UserAuthCache['api'])}"
        _log.info(text)
        await msg.reply(text)
    except:
        await BotLog.BaseException_Handler("ckau",traceback.format_exc(),msg)


# 登录，保存用户的token
@bot.command(name='login')
async def login(msg: Message, user: str = 'err', passwd: str = 'err', apSave='', *arg):
    _log.info(f"Au:{msg.author_id} {msg.author.username}#{msg.author.identify_num} | /login {apSave}")
    BotLog.log_bot_user(msg.author_id)  #这个操作只是用来记录用户和cmd总数的
    global LoginForbidden, login_rate_limit, UserAuthCache
    if not isinstance(msg, PrivateMessage):  # 不是私聊的话，禁止调用本命令
        await msg.reply(f"为了避免您的账户信息泄漏，请「私聊」使用本命令！\n用法：`/login 账户 密码`")
        return
    elif passwd == 'err' or user == 'err':
        await msg.reply(f"参数不完整，请提供您的账户密码！\naccount: `{user}` passwd: `{passwd}`\n正确用法：`/login 账户 密码`")
        return
    elif LoginForbidden:
        await LoginForbidden_send(msg)
        return
    # 提前定义，避免报错
    send_msg = {'msg_id':''}
    cm = CardMessage()
    try:
        # 1.检查全局登录速率
        await check_GloginRate()  # 无须接收此函数返回值，直接raise
        # 1.1 检查当前已经登录的用户数量，超过限制直接提示并返回
        if msg.author_id in UserAuthCache["kook"] and len(UserAuthCache["kook"][msg.author_id]) >= LOGIN_LIMITED:
            await msg.reply(await get_card_msg("您当前已经登录了3个拳头账户！",
                                     "为避免后台缓存压力过大，您最多只能登录3个Riot账户",icon_cm.im_good_phoniex))# type:ignore
            return
        # 2.发送开始登录的提示消息
        cm = await get_card_msg("正在尝试获取您的riot账户token", "小憩一下，很快就好啦！", icon_cm.val_logo_gif)
        send_msg = await msg.reply(cm)  #记录消息id用于后续更新

        # 3.登录，获取用户的token
        auth = EzAuth()
        resw = await auth.authorize(user, passwd)
        # 3.1 将对象插入缓存队列
        await AuthCache.cache_auth_object('kook',msg.author_id,auth)
        # 3.2 没有成功，是2fa用户，需要执行/tfa命令
        if not resw['status']:
            cm = await get_card_msg("请使用「/tfa 验证码」提供邮箱验证码","登录中断，需要提供邮箱验证码",icon_cm.whats_that)
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            _log.info(f"login | 2fa user | Au:{msg.author_id}")  # 打印信息
            return

        # 4.如果没有抛出异常，那就是完成登录了，设置用户的玩家uuid+昵称
        text = f"登陆成功！欢迎回来，{auth.Name}#{auth.Tag}"
        info_text = "当前cookie有效期为2~3天，有任何问题请[点我](https://kook.top/gpbTwZ)"

        # 5.如果是vip用户，则执行下面的代码
        if await BotVip.vip_ck(msg.author_id):
            await cache_vip_auth(msg.author_id,auth)

        # 6.用户自己选择是否保存账户密码，默认是不保存的；2fa用户也不会保存
        if apSave == 'save' and (not auth.is2fa):
            if msg.author_id not in UserPwdReauth:# 不在dict里面，再新建
                UserPwdReauth[msg.author_id] = {}
            # 新增账户密码的键值
            UserAuthCache['acpw'][auth.user_id] = {'a': user, 'p': passwd}
            info_text += "\n您选择了保存账户密码，cookie失效后将使用账户密码重登"

        # 7.发送登录成功的信息
        cm = await get_card_msg(text, info_text, icon_cm.correct)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)

        # 8.全部都搞定了，打印登录信息日志
        _log.info(
            f"Login | Au:{msg.author_id} | {auth.Name}#{auth.Tag}"
        )
    except EzAuthExp.AuthenticationError as result:
        _log.error(f"login AuthenticationError | Au:{msg.author_id} | {result}")
        text_sub = f"Make sure accont/password/verify-code correct\n`{result}`"
        cm = await get_card_msg("登录错误，请检查账户/密码/邮箱验证码", text_sub, icon_cm.dont_do_that)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except EzAuthExp.WaitOvertimeError as result:
        _log.error(f"login WaitOvertimeError | Au:{msg.author_id} | {result}")
        cm = await get_card_msg("等待超时", "auth wait overtime", icon_cm.lagging)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except EzAuthExp.RatelimitError as result:
        err_str = f"ERR! [{getTime()}] login Au:{msg.author_id} - {result}"
        # 更新全局速率限制
        login_rate_limit = {'limit': True, 'time': time.time()}
        _log.error(err_str + " set login_rate_limit = True")
        # 这里是第一个出现速率限制err的用户,更新消息提示
        cm = await get_card_msg(f"登录请求超速！请在{RATE_LIMITED_TIME}s后重试", "RatelimitError,try again later", icon_cm.lagging)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except client_exceptions.ClientResponseError as result:
        err_str = f"ERR! [{getTime()}] login Au:{msg.author_id}\n```\n{traceback.format_exc()}\n```\n"
        Reauth.client_exceptions_handler(str(result),err_str)
        _log.exception("Exception occur in login")
        cm = await get_card_msg(err_str)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except KeyError as result:
        _log.error(f"login | Au:{msg.author_id} | KeyError: {result}")
        text = f"遇到未知的KeyError，请[联系](https://kook.top/gpbTwZ)阿狸的主人哦~"
        text_sub = f"Unkown KeyError, please contact bot developer"
        if '0' in str(result):
            text = f"遇到不常见的KeyError，可能👊Api服务器炸了"
            text_sub = f"KeyError, maybe Roit API Offline"
        # 发送卡片消息
        cm = await get_card_msg(text, text_sub, icon_cm.that_it)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except requester.HTTPRequester.APIRequestFailed as result:  #卡片消息发送失败
        await BotLog.APIRequestFailed_Handler("login", traceback.format_exc(), msg, bot, cm, send_msg=send_msg)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("login",
                                           traceback.format_exc(),
                                           msg,
                                           send_msg=send_msg,
                                           help="请加入帮助频道咨询，或尝试重新执行login命令")


@bot.command(name='tfa')
async def tfa_verify(msg: Message, tfa: str, *arg):
    _log.info(f"Au:{msg.author_id} {msg.author.username}#{msg.author.identify_num} | /tfa")
    if len(tfa) != 6:
        await msg.reply(f"邮箱验证码长度错误，请确认您输入了正确的6位验证码\n当前参数：`{tfa}`")
        return

    send_msg = {'msg_id': ''}
    try:
        # 1. 先判断用户是否在dict里面
        if msg.author_id not in UserAuthCache['tfa']:
            await msg.reply("您不在UserAuthCache中，请先执行login！")
            return
        # 1.1 在，且auth对象是ezauth
        auth = await AuthCache.get_tfa_auth_object(msg.author_id)
        assert isinstance(auth, EzAuth)
        # 1.2 判断这个auth是否已经初始化完毕了，如果是，则不执行后续操作
        if auth.is_init(): # 初始化完毕
            return await msg.reply(await get_card_msg(f"玩家「{auth.Name}#{auth.Tag}」已登录，无须执行本命令","若有问题，请联系开发者",icon_cm.correct))
            

        # 2.发送提示信息
        cm = await get_card_msg(f"两步验证码「{tfa}」获取成功", "小憩一下，很快就好啦！", icon_cm.no_time)
        send_msg = await msg.reply(cm)  #记录消息id用于后续更新

        # 3.进行邮箱验证
        await auth.email_verfiy(tfa)
        # 3.1 验证成功，进行缓存
        await AuthCache.cache_auth_object('kook',msg.author_id,auth)
        # 3.2 如果是vip用户，则执行下面的代码
        if await BotVip.vip_ck(msg.author_id):
            await cache_vip_auth(msg.author_id,auth)
        # 4.成功
        text = f"登陆成功！欢迎回来，{auth.Name}#{auth.Tag}"
        info_text = "当前cookie有效期为2~3天，有任何问题请[点我](https://kook.top/gpbTwZ)"
        cm = await get_card_msg(text, info_text, icon_cm.correct)
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
        _log.info(
            f"tfa | Au:{msg.author_id} | {auth.Name}#{auth.Tag}"
        )
    except EzAuthExp.MultifactorError as result:
        if "multifactor_attempt_failed" in str(result):
            cm = await get_card_msg("两步验证码错误，请重试", str(result), icon_cm.lagging)
        else:
            cm = await get_card_msg("邮箱验证错误，请重新login", str(result), icon_cm.lagging)
        # 更新消息
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("tfa", traceback.format_exc(), msg, help="请加入帮助频道咨询，或尝试重新执行login命令")


# 退出登录
@bot.command(name='logout')
async def logout(msg: Message, *arg):
    BotLog.logMsg(msg)
    try:
        global UserAuthCache
        # 1.用户如果没有登录，那也没必要logout
        if msg.author_id not in UserAuthCache['kook']: 
            cm = await get_card_msg("您尚未登陆！无须logout", "阿巴阿巴？", icon_cm.whats_that)
            await msg.reply(cm)
            return

        log_text = f"Logout | Au:{msg.author_id}"
        # 2.如果id存在，删除auth对象
        # 2.1 删除对象
        riot_user_id_list = UserAuthCache['kook'][msg.author_id]
        for u in riot_user_id_list:
            del UserAuthCache['data'][u]
        # 2.2 删除键值
        del UserAuthCache['kook'][msg.author_id]
        # 3.如果是vip用户，删除本地保存的cookie
        cookie_path = f"./log/cookie/{msg.author_id}.cke"
        # 3.1 判断路径是否存在，存在直接删除
        if os.path.exists(cookie_path):
            os.remove(cookie_path)  # 删除文件
            log_text += " | rm cookie file"
        # 4.成功，发提示信息
        text = f"已退出所有账户的登录！下次再见~"
        cm = await get_card_msg(text, "你会回来的，对吗？", icon_cm.crying_crab)
        await msg.reply(cm) # type:ignore
        _log.info(log_text)

    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("logout", traceback.format_exc(), msg)


@bot.command(name='login-ap')
async def login_acpw(msg: Message, *arg):
    """获取bot使用riot的账户密码登录的记录（用户自己选择了save账户密码的）
    """
    BotLog.logMsg(msg)
    try:
        if msg.author_id not in UserPwdReauth:
            await msg.reply(f"您没有保存账户密码或2fa用户，该命令无效")
            return
        send_text = 'none'
        if len(UserPwdReauth[msg.author_id]) == 0:
            send_text = "阿狸还没有用过您的账户密码来重新登录呢"
        else:
            send_text = '以下为账户密码登录日志\n'
            for i in UserPwdReauth[msg.author_id]:
                send_text += f"{i} - {UserPwdReauth[msg.author_id][i]}\n"
        # 发送信息
        await msg.reply(send_text)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("login-ap", traceback.format_exc(), msg)


@bot.command(name='login-l',aliases=['login-list'],case_sensitive=False)
async def login_list(msg:Message,*arg):
    """获取用户已经登录的账户
    """
    BotLog.logMsg(msg)
    cm = CardMessage()
    try:
        if msg.author_id not in UserAuthCache["kook"]:
            await msg.reply(f"您尚未登录任何valorant账户")
            return
        i = 0
        text="```\n"
        for ru in UserAuthCache["kook"][msg.author_id]:
            auth = UserAuthCache["data"][ru]["auth"]
            assert isinstance(auth, EzAuth)
            text+=f"[{i}] {auth.Name}#{auth.Tag} 登陆于 {getTimeFromStamp(auth.init_time)}\n"
            i+=1
        text+="```"
    
        c = Card()
        c.append(Module.Header(f"您当前已登录的riot账户列表"))
        c.append(Module.Context(f"您还可以登录 {LOGIN_LIMITED-i} 个账户"))
        c.append(Module.Divider())
        c.append(Module.Section(Element.Text(text,Types.Text.KMD)))
        c.append(Module.Context("查询商店/夜市时，需要指定账户前的编号，默认为0\n如「/shop 1」查询已登录账户中编号为1的账户"))
        cm.append(c)
        await msg.reply(cm)
        _log.info(f"Au:{msg.author_id} | login-list reply success")
    except requester.HTTPRequester.APIRequestFailed as result:
        await BotLog.APIRequestFailed_Handler("login-l", traceback.format_exc(), msg,bot,cm)
    except Exception as result:
        await BotLog.BaseException_Handler("login-l", traceback.format_exc(), msg)


# 获取每日商店的命令
@bot.command(name='shop', aliases=['SHOP'])
async def get_daily_shop(msg: Message,index:str = "0",*arg):
    BotLog.logMsg(msg)
    if LoginForbidden:
        await LoginForbidden_send(msg)
        return
    # index参数是下标，应该为一个正整数
    elif "-" in index or "." in index:
        await msg.reply(f"index 参数错误，请使用「/login-l」查看您需要查询的商店账户，并指定正确的编号（默认为0，即第一个账户）")
        return
    # 提前初始化变量
    send_msg = {'msg_id':''}
    resp = ""
    cm = CardMessage()
    try:
        # 1.如果用户不在Authdict里面，代表没有登录，直接退出
        if msg.author_id not in UserAuthCache['kook']:
            await msg.reply(await get_card_msg("您尚未登陆！请「私聊」使用login命令进行登录操作", f"「/login 账户 密码」请确认您知晓这是一个风险操作", icon_cm.whats_that))
            return

        # 2.判断下标是否合法，默认下标为0
        _index = int(index)
        # 2.2 下标非法（越界），发送报错信息
        if _index >= len(UserAuthCache['kook'][msg.author_id]):
            await msg.reply(await get_card_msg("您提供的下标超出范围！请检查您的输入，或不提供本参数","使用「/login-l」查看您当前登录的账户",icon_cm.dont_do_that))
            return 
        # 2.2 下标合法，获取需要进行操作的Riot用户id
        riot_user_id = UserAuthCache['kook'][msg.author_id][_index]
        # 3.执行cookie重登
        reau = await Reauth.check_reauth("每日商店",msg.author_id,riot_user_id,debug_ch,msg)
        if reau == False: return  # 如果为假说明重新登录失败，退出
        # 3.2 获取玩家id成功了，再提示正在获取商店
        cm = await get_card_msg("正在尝试获取您的每日商店", "阿狸正在施法，很快就好啦！", icon_cm.duck)
        # 3.2.1 如果reauth函数return的是dict，说明重新登录成功且发送了消息，则更新卡片
        if isinstance(reau, dict):  
            await upd_card(reau['msg_id'], cm, channel_type=msg.channel_type)
            send_msg = reau
        # 3.2.1 不是dict，说明不需要重登，也没有发送提示信息
        else:
            send_msg = await msg.reply(cm)  #记录消息id用于后续更新

        # 4.开始获取每日商店
        # 4.1 计算获取每日商店要多久
        log_time = ""
        start = time.perf_counter()  #开始计时
        # 4.2 从auth的dict中获取对象
        auth = UserAuthCache['data'][riot_user_id]['auth']
        assert isinstance(auth, EzAuth)
        riotUser = auth.get_riotuser_token()
        # 4.2.1 从dict中获取玩家id
        player_gamename = f"{auth.Name}#{auth.Tag}"
        # 4.3 开始判断是否需要获取商店（是否有缓存）
        a_time = time.time()
        global UserShopCache, VipShopBgDict
        # 4.3.1 UserShopDict每天早八会被清空，如果用户在里面且玩家id一样，那么说明已经获取过当日商店了
        if isClear_UserShopCache() and auth.user_id in UserShopCache["data"]:  # 直接使用本地已有的当日商店
            list_shop = UserShopCache["data"][auth.user_id]["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
            timeout = shop_time_remain()  # 通过当前时间计算商店剩余时间
            log_time += f"[Dict_shop] {format(time.time()-a_time,'.4f')} "
        # 4.3.2 本地没有，api获取每日商店
        else:
            resp = await Riot.fetch_daily_shop(riotUser)  
            list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
            timeout = resp["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]  # 剩余时间
            timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  # 将秒数转为标准时间
            # 需要设置uuid来保证是同一个用户，方便同日的下次查询
            UserShopCache["data"][auth.user_id] = {
                "kook_user_id": msg.author_id,
                "SkinsPanelLayout":resp["SkinsPanelLayout"]
            }
            log_time += f"[Api_shop] {format(time.time()-a_time,'.4f')} "

        # 5.开始画图
        draw_time = time.time()  # 计算画图需要的时间
        is_vip = await BotVip.vip_ck(msg.author_id)  # 判断用户是否为VIP
        img_ret = {'status': True, 'value': None}
        upload_flag = True # 是否有缓存（无须上传图片）
        # 5.1 初始化商店图片的url为一个展示错误的图片
        dailyshop_img_src = "https://img.kookapp.cn/assets/2023-02/5UxA8W06B70e803m.png"
        # 5.1.1 如果是vip而且path存在,背景图/登录用户没有更改过,图片缓存时间正确
        if is_vip and is_CacheLatest(msg.author_id,auth.user_id):
            upload_flag = False  # 有缓存图，直接使用本地已有链接
            dailyshop_img_src = VipShopBgDict['cache'][auth.user_id]['cache_img']
        # 5.1.2 本地缓存路径不存在，或者缓存过期
        elif is_vip:
            play_currency = await Riot.fetch_vp_rp_dict(riotUser)  # 获取用户的vp和rp
            # 如果没有设置背景图，那就设置为err
            background_img = ('err' if msg.author_id not in VipShopBgDict['bg'] else
                              VipShopBgDict['bg'][msg.author_id]["background"][0])
            img_ret = await ShopImg.get_shop_img_169(list_shop,
                                                     vp=play_currency['vp'],
                                                     rp=play_currency['rp'],
                                                     bg_img_src=background_img)
        else: # 5.1.3 普通用户
            # 判断是否有缓存命中
            cache_ret = await ShopRate.query_ShopCache(skinlist=list_shop)
            if not cache_ret['status']:  # 缓存没有命中
                img_ret = await ShopImg.get_shop_img_11(list_shop)
            else:  # 命中
                upload_flag = False
                dailyshop_img_src = cache_ret['img_url']
                log_time += "[cache] "

        # 5.2 img_ret 代表是否画图成功，如果是缓存命中，也当成功处理
        if img_ret['status']:
            bg = img_ret['value']  #获取图片
        else:  # 出现背景图片违规或其他问题
            await msg.reply(img_ret['value'])
            _log.info(f"[GetShopImg] Au:{msg.author_id} | {img_ret['value']}")
            return

        # 5.3 获取图片成功，打印画图耗时
        _log.info(log_time + f"- [Drawing] {format(time.time() - draw_time,'.4f')} - [Au] {msg.author_id}")
        # 5.3.1 判断是否需要上传，false不需要
        if upload_flag:
            # 5.3.2 上传图片
            imgByteArr = io.BytesIO()
            bg.save(imgByteArr, format='PNG')
            imgByte = imgByteArr.getvalue()
            dailyshop_img_src = await bot_upimg.client.create_asset(imgByte)  # type: ignore
            # 5.3.3 如果在bg里面代表有自定义背景图，需更新status
            if is_vip:
                if msg.author_id in VipShopBgDict['bg']:
                    VipShopBgDict['bg'][msg.author_id]['status'] = True
                # 设置商店图片缓存+图片缓存的时间
                VipShopBgDict['cache'][auth.user_id] = {'cache_img': dailyshop_img_src, 'cache_time': time.time()}
            else:  # 非vip，更新缓存
                await ShopRate.update_ShopCache(skinlist=list_shop, img_url=dailyshop_img_src)

        # 6.结束shop的总计时，结果为浮点数，保留两位小数
        end = time.perf_counter()
        shop_using_time = format(end - start, '.2f')

        # 7.商店的图片 卡片
        cm = CardMessage()
        c = Card(color='#fb4b57')
        c.append(Module.Header(f"玩家 {player_gamename} 的每日商店！"))
        c.append(Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {shop_using_time}s"))
        c.append(Module.Container(Element.Image(src=dailyshop_img_src)))
        cm.append(c)

        # 8.皮肤评分和评价卡片，用户不在rate_err_user里面才显示(在评论中发表违规言论的用户)
        if not check_rate_err_user(msg.author_id):
            cm = await ShopRate.get_shop_rate_cm(list_shop, msg.author_id, cm=cm)
            end = time.perf_counter()  #计算获取评分的时间
        # 9.更新消息
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
        # 10.结束，打印结果
        _log.info(f"Au:{msg.author_id} | daily_shop reply successful [{shop_using_time}/{format(end - start, '.2f')}]")
    except requester.HTTPRequester.APIRequestFailed as result:  #卡片消息发送失败
        await BotLog.APIRequestFailed_Handler("shop", traceback.format_exc(), msg, bot, cm, send_msg=send_msg)
    except Exception as result:
        err_str = f"ERR! [{getTime()}] shop\n```\n{traceback.format_exc()}\n```\n"
        if "SkinsPanelLayout" in str(result):
            _log.error(err_str + str(resp))
            btext = f"KeyError:{result}, please re-login\n如果此问题重复出现，请[联系开发者](https://kook.top/gpbTwZ)"
            cm = await get_card_msg(f"键值错误，需要重新登录", btext, icon_cm.whats_that)
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
        else:
            await BotLog.BaseException_Handler("shop", traceback.format_exc(), msg, send_msg=send_msg)


# 获取夜市
@bot.command(name='night', aliases=['NIGHT'])
async def get_night_market(msg: Message,index:str="0", *arg):
    BotLog.logMsg(msg)
    global NightMarketOff
    if "-" in index or "." in index:
        await msg.reply(f"index 参数错误，请使用「/login-l」查看您需要查询的账户，并指定正确的编号（默认为0，即第一个账户）")
        return
    elif LoginForbidden:
        await LoginForbidden_send(msg)
        return
    elif NightMarketOff:
        await msg.reply(f"夜市暂未开放！请等开放了之后再使用本命令哦~")
        return

    send_msg = {'msg_id':''}
    cm = CardMessage()
    try:
        # 1.判断是否已经登录
        if msg.author_id not in UserAuthCache['kook']:
            return await msg.reply(await get_card_msg("您尚未登陆！请「私聊」使用login命令进行登录操作", f"「/login 账户 密码」请确认您知晓这是一个风险操作", icon_cm.whats_that))
            
        
        # 2.判断下标是否合法，默认下标为0
        _index = int(index)
        # 2.2 下标非法（越界），发送报错信息
        if _index >= len(UserAuthCache['kook'][msg.author_id]):
            return await msg.reply(await get_card_msg("您提供的下标超出范围！请检查您的输入，或不提供本参数","使用「/login-l」查看您当前登录的账户",icon_cm.dont_do_that))
            
        # 2.2 下标合法，获取需要进行操作的Riot用户id
        riot_user_id = UserAuthCache['kook'][msg.author_id][_index]
        # 3.执行cookie重登
        reau = await Reauth.check_reauth("夜市",msg.author_id,riot_user_id,debug_ch,msg)
        if reau == False: return  #如果为假说明重新登录失败

        # 重新获取token成功了再提示正在获取夜市
        cm = await get_card_msg("正在尝试获取您的夜市", "阿狸正在施法，很快就好啦！", icon_cm.duck)
        if isinstance(reau, dict):  #如果传过来的是一个dict，说明重新登录成功且发送了消息
            await upd_card(reau['msg_id'], cm, channel_type=msg.channel_type) # type: ignore
            send_msg = reau
        else:
            send_msg = await msg.reply(cm)  #记录消息id用于后续更新

        # 计算获取时间
        start = time.perf_counter()  #开始计时
        auth = UserAuthCache['data'][riot_user_id]['auth']
        assert isinstance(auth, EzAuth)
        riotUser = auth.get_riotuser_token()
        # 获取商店（夜市是相同接口）
        resp = await Riot.fetch_daily_shop(riotUser)
        if "BonusStore" not in resp:  # 如果没有这个字段，说明夜市取消了
            NightMarketOff = False
            cm1 = await get_card_msg("嗷~ 夜市已关闭 或 Api没能正确返回结果", "night_market closed! 'BonusStore' not in resp",
                                    icon_cm.duck)
            await upd_card(send_msg['msg_id'], cm1, channel_type=msg.channel_type)  # 更新消息
            _log.error("night_market closed! | 'BonusStore' not in resp")
            return

        timeout = resp["BonusStore"]["BonusStoreRemainingDurationInSeconds"]  #剩余时间
        timeout = time.strftime("%d %H:%M:%S", time.gmtime(timeout))  #将秒数转为标准时间

        cm = CardMessage()
        c = Card(color='#fb4b57')
        c.append(
            Module.Header(
                f"玩家「{auth.Name}#{auth.Tag}」的夜市！"))
        for Bonus in resp["BonusStore"]["BonusStoreOffers"]:
            # 获取皮肤信息
            skin = Local.fetch_skin_bylist(Bonus["Offer"]["OfferID"])
            skin_icon = skin["data"]['levels'][0]["displayIcon"]
            skin_name = skin["data"]["displayName"]
            # 获取皮肤的等级
            res_iters = Local.fetch_skin_iters_bylist(Bonus["Offer"]["OfferID"])
            # 从预先上传的自定义emoji里面，选择一个和皮肤等级对应的emoji
            iter_emoji = ValItersEmoji[res_iters['data']['devName']] 
            basePrice = Bonus["Offer"]["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #原价
            discPercent = Bonus["DiscountPercent"]  # 打折百分比
            discPrice = Bonus["DiscountCosts"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]  #打折后的价格
            text = f"(emj){res_iters['data']['uuid']}(emj)[{iter_emoji}] {skin_name}\n"
            text += f"(emj)vp(emj)[{ValItersEmoji['vp']}] {discPrice} ~~{basePrice}~~ {discPercent}%Off"
            #c.append(Module.Section(Element.Text(text, Types.Text.KMD), Element.Image(src=skin_icon, size='sm')))
            c.append(Module.Section(Element.Text(text, Types.Text.KMD)))

        # 结束计时
        using_time = format(time.perf_counter() - start, '.2f')
        c.append(Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {using_time}s"))
        cm.append(c)
        # 更新消息
        await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
        _log.info(f"Au:{msg.author_id} | night_market reply success [{using_time}]")

    except requester.HTTPRequester.APIRequestFailed as result:  #卡片消息发送失败
        await BotLog.APIRequestFailed_Handler("night", traceback.format_exc(), msg, bot, cm, send_msg=send_msg)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("night", traceback.format_exc(), msg, send_msg=send_msg)


# 设置全局变量，打开/关闭夜市
@bot.command(name='open-nm')
async def open_night_market(msg: Message, *arg):
    BotLog.logMsg(msg)
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
        await BotLog.BaseException_Handler("open-nm", traceback.format_exc(), msg)


# 获取玩家卡面(添加point的别名)
@bot.command(name='uinfo', aliases=['point', 'UINFO', 'POINT'])
async def get_user_card(msg: Message, *arg):
    BotLog.logMsg(msg)
    if LoginForbidden:
        await LoginForbidden_send(msg)
        return
    # 初始化变量
    send_msg = {'msg_id':''}
    cm = CardMessage()
    try:
        # 1.判断用户是否登录
        if msg.author_id not in UserAuthCache['kook']:
            await msg.reply(await get_card_msg("您尚未登陆！请「私聊」使用login命令进行登录操作", f"「/login 账户 密码」请确认您知晓这是一个风险操作", icon_cm.whats_that))
            return
        # 1.1 发送开始的提示信息
        cm = await get_card_msg("获取您所有账户的 玩家卡面/VP/R点", "阿狸正在施法！很快就好啦~", icon_cm.rgx_card,card_color="#BBFFFF")
        send_msg = await msg.reply(cm)
        # 2.uinfo直接使用for循环来获取不同用户的信息
        cm = CardMessage()
        for riot_user_id in UserAuthCache['kook'][msg.author_id]:
            try:
                # 执行cookie重登
                reau = await Reauth.check_reauth("玩家信息",msg.author_id,riot_user_id,debug_ch,msg)
                if reau == False: return  #如果为假说明重新登录失败

                if isinstance(reau, dict):  # 如果传过来的是一个dict，说明重新登录成功且发送了消息
                    await upd_card(reau['msg_id'], cm, channel_type=msg.channel_type)
                    send_msg = reau  # 再次覆盖更新消息

                auth = UserAuthCache['data'][riot_user_id]['auth']
                assert isinstance(auth, EzAuth)
                riotUser = auth.get_riotuser_token()
                resp = await Riot.fetch_player_loadout(riotUser)  #获取玩家装备栏
                player_card = await Assets.fetch_playercard(resp['Identity']['PlayerCardID'])  #玩家卡面id
                player_title = await Assets.fetch_title(resp['Identity']['PlayerTitleID'])  #玩家称号id
                if 'data' not in player_card or player_card['status'] != 200:
                    player_card = {'data': {'wideArt': 'https://img.kookapp.cn/assets/2022-09/PDlf7DcoUH0ck03k.png'}}
                    _log.warning(f"player_card | Au:{msg.author_id} | uuid:{resp['Identity']['PlayerCardID']}")
                if 'data' not in player_title or player_title['status'] != 200:
                    player_title = {
                        'data': {
                            "displayName": f"未知玩家卡面uuid！\nUnknow uuid: `{resp['Identity']['PlayerTitleID']}`"
                        }
                    }
                    _log.warning(f"player_title | Au:{msg.author_id} | uuid:{resp['Identity']['PlayerTitleID']}")
                # 可能遇到全新账户（没打过游戏）的情况
                if resp['Guns'] == None or resp['Sprays'] == None:
                    c = await get_card_msg(f"玩家「{auth.Name}#{auth.Tag}」状态错误！", 
                                        f"您可能登录了一个全新账户（没打过瓦）\ncard:\n```\n{player_card}\n```\ntitle:\n```\n{player_title}\n```",
                                        icon_cm.whats_that)
                    cm.append(c)
                    continue

                # 获取玩家等级
                resp = await Riot.fetch_player_level(riotUser)
                player_level = resp["Progress"]["Level"]  # 玩家等级
                player_level_xp = resp["Progress"]["XP"]  # 玩家等级经验值
                last_fwin = resp["LastTimeGrantedFirstWin"]  # 上次首胜时间
                next_fwin = resp["NextTimeFirstWinAvailable"]  # 下次首胜重置
                c = Card(color='#fb4b57')
                c.append(
                    Module.Header(
                        f"玩家「{auth.Name}#{auth.Tag}」的个人信息"))
                c.append(Module.Container(Element.Image(src=player_card['data']['wideArt'])))  #将图片插入进去
                text = f"玩家称号：" + player_title['data']['displayName'] + "\n"
                text += f"玩家等级：{player_level}  -  经验值：{player_level_xp}\n"
                text += f"上次首胜：{last_fwin}\n"
                text += f"首胜重置：{next_fwin}"
                c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
                #获取玩家的vp和r点剩余的text
                resp = await Riot.fetch_vp_rp_dict(riotUser)
                text = f"(emj)r点(emj)[{ValItersEmoji['rp']}] RP  {resp['rp']}    "
                text += f"(emj)vp(emj)[{ValItersEmoji['vp']}] VP  {resp['vp']}\n"
                c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
                cm.append(c)
            except KeyError as result:
                for i in ["Progress","Identity","Balances"]:
                    if i in str(result):
                        _log.exception(f"KeyErr '{i}' | Ru:{riot_user_id}")
                        cm2 = await get_card_msg(f"键值错误，需要重新登录", f"KeyError:{result}, please re-login", icon_cm.lagging)
                        await upd_card(send_msg['msg_id'], cm2, channel_type=msg.channel_type)
                        continue
                else: 
                    raise result
        
        # 多个账户都获取完毕，发送卡片并输出结果
        if cm:
            await upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            _log.info(f"Au:{msg.author_id} | uinfo reply successful!")
        else: raise Exception("卡片消息cm为空，消息初始化失败")
    except requester.HTTPRequester.APIRequestFailed as result:  # 卡片消息发送失败
        await BotLog.APIRequestFailed_Handler("uinfo", traceback.format_exc(), msg, bot, cm, send_msg=send_msg)
    except Exception as result:
        await BotLog.BaseException_Handler("uinfo", traceback.format_exc(), msg, send_msg=send_msg)


# 获取捆绑包信息(无需登录)
@bot.command(name='bundle', aliases=['skin'])
async def get_bundle(msg: Message, *arg):
    BotLog.logMsg(msg)
    if arg == ():
        await msg.reply(f"函数参数错误，name: `{arg}`\n")
        return
    try:
        name = " ".join(arg)  # 补全函数名
        name = zhconv.convert(name, 'zh-tw')  #将名字繁体化
        # 不能一来就在武器列表里面找，万一用户输入武器名，那就会把这个武器的所有皮肤都找出来，和该功能的需求不符合
        for b in ValBundleList:  #在本地查找
            if name in b['displayName']:
                # 确认在捆绑包里面有这个名字之后，在查找武器（这里不能使用displayName，因为有些捆绑包两个版本的名字不一样）
                weapenlist = await Local.fetch_bundle_weapen_byname(name)
                cm = CardMessage()
                c = Card(Module.Section(Element.Text(f"已为您查询到 `{name}` 相关捆绑包", Types.Text.KMD)))
                for b in ValBundleList:
                    if name in b['displayName']:  # 将图片插入 卡片消息
                        c.append(Module.Container(Element.Image(src=b['displayIcon2'])))
                if weapenlist != []:  # 遇到“再来一局”这种旧皮肤捆绑包，找不到武器名字
                    text = "```\n"
                    for w in weapenlist:
                        res_price = Local.fetch_item_price_bylist(w['lv_uuid'])
                        if res_price != None:  # 有可能出现返回值里面找不到这个皮肤的价格的情况，比如冠军套
                            price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
                            text += '%-28s\t- vp%5s\n' % (w['displayName'], price)
                        else:  # 找不到价格就直接插入武器名字
                            text += f"{w['displayName']}\n"

                    text += "```\n"
                    c.append(Module.Section(Element.Text(text, Types.Text.KMD)))  #插入皮肤
                cm.append(c)
                await msg.reply(cm)
                _log.info(f"Au:{msg.author_id} | get_bundle reply successful!")
                return

        await msg.reply(f"未能查找到结果，请检查您的皮肤名拼写")
        _log.info(f"Au:{msg.author_id} | get_bundle failed! Can't find {name}")
    except Exception as result:
        await BotLog.BaseException_Handler("bundle", traceback.format_exc(), msg)


# 设置rate的错误用户
@bot.command(name='ban-r')
async def set_rate_err_user(msg: Message, user_id: str):
    BotLog.logMsg(msg)
    try:
        global SkinRateDict
        if msg.author_id != master_id:
            await msg.reply(f"您没有权限执行此命令！")
            return
        
        if user_id in SkinRateDict['err_user']:
            await msg.reply(f"该用户已在SkinRateDict['err_user']列表中")
        elif user_id in SkinRateDict['data']:
            for skin, info in SkinRateDict['data'][user_id].items():
                # 找到这条评论，将其删除
                if not await ShopRate.remove_UserRate(skin, user_id):
                    await msg.reply(f"Au:{user_id} 删除 {skin} [{info['name']}] 错误")

            # 删除完该用户的所有评论之后，将其放入err_user
            temp_user = copy.deepcopy(SkinRateDict['data'][user_id])
            del SkinRateDict['data'][user_id]
            SkinRateDict['err_user'][user_id] = temp_user
            await msg.reply(f"用户 {user_id} 已被加入SkinRateDict['err_user']列表")
            _log.info(f"rate_err_user | add Au:{user_id} | file saved")
    except Exception as result:
        await BotLog.BaseException_Handler("bundle", traceback.format_exc(), msg)

# 每月1日删除违规用户
@bot.task.add_cron(day=1, timezone="Asia/Shanghai")
async def clear_rate_err_user():
    global SkinRateDict
    SkinRateDict['err_user'] = {}
    SkinRateDict.save()# 写入文件
    _log.info(f"[BOT.TASK] clear_rate_err_user")


# 给一个皮肤评分（灵感来自微信小程序”瓦的小卖铺“）
@bot.command(name="rate", aliases=['评分'])
async def rate_skin_add(msg: Message, *arg):
    BotLog.logMsg(msg)
    if check_rate_err_user(msg.author_id):
        await msg.reply(f"您有过不良评论记录，阿狸现已不允许您使用相关功能\n后台存放了所有用户的评论内容和评论时间。在此提醒，请不要在评论的时候发送不雅言论！")
        return
    elif arg == ():
        await msg.reply(f"你没有提供皮肤参数！skin: `{arg}`\n正确用法：`/rate 您想评价的皮肤名`")
        return
    cm = CardMessage()
    try:
        name = " ".join(arg)
        retlist = await ShopRate.get_available_skinlist(name)
        if retlist == []:  # 空list，有问题
            await msg.reply(f"该皮肤不在列表中[或没有价格]，请重新查询！")
            return

        # 将皮肤list插入到选择列表中，用户使用/rts命令选择
        UserRtsDict[msg.author_id] = retlist
        # 获取选择列表的text
        ret = await ShopRate.get_skinlist_rate_text(retlist, msg.author_id)
        text = f"```\n{ret['text']}```"

        cm = CardMessage()
        c = Card(Module.Header(f"查询到 {name} 相关皮肤如下"), Module.Section(Element.Text(text, Types.Text.KMD)),
                 Module.Section(Element.Text("请使用以下命令对皮肤进行评分;\n√代表您已评价过该皮肤，+已有玩家评价，-无人评价\n", Types.Text.KMD)))
        text1 = "```\n/rts 序号 评分 吐槽\n"
        text1 += "序号：上面列表中的皮肤序号\n"
        text1 += "评分：给皮肤打分，范围0~100\n"
        text1 += "吐槽：说说你对这个皮肤的看法\n"
        text1 += "吐槽的时候请注意文明用语！\n```\n"
        text1 += f"您已经评价过了 {ret['sum']} 个皮肤"
        c.append(Module.Section(Element.Text(text1, Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)

    except requester.HTTPRequester.APIRequestFailed as result:  #卡片消息发送失败
        await BotLog.APIRequestFailed_Handler("rate", traceback.format_exc(), msg, bot, cm)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("rate", traceback.format_exc(), msg)


#选择皮肤（这个命令必须跟着上面的命令用）
@bot.command(name="rts")
async def rate_skin_select(msg: Message, index: str = "err", rating: str = "err", *arg):
    BotLog.logMsg(msg)
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
    cm = CardMessage()
    try:
        if msg.author_id in UserRtsDict:
            _index = int(index)  #转成int下标（不能处理负数）
            _rating = int(rating)  #转成分数
            if _index >= len(UserRtsDict[msg.author_id]):  #下标判断，避免越界
                await msg.reply(f"您的选择越界了！请正确填写序号")
                return
            elif _rating < 0 or _rating > 100:
                await msg.reply(f"您的评分有误，正确范围为0~100")
                return

            S_skin = UserRtsDict[msg.author_id][_index]
            skin_uuid = S_skin['skin']['lv_uuid']
            comment = " ".join(arg)  #用户对此皮肤的评论
            point = _rating  # 初始化分数
            text1 = ""
            text2 = ""
            # 先从leancloud获取该皮肤的分数
            skin_rate = await ShopRate.query_SkinRate(skin_uuid)
            if skin_rate['status']:  # 找到了
                #用户的评分和皮肤平均分差值不能超过32，避免有人乱刷分
                if abs(float(_rating) - skin_rate['rating']) <= 32:
                    # 计算分数
                    point = (skin_rate['rating'] + float(_rating)) / 2
                else:  # 差值过大，不计入皮肤平均值
                    point = skin_rate['rating']
                    text2 += f"由于您的评分和皮肤平均分差值大于32，所以您的评分不会计入皮肤平均分，但您的评论会进行保留\n"

            # 更新数据库中皮肤评分
            await ShopRate.update_SkinRate(skin_uuid, S_skin['skin']['displayName'], point)
            # 用户之前没有评价过，新建键值
            if msg.author_id not in SkinRateDict['data']:
                SkinRateDict['data'][msg.author_id] = {}
            # 设置uuid的键值
            SkinRateDict['data'][msg.author_id][skin_uuid] = {}
            SkinRateDict['data'][msg.author_id][skin_uuid]['name'] = S_skin['skin']['displayName']
            SkinRateDict['data'][msg.author_id][skin_uuid]['cmt'] = comment
            SkinRateDict['data'][msg.author_id][skin_uuid]['rating'] = point
            SkinRateDict['data'][msg.author_id][skin_uuid]['time'] = int(time.time())  # 秒级
            SkinRateDict['data'][msg.author_id][skin_uuid]['msg_id'] = msg.id
            # 数据库添加该评论
            await ShopRate.update_UserRate(skin_uuid, SkinRateDict['data'][msg.author_id][skin_uuid], msg.author_id)
            # 更新用户已评价的皮肤
            await ShopRate.update_UserCmt(msg.author_id, skin_uuid)

            text1 += f"评价成功！{S_skin['skin']['displayName']}"
            text2 += f"您的评分：{_rating}\n"
            text2 += f"皮肤平均分：{point}\n"
            text2 += f"您的评语：{comment}"
            c = Card(Module.Header(text1), Module.Divider(), Module.Section(Element.Text(text2, Types.Text.KMD)))
            cm.append(c)
            # 设置成功并删除list后，再发送提醒事项设置成功的消息
            await msg.reply(cm)
            _log.info(f"[rts] Au:{msg.author_id} | {text1} {skin_uuid}")
        else:
            await msg.reply(f"您需要执行 `/rate 皮肤名` 来查找皮肤\n再使用 `/rts` 进行选择")

    except requester.HTTPRequester.APIRequestFailed as result:  #卡片消息发送失败
        await BotLog.APIRequestFailed_Handler("rts", traceback.format_exc(), msg, bot, cm)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("rts", traceback.format_exc(), msg)


# 查看昨日牛人/屌丝
@bot.command(name="kkn")
async def show_shoprate(msg: Message):
    BotLog.logMsg(msg)
    if check_rate_err_user(msg.author_id):
        await msg.reply(f"您有过不良评论记录，阿狸现已不允许您使用相关功能\n后台存放了所有用户的评论内容和评论时间。在此提醒，请不要在评论的时候发送不雅言论！")
        return
    cm = CardMessage()
    try:
        # 从数据库中获取
        cmpRet = await ShopRate.get_ShopCmp()
        if not cmpRet['status']:
            await msg.reply(f"获取昨日天选之子和丐帮帮主出错！请重试或联系开发者")
            return

        c = Card(Module.Header(f"来看看昨日天选之子和丐帮帮主吧！"), Module.Divider())
        # best
        text = ""
        c.append(Module.Section(Element.Text(f"**天选之子** 综合评分 {cmpRet['best']['rating']}", Types.Text.KMD)))
        c.append(Module.Context(f"来自 {cmpRet['best']['platform']} 平台"))
        for sk in cmpRet['best']['skin_list']:
            # 数据库中获取一个皮肤的评分情况
            skinRet = await ShopRate.query_SkinRate(sk)
            if skinRet['status']:
                skin_name = f"「{skinRet['skin_name']}」"
                text += f"%-50s\t\t评分: {skinRet['rating']}\n" % skin_name
        c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        c.append(Module.Divider())
        # worse
        text = ""
        c.append(Module.Section(Element.Text(f"**丐帮帮主** 综合评分 {cmpRet['worse']['rating']}", Types.Text.KMD)))
        c.append(Module.Context(f"来自 {cmpRet['worse']['platform']} 平台"))
        for sk in cmpRet['worse']['skin_list']:
            # 数据库中获取一个皮肤的评分情况
            skinRet = await ShopRate.query_SkinRate(sk)
            if skinRet['status']:
                skin_name = f"「{skinRet['skin_name']}」"
                text += f"%-50s\t\t评分: {skinRet['rating']}\n" % skin_name
        c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
        cm.append(c)
        await msg.reply(cm)

        _log.info(f"[kkn] Au:{msg.author_id} | reply success")
    except requester.HTTPRequester.APIRequestFailed as result:  #卡片消息发送失败
        await BotLog.APIRequestFailed_Handler("rts", traceback.format_exc(), msg, bot, cm)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("rts", traceback.format_exc(), msg)


# 检查用户是否在错误用户里面
async def check_notify_err_user(msg: Message):
    """Return(bool):
     - True: user in SkinNotifyDict['err_user']
     - False: user not in, everythings is good
    """
    global SkinNotifyDict
    if msg.author_id in SkinNotifyDict['err_user']:
        try:
            user = await bot.client.fetch_user(msg.author_id)
            await user.send(f"这是一个私聊测试，请忽略此条消息")  #先测试是否能发私聊
            # 可以发起，在err_user列表中删除该用户
            del SkinNotifyDict['err_user'][msg.author_id]
            return False
        except:
            err_cur = str(traceback.format_exc())
            err_str = f"ERR![{getTime()}] err_Au:{msg.author_id} user.send\n```\n{err_cur}\n```"
            if '屏蔽' in err_cur or '无法发起' in err_cur:
                await msg.reply(f"您之前屏蔽了阿狸，或阿狸无法向您发起私信\n您的皮肤提醒信息已经被`删除`，请在解除对阿狸的屏蔽后重新操作！\n{err_str}")
            else:
                err_str += "\n如果此错误多次出现，请[联系](https://kook.top/gpbTwZ)开发者"
                await msg.reply(err_str)
            # 不管出现什么错误，都返回True代表无法私信
            return True
    else:
        return False


#设置提醒（出现xx皮肤）
@bot.command(name="notify-add", aliases=['notify-a'])
async def add_skin_notify(msg: Message, *arg):
    BotLog.logMsg(msg)
    if arg == ():
        await msg.reply(f"你没有提供皮肤参数！skin: `{arg}`")
        return
    try:
        if await check_notify_err_user(msg):
            return
        # 检查用户的提醒栏位
        vip_status = await BotVip.vip_ck(msg.author_id)
        if msg.author_id in SkinNotifyDict['data'] and not vip_status:
            if len(SkinNotifyDict['data'][msg.author_id]) > NOTIFY_NUM:
                cm = await get_card_msg(f"您的皮肤提醒栏位已满", f"想解锁更多栏位，可以来[支持一下](https://afdian.net/a/128ahri?tab=shop)阿狸呢！",
                                    icon_cm.rgx_broken)
                await msg.reply(cm)
                return

        #用户没有登录
        if msg.author_id not in UserAuthCache['kook']:
            cm = await get_card_msg("您尚未登陆！请「私聊」使用login命令进行登录操作", f"「/login 账户 密码」请确认您知晓这是一个风险操作", icon_cm.whats_that)
            await msg.reply(cm)
            return

        name = " ".join(arg)
        name = zhconv.convert(name, 'zh-tw')  #将名字繁体化
        sklist = Local.fetch_skin_list_byname(name)
        if sklist == []:  #空list代表这个皮肤不在里面
            await msg.reply(f"该皮肤不在列表中，请重新查询！")
            return

        retlist = list()  #用于返回的list，因为不是所有搜到的皮肤都有价格，没有价格的皮肤就是商店不刷的
        for s in sklist:
            res_price = Local.fetch_item_price_bylist(s['lv_uuid'])
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

    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("notify-add", traceback.format_exc(), msg)


#选择皮肤（这个命令必须跟着上面的命令用）
@bot.command(name="sts")
async def select_skin_notify(msg: Message, n: str = "err", *arg):
    BotLog.logMsg(msg)
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
            await user_test.send(f"这是一个私信测试。请不要修改您的私信权限，以免notify功能无法正常使用")
            # 测试通过，继续后续插入
            S_skin = UserStsDict[msg.author_id][num]
            if msg.author_id not in SkinNotifyDict['data']:
                SkinNotifyDict['data'][msg.author_id] = {}
                SkinNotifyDict['data'][msg.author_id][S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            else:  #如果存在了就直接在后面添加
                SkinNotifyDict['data'][msg.author_id][S_skin['skin']['lv_uuid']] = S_skin['skin']['displayName']
            _log.debug(SkinNotifyDict['data'][msg.author_id])

            del UserStsDict[msg.author_id]  #删除选择页面中的list
            text = f"设置成功！已开启`{S_skin['skin']['displayName']}`的提醒"
            # 设置成功并删除list后，再发送提醒事项设置成功的消息
            await msg.reply(text)
            _log.info(f"[sts] Au:{msg.author_id} | {text}")
        else:
            await msg.reply(f"您需要（重新）执行 `/notify-a` 来设置提醒皮肤")
    except requester.HTTPRequester.APIRequestFailed as result:  #消息发送失败
        err_str = f"ERR! [{getTime()}] sts\n```\n{traceback.format_exc()}\n```\n"
        await bot.client.send(debug_ch, err_str)
        await BotLog.APIRequestFailed_Handler("sts", traceback.format_exc(), msg, bot)
    except Exception as result:  # 其他错误
        await BotLog.BaseException_Handler("sts", traceback.format_exc(), msg)


# 显示当前设置好了的皮肤通知
@bot.command(name="notify-list", aliases=['notify-l'])
async def list_skin_notify(msg: Message, *arg):
    BotLog.logMsg(msg)
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
        await BotLog.BaseException_Handler("notify-list", traceback.format_exc(), msg, debug_send=debug_ch)


# 删除已有皮肤通知
@bot.command(name="notify-del", aliases=['notify-d'])
async def delete_skin_notify(msg: Message, uuid: str = "err", *arg):
    BotLog.logMsg(msg)
    if uuid == 'err':
        await msg.reply(f"请提供正确的皮肤uuid：`{uuid}`")
        return
    try:
        if await check_notify_err_user(msg):
            return
        global SkinNotifyDict
        if msg.author_id in SkinNotifyDict['data']:
            if uuid in SkinNotifyDict['data'][msg.author_id]:
                _log.info(f"notify-d | Au:{msg.author_id} | {uuid} {SkinNotifyDict['data'][msg.author_id][uuid]}")
                await msg.reply(f"已删除皮肤：`{SkinNotifyDict['data'][msg.author_id][uuid]}`")
                del SkinNotifyDict['data'][msg.author_id][uuid]
            else:
                await msg.reply(f"您提供的uuid不在列表中！")
                return
    except Exception as result:
        await BotLog.BaseException_Handler("notify-del", traceback.format_exc(), msg, debug_send=debug_ch)


def check_night_market_status(resp:dict):
    """在notifytask中判断夜市有没有开，只会判断一次"""
    global NightMarketOff  #true代表夜市没有开启
    if NightMarketOff and "BonusStore" in resp: #夜市字段存在
        NightMarketOff = False  #夜市开启！

#独立函数，为了封装成命令+定时
async def auto_skin_notify():
    global SkinNotifyDict, SkinRateDict, UserShopCache, VipShopBgDict
    try:
        _log.info(f"[BOT.TASK.NOTIFY] Start")  #开始的时候打印一下
        UserShopCache["data"] = {}  # 清空用户的商店
        UserShopCache["clear_time"] = time.time() # 更新时间
        #清空昨日最好/最差用户的皮肤表
        SkinRateDict["kkn"] = copy.deepcopy(SkinRateDict["cmp"])
        SkinRateDict["cmp"]["best"]["list_shop"] = list()
        SkinRateDict["cmp"]["best"]["rating"] = 0
        SkinRateDict["cmp"]["worse"]["list_shop"] = list()
        SkinRateDict["cmp"]["worse"]["rating"] = 100
        # 更新数据库中的记录，并重置计数器
        await ShopRate.update_ShopCmp(SkinRateDict["kkn"]["best"], SkinRateDict["kkn"]["worse"], 'kook', True)
        _log.info(f"[BOT.TASK.NOTIFY] SkinRateDict/UserShopCache clear, sleep(10)")
        #睡10s再开始遍历（避免时间不准）
        await asyncio.sleep(10)
        _log.info(f"skin_notify Start")
        #加载vip用户列表
        VipUserD = copy.deepcopy(VipUserDict)
        err_count = 0  # 设置一个count来计算出错的用户数量
        log_vip_failed = f"reauthorize failed  = VipAu: "
        log_vip_not_login = f"not_in UserAuthCache = VipAu: "
        dailyshop_img_src = "https://img.kookapp.cn/assets/2023-02/5UxA8W06B70e803m.png"
        # 先遍历vip用户列表，获取vip用户的商店
        for vip, uinfo in VipUserD.items():
            riot_user_id = "none"
            cm = CardMessage()
            try:
                user = await bot.client.fetch_user(vip)
                if vip in UserAuthCache['kook']: 
                    start = time.perf_counter()  # 开始计时这个用户
                    for riot_user_id in UserAuthCache['kook'][vip]:
                        auth = UserAuthCache['data'][riot_user_id]['auth']
                        assert isinstance(auth, EzAuth)
                        # 重新登录,如果为假说明重新登录失败
                        if not await Reauth.check_reauth("早八Vip用户商店", vip,riot_user_id,debug_ch):
                            log_vip_failed += f"({vip})"
                            _log.debug(f"VipAu:{vip} | Riot:{riot_user_id} | reauthorize failed ")
                            continue
                        
                        shop_text = "" # 空字符串认为是False
                        a_start = time.perf_counter()  # 开始计时当前拳头用户
                        # 获取账户token
                        riotUser = auth.get_riotuser_token() 
                        a_time = time.time()  # 开始调用api的时间
                        resp = await Riot.fetch_daily_shop(riotUser)  # 获取每日商店
                        # 检查夜市是否开启
                        check_night_market_status(resp)
                        # 处理商店返回值             
                        list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
                        timeout = resp["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]  #剩余时间
                        timeout = time.strftime("%H:%M:%S", time.gmtime(timeout))  #将秒数转为标准时间
                        # 商店获取成功，记录时间消耗
                        log_time = f"[Api_shop] {format(time.time()-a_time,'.4f')} "
                        # 计算用户商店得分
                        await ShopRate.check_shop_rate(vip, list_shop)  
                        # vip用户会提前缓存当日商店，需要设置uuid来保证是同一个游戏用户
                        UserShopCache["data"][auth.user_id] = {
                            "kook_user_id": vip,
                            "SkinsPanelLayout":resp["SkinsPanelLayout"]
                        }
                        # 直接获取商店图片
                        draw_time = time.time()  # 开始计算画图需要的时间
                        # 获取用户的vp和rp
                        play_currency = await Riot.fetch_vp_rp_dict(riotUser) 
                        # 设置用户背景图，如果在则用，否则返回err
                        background_img = ('err' if vip not in VipShopBgDict['bg'] else
                                            VipShopBgDict['bg'][vip]["background"][0])
                        # 开始画图
                        img_ret = await ShopImg.get_shop_img_169(list_shop,
                                                                    vp=play_currency['vp'],
                                                                    rp=play_currency['rp'],
                                                                    bg_img_src=background_img)
                        # 画图成功
                        if img_ret['status']:
                            bg_shop = img_ret['value'] # 取出pil图片对象
                            img_shop_path = f"./log/img_temp_vip/shop/{vip}.png" # 缓存商店图片的本地路径
                            bg_shop.save(img_shop_path, format='PNG') # 保存到本地
                            # 打印画图日志
                            log_time += f"| [Draw] {format(time.time() - draw_time,'.4f')} | [Au] {vip} | [Riot] {riot_user_id}"
                            _log.info(log_time)
                            # 上传图片
                            dailyshop_img_src = await bot_upimg.client.create_asset(img_shop_path)  
                            # 缓存图片的url+设置图片缓存的时间
                            VipShopBgDict['cache'][auth.user_id] = { 'cache_img': dailyshop_img_src,'cache_time': time.time()} 
                            # 更新商店图片status为True，代表用户当天执行/shop命令不需再画图
                            if vip in VipShopBgDict['bg']: VipShopBgDict['bg'][vip]['status'] = True
                            _log.info(f"VipAu:{vip} | Riot:{riot_user_id} | {dailyshop_img_src}")
                        # 如果图片没有正常返回，那就发送文字版本
                        else: 
                            for skinuuid in list_shop:
                                res_item = Local.fetch_skin_bylist(skinuuid)  # 从本地文件中查找
                                res_price = Local.fetch_item_price_bylist(skinuuid)  # 在本地文件中查找
                                price = res_price['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'] # 皮肤价格
                                shop_text += f"{res_item['data']['displayName']}     - VP {price}\n"
                            # 获取完毕text，记录信息
                            _log.info(f"VipAu:{vip} | Riot:{riot_user_id} | img_draw err, using text")

                        # 结束shop的总计时 结果为浮点数，保留两位小数
                        using_time = format(time.perf_counter() - a_start, '.2f')
                        # 卡片消息发送图片或者text
                        c = Card(color='#fb4b57')
                        c.append(Module.Header(
                                    f"早安！玩家 {auth.Name}#{auth.Tag} 的每日商店"))
                        c.append(Module.Context(f"失效时间剩余: {timeout}    本次查询用时: {using_time}s"))
                        # 如果字符串不为空，代表图片获取失败，需要进行文字提醒
                        if not shop_text:
                            c.append(Module.Container(Element.Image(src=dailyshop_img_src)))
                        else:
                            c.append(Module.Section(Element.Text(shop_text, Types.Text.KMD)))
                            c.append(Module.Context(Element.Text(f"这里有没有你想要的枪皮呢？", Types.Text.KMD)))
                        # 单个拳头用户的卡片做好了
                        cm.append(c)
                    
                    # 多个拳头账户遍历完毕，发送信息
                    using_time = format(time.perf_counter() - start, '.2f')
                    if cm: await user.send(cm) # 卡片不为空才发送信息
                    _log.info(f"VipAu:{vip} | notify_shop success [{using_time}]")
                else:  #不在auth里面说明没有登录
                    log_vip_not_login += f"({vip})"
            except Exception as result:  #这个是用来获取单个用户的问题的
                err_count += 1
                err_str = f"VipAu:{vip} | Riot:{riot_user_id}\n```\n{traceback.format_exc()}\n```"
                err_str+= await Reauth.check_user_send_err(str(result),vip,True)
                if 'HTTPRequester.APIRequestFailed' in err_str:
                    err_str+= f"\ncm.dumps: {json.dumps(cm)}"
                _log.error(err_str)
                # 发送消息到debug频道
                await bot.client.send(debug_ch, err_str)  
        # 打印vip用户的log信息
        _log.info(log_vip_failed)
        _log.info(log_vip_not_login)

        # 再遍历所有用户的皮肤提醒
        log_failed = f"reauthorize failed  = Au: "
        log_not_login = f"not_in UserAuthCache = Au: "
        temp_SkinNotifyDict = copy.deepcopy(SkinNotifyDict)
        for aid, skin in temp_SkinNotifyDict['data'].items():
            riot_user_id = "none"
            try:
                user = await bot.client.fetch_user(aid)
                if aid in UserAuthCache['kook']:
                    # 遍历这个用户的拳头商店
                    for riot_user_id in UserAuthCache['kook'][aid]:
                        # 重新登录,如果为假说明重新登录失败
                        if not await Reauth.check_reauth("早八用户商店", aid,riot_user_id,debug_ch):
                            log_failed += f"({aid})"
                            continue
                        # 重登成功，进行后续操作
                        auth = UserAuthCache['data'][riot_user_id]['auth']
                        assert isinstance(auth, EzAuth)
                        riotUser = auth.get_riotuser_token()
                        # vip用户在前面已经获取过商店了，直接在缓存里面取
                        if await BotVip.vip_ck(aid) and auth.user_id in UserShopCache["data"]:
                            list_shop = UserShopCache["data"][auth.user_id]["SkinsPanelLayout"]["SingleItemOffers"]
                        else: # 非vip用户，调用api获取每日商店
                            resp = await Riot.fetch_daily_shop(riotUser)  # 获取每日商店
                            list_shop = resp["SkinsPanelLayout"]["SingleItemOffers"]  # 商店刷出来的4把枪
                            await ShopRate.check_shop_rate(aid, list_shop)  #计算非vip用户商店得分

                        # 然后再遍历列表查看是否有提醒皮肤
                        # 关于下面这一行参考 https://img.kookapp.cn/assets/2022-08/oYbf8PM6Z70ae04s.png
                        target_skin = [val for key, val in skin.items() if key in list_shop]
                        for name in target_skin:
                            _log.info(f"Au:{aid} | Riot:{riot_user_id} | skin_notify | {name}")
                            await user.send(f"[{getTime()}] 您的每日商店刷出`{name}`了，请上号查看哦！")
                    
                    # 打印这个说明这个用户正常遍历完了
                    _log.info(f"Au:{aid} | skin_notify finished")
                else:  #不在auth里面说明没有登录
                    log_not_login += f"({aid})"
            except Exception as result:  #这个是用来获取单个用户的问题的
                err_count += 1
                err_str = f"Au:{aid} | Riot:{riot_user_id}\n```\n{traceback.format_exc()}\n```"
                err_str+= await Reauth.check_user_send_err(str(result),aid,False)
                _log.error(err_str)
                await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道

        # 打印普通用户的log信息
        _log.info(log_failed)
        _log.info(log_not_login)
        # 完成遍历后，如果有删除才重新保存dict
        if temp_SkinNotifyDict != SkinNotifyDict:
            SkinNotifyDict.save()
            _log.info("save SkinNotifyDict")

        # 打印结束信息
        finish_str = f"[NOTIFY.TASK] Finish at {getTime()} [ERR {err_count}]"
        _log.info(finish_str)  # 正常完成
        await bot.client.send(debug_ch, finish_str)  #发送消息到debug频道
    except Exception as result:
        err_str = f"ERR! [{getTime()}] NOTIFY.TASK\n```\n{traceback.format_exc()}\n```"
        await bot.client.send(debug_ch, err_str)  # 发送消息到debug频道
        _log.exception("Exception occur")

# 早八自动执行
@bot.task.add_cron(hour=8, minute=0, timezone="Asia/Shanghai")
async def auto_skin_notify_task():
    await auto_skin_notify()

# 手动执行notify task
@bot.command(name='notify-test', aliases=['notify-t'])
async def auto_skin_notify_cmd(msg: Message, *arg):
    BotLog.logMsg(msg)
    if msg.author_id == master_id:
        await auto_skin_notify()


#######################################################################################################
#######################################################################################################


# 显示当前阿狸加入了多少个服务器，以及用户数量
@bot.command(name='log-list', aliases=['log-l', 'log'])
async def bot_log_list(msg: Message, *arg):
    BotLog.logMsg(msg)
    try:
        if msg.author_id != master_id:
            await msg.reply(f"您没有权限执行此命令！")
            return
        
        retDict = await BotLog.log_bot_list(msg)  # 获取用户/服务器列表
        res_text = await BotLog.log_bot_list_text(retDict)  # 获取text

        cm = CardMessage()
        c = Card(
            Module.Header(f"来看看阿狸当前的用户记录吧！"),
            Module.Context(
                f"服务器总数: {retDict['guild']['guild_total']}  活跃服务器: {retDict['guild']['guild_active']}  用户数: {retDict['user']['user_total']}  cmd: {retDict['cmd_total']}"
            ), Module.Divider())
        log_img_src = await bot_upimg.client.create_asset("../screenshot/log.png")
        c.append(Module.Container(Element.Image(src=log_img_src)))
        c.append(
            Module.Section(
                Struct.Paragraph(2, Element.Text(f"{res_text['name'][:5000]}", Types.Text.KMD),
                                    Element.Text(f"{res_text['user'][:5000]}", Types.Text.KMD))))  #限制字数才能发出来
        cm.append(c)
        await msg.reply(cm)           
    except:
        await BotLog.BaseException_Handler("log-list",traceback.format_exc(),msg)


@bot.command(name='mem')
async def proc_check(msg: Message, *arg):
    BotLog.logMsg(msg)
    try:
        if msg.author_id == master_id:
            cm = await BotLog.get_proc_info(start_time)
            await msg.reply(cm)
    except:
        await BotLog.BaseException_Handler("mem",traceback.format_exc(),msg)


#在阿狸开机的时候自动加载所有保存过的cookie
# 注册其他命令
from pkg.plugins import Funny,GrantRoles,Translate,BotStatus,Vip,Match,GameHelper,ValFileUpd,Mission

@bot.on_startup
async def loading_cache(bot: Bot):
    try:
        global debug_ch, cm_send_test
        cm_send_test = await bot_upimg.client.fetch_public_channel(config['channel']["img_upload_ch"])
        debug_ch = await bot.client.fetch_public_channel(config['channel']['debug_ch'])
        _log.info("[BOT.TASK] fetch_public_channel success")
        Funny.init(bot,debug_ch)
        GrantRoles.init(bot,master_id)
        Translate.init(bot,master_id)
        BotStatus.init(bot)
        Match.init(bot,debug_ch)
        GameHelper.init(bot)
        ValFileUpd.init(bot,bot_upimg,master_id)
        Vip.init(bot,bot_upimg,master_id,debug_ch,cm_send_test)
        Mission.init(bot,debug_ch)
        _log.info("[BOT.TASK] load plugins")
    except:
        _log.fatal("[BOT.TASK] startup task failed!")
        _log.exception("Exception occur")
        os._exit(-1)  #出现错误直接退出程序

    _log.info("[BOT.TASK] loading cookie start")
    global UserAuthCache
    log_str_success = "[BOT.TASK] load cookie success  = Au:"
    log_str_failed = "[BOT.TASK] load cookie failed!  = Au:"
    log_not_exits = "[BOT.TASK] cookie path not exists = Au:"
    # 遍历vip的用户dict
    TmpVipAuthLog = copy.deepcopy(VipAuthLog)
    for user, uinfo in TmpVipAuthLog.items():
        for ru in uinfo: # 遍历该用户已登录账户的uuid列表
            cookie_path = f"./log/cookie/{ru}.cke"
            # 如果路径存在，那么说明已经保存了这个vip用户的cookie
            if os.path.exists(cookie_path):
                auth = EzAuth()
                auth.load_cookies(cookie_path)  # 加载cookie
                ret_bool = await auth.reauthorize(exp_print=False)  # 尝试登录
                # True登陆成功
                if ret_bool:
                    # 只有登录成功了，再新建此键值
                    if user not in UserAuthCache['kook']: 
                        UserAuthCache['kook'][user] = []
                    # 插入用户登录信息
                    UserAuthCache['kook'][user].append(auth.user_id)
                    UserAuthCache['data'][auth.user_id] = {"auth": auth, "2fa": False}  #将对象插入
                    log_str_success += f"({user},{ru})"
                # 重登失败
                else:
                    del auth  # 删除对象
                    VipAuthLog[user].remove(ru) # 还需要删除该vip用户对象中的已登录信息
                    log_str_failed += f"({user},{ru})"
                    continue
            else:
                log_not_exits += f"({user},{ru})"
                continue
    # 结束任务
    _log.info("TASK.INFO\n\t" + log_str_success + "\n\t" + log_str_failed + "\n\t" + log_not_exits)
    _log.info(f"[BOT.TASK] loading user cookie finished")

    # api缓存的用户列表
    log_str_success = "[BOT.TASK] api load cookie success  = Au:"
    log_str_failed = "[BOT.TASK] api load cookie failed!  = Au:"
    log_not_exits = "[BOT.TASK] api cookie path not exists = Au:"
    # 遍历api用户列表，对应的是account:uuid
    for acc,ru in ApiAuthLog.items():
        cookie_path = f"./log/cookie/{ru}.cke"
        # 如果uuid存在，代表之前vip用户里面有这个对象，直接插入
        if ru in UserAuthCache['data']:
            UserAuthCache['api'][acc] = ru
            log_str_success += f"({acc},v)"
        # 如果路径存在，那么说明已经保存了这个vip用户的cookie
        elif os.path.exists(cookie_path):
            auth = EzAuth()
            auth.load_cookies(cookie_path)  #加载cookie
            ret_bool = await auth.reauthorize(exp_print=False)  #尝试登录
            if ret_bool:  # True登陆成功
                UserAuthCache['api'][acc] = auth.user_id
                UserAuthCache['data'][auth.user_id] = {"auth": auth, "2fa": False}  #将对象插入
                log_str_success += f"({acc})"
            else:
                del auth  # 删除对象
                log_str_failed += f"({acc})"
                continue
        else:
            log_not_exits += f"({acc})"
            continue
    # 结束任务
    _log.info("TASK.INFO\n\t" + log_str_success + "\n\t" + log_str_failed + "\n\t" + log_not_exits)
    _log.info(f"[BOT.TASK] loading api user cookie finished")
    await save_all_file() # 保存一下所有文件


# 开机 （如果是主文件就开机）
if __name__ == '__main__':
    # 开机的时候打印一次时间，记录开启时间
    _log.info(f"[BOT] Start at: [%s]" % start_time)
    bot.run()