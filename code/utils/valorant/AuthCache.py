# 缓存登录对象
from .EzAuth import EzAuth
from ..file.Files import UserAuthCache,ApiAuthLog,_log

Auth2faCache = UserAuthCache['tfa']

async def cache_auth_object(platfrom:str,key:str,auth:EzAuth) -> None:
    """cache auth obj base on platform and key
    - platfrom: kook or api
    - key: kook_user_id or api-account
    - auth: EzAuth obj
    """
    _log.debug(f"enter def | {UserAuthCache}")
    # 如果是2fa用户，且键值不在缓存里面，认为是初次登录，需要提供邮箱验证码
    if auth.is2fa and key not in Auth2faCache:
        Auth2faCache[key] = auth # 将对象插入2fa的缓存
        return
    # 如果键值存在，认为是tfa登陆成功，删除临时键值
    elif auth.is2fa and key in Auth2faCache:
        if not auth.is_init(): return # 前提是已经初始化完毕了
        del Auth2faCache[key]
    
    # 如果对象没有成功初始化，说明还是有问题；不进行缓存，让用户重登
    if not auth.is_init():
        _log.warning(f"key:{key} | auth obj not init!")
        raise Exception("cache auth obj before init!")

    # 在data中插入对象
    UserAuthCache['data'][auth.user_id] = {"auth": auth, "2fa": auth.is2fa}

    # 判断缓存的来源
    if platfrom == 'kook':
        # 用户id键值不存在，新建key
        if key not in UserAuthCache['kook']:
            UserAuthCache['kook'][key] = []
        # 如果该账户已经登陆过了，则不进行操作
        if auth.user_id not in UserAuthCache['kook'][key]:
            UserAuthCache['kook'][key].append(auth.user_id) # 往用户id缓存list中插入Riot用户的uuid
    
    elif platfrom == 'api':
        # 往缓存键值中插入Riot用户的uuid (api的键值是用户账户，有唯一性，不需弄list)
        UserAuthCache['api'][key] = auth.user_id
        # 记录已缓存的用户账户（方便开机加载）
        ApiAuthLog[key] = auth.user_id
        # 保存cookie到本地
        auth.save_cookies(f"./log/cookie/{auth.user_id}.cke")
        _log.info(f"save cookies | './log/cookie/{auth.user_id}.cke'")
    
    _log.debug(f"exit def | {UserAuthCache}")

async def get_tfa_auth_object(key:str) -> EzAuth | None:
    """get auth obj (need 2fa verify code) base on key. Return None if key not in cache
    """
    _log.debug(f"enter def | {Auth2faCache}")
    if key not in Auth2faCache:
        return None
    else:
        return Auth2faCache[key]
    
async def get_auth_object(platfrom:str,key:str) -> list[dict[str,EzAuth]]|None:
    """get auth obj base on key. Return None if key not in cache
    - platfrom: kook or api
    """
    ret = list()
    if platfrom=="kook":
        _log.debug(f"enter def | {UserAuthCache}")
        if key not in UserAuthCache["kook"]:
            _log.info(f"platfrom: {platfrom} | key:{key} not in cache")
            return ret
        
        riot_user_id_list = UserAuthCache["kook"][key]
        for ru in riot_user_id_list:
            ret.append(UserAuthCache["data"][ru])
        
        return ret
    elif platfrom=="api":
        _log.debug(f"enter def | {UserAuthCache}")
        if key not in UserAuthCache["api"]:
            _log.info(f"platfrom: {platfrom} | key:{key} not in cache")
            return ret
        
        riot_user_id = UserAuthCache["api"][key]
        ret.append(UserAuthCache["data"][riot_user_id])
        return ret
    else:
        _log.error(f"platfrom '{platfrom}' invalid")
        return ret