import traceback
from khl import Message, Channel
from aiohttp import client_exceptions
from .EzAuth import EzAuth, EzAuthExp
from ..file.Files import UserAuthCache, UserPwdReauth,SkinNotifyDict,bot,Boolean
from .api.Riot import fetch_valorant_point
from ..log.Logging import _log
from .. import KookApi, Gtime

LoginForbidden  = Boolean(False)
"""出现403错误，禁止重登; 初始值为false"""
NightMarketOff  = Boolean(True)
"""夜市是否关闭？False (on,夜市开着) | True (off,夜市关闭)"""

async def login_forbidden_send(msg: Message):
    """拳头api调用被403禁止的时候，发送提示信息"""
    text = f"拳头api登录接口出现403错误，已禁止登录相关功能的使用\n"
    text+= f"[https://img.kookapp.cn/assets/2022-09/oj33pNtVpi1ee0eh.png](https://img.kookapp.cn/assets/2022-09/oj33pNtVpi1ee0eh.png)"
    await msg.reply(await KookApi.get_card_msg(text))
    _log.info(f"Au:{msg.author_id} command failed | LoginForbidden: {LoginForbidden}")
    return None

def check_night_market_status(resp:dict) ->bool:
    """在notify.task中判断夜市有没有开，只会判断一次
    - True: 夜市已开启
    - False: 夜市关闭
    """
    if NightMarketOff and "BonusStore" in resp: #夜市字段存在
        NightMarketOff.set(False)  # 夜市开启！
        return True
    return False 

def client_exceptions_handler(result:str,err_str:str) -> str:
    """检查aiohttp错误的类型"""
    if 'auth.riotgames.com' and '403' in result:
        global LoginForbidden
        LoginForbidden.set(True)
        err_str += f"[check_reauth] 403 err! set LoginForbidden = True"
    elif '404' in result:
        err_str += f"[check_reauth] 404 err! network err, try again"
    else:
        err_str += f"[check_reauth] Unkown aiohttp ERR!"

    return err_str

# 检查是否有私聊错误
async def check_user_send_err(result:str,kook_user_id:str,is_vip:bool) ->str:
    """判断是否出现了无法私聊的问题，返回处理之后的日志"""
    text="\n"
    if '屏蔽' in result or '无法发起' in result:
        global SkinNotifyDict
        if not is_vip: # 非vip用户直接粗暴解决，删除用户
            del SkinNotifyDict['data'][kook_user_id] 
            text+=f"del SkinNotifyDict['data'][{kook_user_id}], "
        # 添加到err_user中
        SkinNotifyDict['err_user'][kook_user_id] = Gtime.getTime()
        text+= "add to ['err_user']"
        return text
    
    return ""

# cookie重新登录
async def login_reauth(kook_user_id: str, riot_user_id: str) -> bool:
    """Return:
    - True: reauthorize success
    - False: reauthorize failed
    """
    base_print = f"Au:{kook_user_id} | Riot:{riot_user_id} | "
    _log.info(base_print + "auth_token failure,trying reauthorize()")
    global UserAuthCache
    # 这个函数只负责重登录，所以直接找对应的拳头用户id
    auth = UserAuthCache['data'][riot_user_id]['auth']
    assert isinstance(auth, EzAuth)
    #用cookie重新登录,会返回一个bool是否成功
    ret = await auth.reauthorize()
    if ret:  #会返回一个bool是否成功,成功了重新赋值
        UserAuthCache['data'][riot_user_id]['auth'] = auth
        _log.info(base_print + "reauthorize() Successful!")
    else:  # cookie重新登录失败
        _log.info(base_print + "reauthorize() Failed! T-T")  # 失败打印
        # 有保存账户密码+不是邮箱验证用户
        if riot_user_id in UserAuthCache['acpw'] and (not auth.is2fa):
            auth = EzAuth()  # 用账户密码重新登录
            resw = await auth.authorize(UserAuthCache['acpw'][riot_user_id]['a'],
                                        UserAuthCache['acpw'][riot_user_id]['p'])
            if not resw['status']:  # 需要邮箱验证，那就直接跳出
                _log.info(base_print + "authorize() need 2fa, return False")
                return False
            # 更新auth对象
            UserAuthCache['data'][riot_user_id]['auth'] = auth
            auth.save_cookies(f"./log/cookie/{riot_user_id}.cke")  # 保存cookie
            # 记录使用账户密码重新登录的时间，和对应的账户
            UserPwdReauth[kook_user_id][Gtime.getTime()] = f"{auth.Name}#{auth.Tag}"
            _log.info(base_print + "authorize by account/passwd")
            ret = True
    # 正好返回auth.reauthorize()的bool
    return ret


# 判断是否需要重新获取token
async def check_reauth(def_name: str,
                       kook_user_id: str,
                       riot_user_id: str,
                       debug_ch: Channel,
                       msg: Message = None) -> bool | dict[str, str]:  # type: ignore
    """Args:
    - def_name: def_name call this def
    - kook_user_id: kook_user_id
    - riot_user_id: which riot account for reauth
    - debug_ch: channel for sending debug info
    - msg: khl.Message obj, only send info if msg != None

    Return value:
     - True: no need to reauthorize / get `user_id` as params & reauhorize success 
     - False: unkown err / reauthorize failed
     - send_msg(dict): get `Message` as params & reauhorize success
    """
    try:
        # 1.通过riot用户id获取对象
        auth = UserAuthCache['data'][riot_user_id]['auth']
        assert isinstance(auth, EzAuth)
        # 2.直接从对象中获取user的Token，并尝试获取用户的vp和r点
        riotUser = auth.get_riotuser_token()
        resp = await fetch_valorant_point(riotUser)
        # resp={'httpStatus': 400, 'errorCode': 'BAD_CLAIMS', 'message': 'Failure validating/decoding RSO Access Token'}
        # 3.如果没有这个键，会直接报错进except; 如果有这个键，就可以继续执行下面的内容
        test = resp['httpStatus']
        # 3.1 走到这里代表需要重登
        send_msg = {'msg_id': ''}
        # 3.2 如果传入params有消息对象msg，则提示用户
        if msg:
            text = f"获取「{def_name}」失败！正在尝试重新获取token，您无需操作"
            cm = await KookApi.get_card_msg(text, f"{resp['message']}", KookApi.icon_cm.im_good_phoniex)
            send_msg = await msg.reply(cm)

        # 4.传入kook id和拳头账户id，进行重登
        ret = await login_reauth(kook_user_id, auth.user_id)
        # 4.1 ret为True，正常重新登录，且params有消息对象
        if ret and msg:
            return send_msg  # 返回发送出去的消息（用于更新）
        # ret为False，重登失败，发送提示信息
        elif not ret and msg:
            text = f"重新获取token失败，请私聊「/login」重新登录\n"
            cm = await KookApi.get_card_msg(text, "Reauthorize Failed!", KookApi.icon_cm.crying_crab)
            await KookApi.upd_card(send_msg['msg_id'], cm, channel_type=msg.channel_type)
            return False

        return ret  #返回是否成功重登
    # aiohttp网络错误
    except client_exceptions.ClientResponseError as result:
        err_str = f"Au:{kook_user_id} | aiohttp ERR!\n```\n{traceback.format_exc()}\n```\n"
        err_str = client_exceptions_handler(str(result),err_str)
        _log.error(err_str)
        await bot.client.send(debug_ch, err_str)
        return False
    # 用户在EzAuth初始化完毕之前调用了其他命令
    except EzAuthExp.InitNotFinishError as result:
        _log.warning(f"Au:{kook_user_id} | EzAuth used before init")
        return False
    except Exception as result:
        if 'httpStatus' in str(result):
            _log.info(f"Au:{kook_user_id} | No need to reauthorize [{result}]")
            return True
        else:
            _log.exception("Unkown Exception occur")
            await bot.client.send(debug_ch, f"[check_reauth] Unkown ERR!\n{traceback.format_exc()}")
            return False