# code from https://github.com/Prodzify/Riot-auth/blob/main/main.py
import ssl
import time
import asyncio
import copy
import random
import pandas
import requests
from requests.adapters import HTTPAdapter
from http.cookies import SimpleCookie
from typing import Any
from collections import OrderedDict
from re import compile

from riot_auth import RiotAuth
from endpoints.auth import EzAuthExp

RiotClient = "RiotClient/62.0.1.4852117.4789131"
User2faCode = {}
TFA_TIME_LIMIT = 600  # 600s时间限制

CIPHERS = [
    'ECDHE-ECDSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-CHACHA20-POLY1305', 'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305', 'ECDHE+AES128', 'RSA+AES128', 'ECDHE+AES256', 'RSA+AES256', 'ECDHE+3DES', 'RSA+3DES'
]


class URLS:
    AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
    REGION_URL = 'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant'
    VERIFED_URL = "https://email-verification.riotgames.com/api/v1/account/status"
    ENTITLEMENT_URL = 'https://entitlements.auth.riotgames.com/api/token/v1'
    USERINFO_URL = "https://auth.riotgames.com/userinfo"


class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *a: Any, **k: Any) -> None:
        c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        c.set_ciphers(':'.join(CIPHERS))
        k['ssl_context'] = c
        return super(SSLAdapter, self).init_poolmanager(*a, **k)


class EzAuth:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = OrderedDict({
            "User-Agent": f"{RiotClient} %s (Windows;10;;Professional, x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        })
        self.session.mount('https://', SSLAdapter())
        #self.p = self.print()

    def authorize(self, username, password, key):
        global User2faCode

        data = {
            "acr_values": "urn:riot:bronze",
            "claims": "",
            "client_id": "riot-client",
            "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
            "redirect_uri": "http://localhost/redirect",
            "response_type": "token id_token",
            "scope": "openid link ban lol_region",
        }
        data2 = {"language": "en_US", "password": password, "remember": "true", "type": "auth", "username": username}
        r = self.session.post(url=URLS.AUTH_URL, json=data)
        r = self.session.put(url=URLS.AUTH_URL, json=data2)
        data = r.json()
        tokens = ["", ""]  # 提前定义，避免下方出错（理论上来说应该走不到下面）

        if "access_token" in r.text:
            pattern = compile(
                'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
            data = pattern.findall(data['response']['parameters']['uri'])[0]
            token = data[0]
            token_id = data[1]
            tokens = [token, token_id]

        elif "auth_failure" in r.text:
            User2faCode[key] = {'status': False, 'err': "auth_failure, USER NOT EXIST", 
                                'start_time': time.time(),'2fa_status':True}
            print(F"[EzAuth] k:{key} auth_failure, USER NOT EXIST")
            raise EzAuthExp.AuthenticationError(User2faCode[key]['err'])

        elif 'rate_limited' in r.text:
            User2faCode[key] = {'status': False, 'err': "auth rate_limited", 'start_time': time.time(),'2fa_status':True}
            print(F"[EzAuth] k:{key} auth rate_limited")
            raise EzAuthExp.RatelimitError(User2faCode[key]['err'])

        else:  # 到此处一般是需要邮箱验证的用户
            print(f"[EzAuth] k:{key} 2fa user")
            User2faCode[key] = {
                'vcode': '',
                'status': False,
                'start_time': time.time(),
                '2fa_status': False,
                'err': None
            }
            # 开始等待用户提供邮箱验证码
            while (not User2faCode[key]['2fa_status']):
                if (time.time() - User2faCode[key]['start_time']) > TFA_TIME_LIMIT:
                    break  # 超过10分钟，以无效处理
                time.sleep(0.2) # 因为是线程执行操作，不能线程+异步
            
            # 再次判断，避免是超时break的
            if User2faCode[key]['2fa_status']:
                #需要用户通过命令键入邮箱验证码
                authdata = {
                    'type': 'multifactor',
                    'code': User2faCode[key]['vcode'],
                }
                r = self.session.put(url=URLS.AUTH_URL, json=authdata)
                data = r.json()
                if "access_token" in r.text:
                    pattern = compile(
                        'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
                    data = pattern.findall(data['response']['parameters']['uri'])[0]
                    token = data[0]
                    token_id = data[1]
                    tokens = [token, token_id]

                elif "auth_failure" in r.text:
                    User2faCode[key]['err'] = "2fa auth_failue"
                    print(F"[EzAuth] k:{key} {User2faCode[key]['err']}")  
                    raise EzAuthExp.MultifactorError(User2faCode[key]['err'])
                else: # 大概率是验证码错了
                    User2faCode[key]['err'] = "auth_failue, maybe wrong 2fa code"
                    print(F"[EzAuth] k:{key} {User2faCode[key]['err']}")
                    raise EzAuthExp.MultifactorError(User2faCode[key]['err'])
            else: # 2fa等待超出600s
                User2faCode[key]['err']="2fa wait overtime as 600s, wait failed"
                print(f"[EzAuth] k:{key} {User2faCode[key]['err']}")             
                raise EzAuthExp.WaitOvertimeError(User2faCode[key]['err'])

        # auth success
        self.access_token = tokens[0]
        self.id_token = tokens[1]

        self.base_headers = {
            'User-Agent': f"{RiotClient} %s (Windows;10;;Professional, x64)",
            'Authorization': f'Bearer {self.access_token}',
        }
        self.session.headers.update(self.base_headers)
        self.cookie = self.session.cookies

        self.entitlements_token = self.get_entitlement_token()
        self.emailverifed = self.get_emailverifed()

        userinfo = self.get_userinfo()
        self.user_id = userinfo['sub']
        self.Name = userinfo['name']
        self.Tag = userinfo['tag']
        self.creationdata = userinfo['create_data']
        self.typeban = userinfo['typeban']
        self.Region_headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.access_token}'}
        self.session.headers.update(self.Region_headers)
        self.Region = self.get_Region()
        # return self 
        User2faCode[key] = {
            'status': True,
            'auth': self,
            'err': None
        }
        print(f"[EzAuth] k:{key} auth success")

    def get_entitlement_token(self):
        r = self.session.post(URLS.ENTITLEMENT_URL, json={})
        entitlement = r.json()['entitlements_token']
        return entitlement

    def get_emailverifed(self):
        r = self.session.get(url=URLS.VERIFED_URL, json={})
        Emailverifed = r.json()["emailVerified"]
        return Emailverifed

    def get_userinfo(self):
        """ {'sub':Sub, 'name':Name, 'tag':Tag, 'create_datad':Createdat, 'typeban':typeban}
        """
        r = self.session.get(url=URLS.USERINFO_URL, json={})
        data = r.json()
        Sub = data['sub']
        data1 = data['acct']
        Name = data1['game_name']
        Tag = data1['tag_line']
        time4 = data1['created_at']
        time4 = int(time4)
        Createdat = pandas.to_datetime(time4, unit='ms')
        str(Createdat)
        data2 = data['ban']
        data3 = data2['restrictions']
        typeban = None
        if data3 != []:
            for x in data3:
                type = x['type']
                if type == "TIME_BAN":
                    for y in data3:
                        lol = y['dat']
                        exeperationdate = lol['expirationMillis']
                        time1 = exeperationdate
                        time1 = int(time1)
                        Exp = pandas.to_datetime(time1, unit='ms', errors="ignore")
                        str(Exp)
                    typeban = "TIME_BAN"
                if type == "PERMANENT_BAN":
                    typeban = "PERMANENT_BAN"
        if data3 == [] or "PBE_LOGIN_TIME_BAN" in data3 or "LEGACY_BAN" in data3:
            typeban = "None"
        return {'sub':Sub, 'name':Name, 'tag':Tag, 'create_data':Createdat, 'typeban':typeban}

    def get_Region(self):
        json = {"id_token": self.id_token}
        r = self.session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', json=json)
        data = r.json()
        Region = data['affinities']['live']
        return Region

    def print(self):
        print()
        print(f"Accestoken: {self.access_token}")
        print("-" * 50)
        print(f"Entitlements: {self.entitlements_token}")
        print("-" * 50)
        print(f"Userid: {self.user_id}")
        print("-" * 50)
        print(f"Region: {self.Region}")
        print("-" * 50)
        print(f"Name: {self.Name}#{self.Tag}")
        print("-" * 50)
        print(f"Createdat: {self.creationdata}")
        print("-" * 50)
        print(f"Bantype: {self.typeban}")

    def get_Token(self):
        userdict = {
            'auth_user_id': self.user_id,
            'access_token': self.access_token,
            'entitlements_token': self.entitlements_token
        }
        return userdict

    def get_CookieDict(self):
        # cookie转换成dict
        ck_dict = requests.utils.dict_from_cookiejar(self.cookie)
        return ck_dict

    async def get_RiotAuth(self):
        # cookie dict导入到SimpleCookie
        Scookie = SimpleCookie(self.get_CookieDict())
        rauth = RiotAuth()
        # 更新cookie
        rauth._cookie_jar.update_cookies(Scookie)
        ret = await rauth.reauthorize()  # 测试登录
        if ret:
            return rauth
        else:  #失败返回None
            raise Exception('EzAuth change to RiotAuth failed')


###################################### Riot Auth ######################################################


# 获取拳头的token
# 此部分代码来自 https://github.com/floxay/python-riot-auth
async def authflow(user: str, passwd: str):
    CREDS = user, passwd
    auth = RiotAuth()
    await auth.authorize(*CREDS)
    # await auth.reauthorize()
    # print(f"Access Token Type: {auth.token_type}\n",f"Access Token: {auth.access_token}\n")
    # print(f"Entitlements Token: {auth.entitlements_token}\n",f"User ID: {auth.user_id}")
    return auth


# 两步验证的用户
def auth2fa(user: str, passwd: str, key: str):
    auth = EzAuth()
    auth.authorize(user, passwd, key=key)


# 轮询检测的等待
async def auth2faWait(key, msg=None):
    while True:
        if key in User2faCode:
            # 如果2fa_status为假，代表是2fa且账户密码没有问题，需要用户提供vcode
            if not User2faCode[key]['2fa_status']:
                print(f"[auth2faWait] k:{key} 2fa Wait")
                if msg != None:
                    await msg.reply(f"您开启了邮箱双重验证，请使用「/tfa {key} 邮箱码」的方式验证\n栗子：若邮箱验证码为114514，那么您应该键入 `/tfa {key} 114514`"
                                    )

            # 开始循环检测status状态
            while (not User2faCode[key]['status']):
                # 不为none，出现错误
                if User2faCode[key]['err'] != None:
                    if 'rate_limited' in User2faCode[key]['err']:
                        raise EzAuthExp.RatelimitError(User2faCode[key]['err'])
                    elif 'auth_failure' in User2faCode[key]['err']:
                        raise EzAuthExp.AuthenticationError(User2faCode[key]['err'])
                    elif 'overtime' in User2faCode[key]['err']:
                        del User2faCode[key]
                        raise EzAuthExp.WaitOvertimeError(User2faCode[key]['err'])
                    else:
                        raise EzAuthExp.UnkownError(User2faCode[key]['err'])

                # 睡一会再检测
                await asyncio.sleep(0.3)

            # 如果退出且为真，代表登录成功了
            if User2faCode[key]['status']:
                ret = copy.deepcopy(User2faCode[key])
                del User2faCode[key]
                print(f"[auth2faWait] k:{key} Wait success,del key")
                return ret
            else: # 走到这里没有被raise，出现了未知错误
                print(f"[auth2faWait] k:{key} Wait failed, unkown err") 
                raise EzAuthExp.UnkownError("auth2faWait Failed")
        # key值不在，睡一会后再看看
        await asyncio.sleep(0.2)


async def Get2faWait_Key():
    ran = random.randint(1, 9999)
    while (ran in User2faCode):
        ran = random.randint(1, 9999)  # 创建一个1-9999的随机值
    # 直到创建出了一个不在其中的键值
    return ran