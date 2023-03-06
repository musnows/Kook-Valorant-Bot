import uuid
import time

# 所有token
from utils.FileManage import ApiTokenDict,_log
# token速率限制为10，检测周期为60s
TOKEN_RATE_LIMITED = 10
TOKEN_RATE_TIME = 60

#获取uuid
def get_uuid():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return get_timestamp_uuid


def save_token_files(text=''):
    global ApiTokenDict
    ApiTokenDict.save()
    _log.info(f"ApiTokenDict.save | {text}")


# 生成uuid
def create_token_uuid(num: int = 10, day: int = 30):
    """Args:
        num (int): Defaults to 10.
        day (int): Defaults to 30.

    Returns:
        str: text for uuid

    Keys:
    - days: token expiration date
    - prime: is token public? False(public)/True(private)
    - od_time: token overdue timestamp (init in first use)
    - last_uesed: token last_used time
    - rate_time: token rate_limit start time
    - rate_nums: token rate_limit count (use-count in 60s)
    - sum: token post/get count
    """
    global ApiTokenDict
    i = num
    NewUuid = list()  #当前创建的新uuid
    while (i > 0):
        uuid = str(get_uuid())
        ApiTokenDict['data'][uuid] = {
            'days': day,
            'prime': True,
            'od_time': 0,
            'last_used': time.time(),
            'rate_time': time.time(),
            'rate_nums': 0,
            'sum': 0
        }
        NewUuid.append(uuid)
        i -= 1

    # 更新uuid到文件
    save_token_files("token create")

    text = ""
    for uuid in NewUuid:
        text += f"{uuid}" + "\n"

    _log.info(f"Api token | create_token_uuid | num:{num} | day:{day}")
    return text


# 检查用户token是否失效或者不是token
async def token_ck(token: str):
    """    
    retuns:
        * True: is token
        * False: not token
    """
    global ApiTokenDict
    if token in ApiTokenDict['data']:
        # 判断token是否为第一次使用（是的话，根据days更新过期时间）
        if ApiTokenDict['data'][token]['od_time'] == 0:
            od_time = time.time() + ApiTokenDict['data'][token]['days'] * 86400
            ApiTokenDict['data'][token]['od_time']  = od_time
            save_token_files("token init use")
        # 用户的token是否过期？
        if time.time() > ApiTokenDict['data'][token]['od_time']:
            # 过期了，删除该token
            del ApiTokenDict['data'][token]
            # 更新本地文件
            save_token_files("token expire")
            _log.info(f"T:{token} | out of date")
            return False
        else:  # 没有过期，返回真
            _log.info(f"T:{token} | is token")
            return True
    else:  # token不在
        _log.info(f"T:{token} | not token")
        return False


# 检测速率（一分钟只允许10次）
async def check_token_rate(token: str):
    global ApiTokenDict
    ret = await token_ck(token) # 判断token合法性
    if ret:
        cur_time = time.time()
        # 当前时间和rate计数开始时间的差值
        time_diff = cur_time - ApiTokenDict['data'][token]['rate_time']
        # token的总使用次数+1
        ApiTokenDict['data'][token]['sum'] += 1
        # rate_nums为0，代表是当前检测周期的初次使用
        if ApiTokenDict['data'][token]['rate_nums'] == 0:  
            ApiTokenDict['data'][token]['rate_time'] = cur_time
            ApiTokenDict['data'][token]['rate_nums'] = 1
            # save_token_files("token init use") 
            return {'status': True, 'message': 'first use', 'info': '一切正常'}
        # rate_nums不为0，代表检测周期内有调用
        elif time_diff <= TOKEN_RATE_TIME:  # 和上次调用的时间差在60s以内
            # 调用的次数超过10次，触发速率限制
            if ApiTokenDict['data'][token]['rate_nums'] > TOKEN_RATE_LIMITED:
                return {'status': False, 'message': 'token rate limited!', 'info': '速率限制，请稍后再试'}
            else:  # 没有引发速率限制
                ApiTokenDict['data'][token]['rate_nums'] += 1
                return {'status': True, 'message': 'time_diff <= 60, in rate', 'info': '一切正常'}
        else:  # 时间超过60s
            # save_token_files("rate check")
            # 重置rate_time为当前时间，重置计数器（开始新一轮速率检测）
            ApiTokenDict['data'][token]['rate_time'] = cur_time
            ApiTokenDict['data'][token]['rate_nums'] = 0
            return {'status': True, 'message': 'time_diff > 60', 'info': '一切正常'}
    else: # 压根不是一个合法的token
        return {'status': False, 'message': 'token not in dict', 'info': '无效token'}

# 在此处手动添加token
# text = create_token_uuid(1,5)
# print(text)