import uuid
import json
import time

# 所有token
with open("./log/UserToken.json", 'r', encoding='utf-8') as frpr:
    UserTokenDict = json.load(frpr)

#获取uuid
def get_uuid():
    get_timestamp_uuid = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    return get_timestamp_uuid


def save_token_files():
    global UserTokenDict
    with open("./log/UserToken.json", 'w', encoding='utf-8') as fw2:
        json.dump(UserTokenDict, fw2, indent=2, sort_keys=True, ensure_ascii=False)
    print("[Token] files saved!")

# 生成uuid
def create_token_uuid(num: int = 10, day: int = 30):
    """_summary_

    Args:
        num (int): Defaults to 10.
        day (int): Defaults to 30.

    Returns:
        str: text for uuid
    """
    global UserTokenDict
    i = num
    NewUuid = list()  #当前创建的新uuid
    while (i > 0):
        uuid = str(get_uuid())
        UserTokenDict['data'][uuid] = {
            'days': day, 
            'prime': False,
            'od_time': time.time()+day*86400,
            'last_used':time.time(),
            'rate_time':time.time(),
            'rate_nums':0,
            'sum':0
        }
        if day > 3000: #永久会员
            UserTokenDict['data'][uuid]['prime'] = True
        NewUuid.append(uuid)
        i -= 1

    # 更新uuid
    save_token_files()

    text = ""
    for uuid in NewUuid:
        text += f"{uuid}" + "\n"

    print(f"[token] create_token_uuid - num:{num} - day:{day}")
    return text

# text = create_token_uuid(1,5)
# print(text)

# 检查用户token是否失效或者不是token
async def token_ck(token:str):
    """    
    retuns:
        * True: is token
        * False: not token
    """
    # 检查
    global UserTokenDict
    if token in UserTokenDict['data']:
        #用户的token是否过期？
        if time.time() > UserTokenDict['data'][token]['od_time']:
            del UserTokenDict['data'][token]
            # 更新uuid
            save_token_files()
            print(f"[token-ck] T:{token} out of date")
            return False
        else:#没有过期，返回真
            print(f"[token-ck] T:{token} is token")
            return True
    else:#token不在
        print(f"[token-ck] T:{token} not token")
        return False