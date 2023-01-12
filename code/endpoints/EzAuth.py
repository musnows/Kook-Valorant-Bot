# code from https://github.com/Prodzify/Riot-auth/blob/main/main.py
import ssl
from typing import Any
from collections import OrderedDict
import requests
from requests.adapters import HTTPAdapter
import pandas
from re import compile
import time
import asyncio
import copy
import random
from riot_auth import auth_exceptions,RiotAuth

RiotClient = "RiotClient/62.0.1.4852117.4789131"
User2faCode = {}
TFA_TIME_LIMIT = 600 # 600s时间限制

CIPHERS = [
	'ECDHE-ECDSA-AES128-GCM-SHA256',
	'ECDHE-ECDSA-CHACHA20-POLY1305',
	'ECDHE-RSA-AES128-GCM-SHA256',
	'ECDHE-RSA-CHACHA20-POLY1305',
	'ECDHE+AES128',
	'RSA+AES128',
	'ECDHE+AES256',
	'RSA+AES256',
	'ECDHE+3DES',
	'RSA+3DES'
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
        self.session.headers = OrderedDict({"User-Agent": f"{RiotClient} %s (Windows;10;;Professional, x64)","Accept-Language": "en-US,en;q=0.9","Accept": "application/json, text/plain, */*"})
        self.session.mount('https://', SSLAdapter()) 
        #self.p = self.print()
    
    def authorize(self,username, password,key):
        global User2faCode

        data = {"acr_values": "urn:riot:bronze","claims": "","client_id": "riot-client","nonce": "oYnVwCSrlS5IHKh7iI16oQ","redirect_uri": "http://localhost/redirect","response_type": "token id_token","scope": "openid link ban lol_region",}
        data2 = {"language": "en_US","password": password,"remember": "true","type": "auth","username": username}
        r = self.session.post(url=URLS.AUTH_URL, json = data)
        r = self.session.put(url=URLS.AUTH_URL, json = data2)
        data = r.json()

        if "access_token" in r.text:
            pattern = compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
            data = pattern.findall(data['response']['parameters']['uri'])[0]
            token = data[0]
            token_id = data[1]
            tokens = [token,token_id]

        elif "auth_failure" in r.text:
            print(F"[EzAuth] k:{key} auth_failure, USER NOT EXIST")
            User2faCode[key]= {'status':False,'err':"auth_failure, NOT EXIST",'start_time':time.time()}
            raise Exception("auth_failure")

        elif 'rate_limited' in r.text:
            print(F"[EzAuth] k:{key} auth rate limited")
            User2faCode[key]= {'status':False,'err':"auth rate_limited",'start_time':time.time()}
            raise Exception("auth rate_limited")
        
        else:# 到此处一般是需要邮箱验证的用户
            print(f"[EzAuth] k:{key} 2fa user")
            User2faCode[key]= {'vcode':'','status':False,'start_time':time.time(),'2fa_status':False,'err':None}
            while(not User2faCode[key]['2fa_status']):
                if (time.time()-User2faCode[key]['start_time'])>TFA_TIME_LIMIT:
                    break# 超过10分钟，以无效处理
                #await asyncio.sleep(0.2)
                time.sleep(0.2)
            # 再次判断，避免是超时的
            if User2faCode[key]['2fa_status']:
                #需要用户通过命令键入邮箱验证码
                authdata = {
                    'type': 'multifactor',
                    'code': User2faCode[key]['vcode'],
                }
                r = self.session.put(url=URLS.AUTH_URL, json=authdata)
                data = r.json()
                if "access_token" in r.text:
                    pattern = compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
                    data = pattern.findall(data['response']['parameters']['uri'])[0]
                    token = data[0]
                    token_id = data[1]
                    tokens = [token,token_id]

                elif "auth_failure" in r.text:
                    print(F"[EzAuth] k:{key} auth_failure") # banned (?)
                    User2faCode[key]['err']="2fa auth_failue"
                    raise Exception("2fa auth_failure")
                else:
                    print(F"[EzAuth] k:{key} 2fa unkown")
                    User2faCode[key]['err']="auth_failue, maybe wrong 2fa code"
                    raise Exception("unkown auth err, maybe wrong 2fa code")

        self.access_token = tokens[0]
        self.id_token = tokens[1]

        self.base_headers = {'User-Agent': f"{RiotClient} %s (Windows;10;;Professional, x64)",'Authorization': f'Bearer {self.access_token}',}
        self.session.headers.update(self.base_headers)

        self.entitlements_token = self.get_entitlement_token()
        self.emailverifed = self.get_emailverifed()

        userinfo = self.get_userinfo()
        self.user_id = userinfo[0]
        self.Name = userinfo[1]
        self.Tag = userinfo[2]
        self.creationdata = userinfo[3]
        self.typeban = userinfo[4]
        self.Region_headers =  {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.access_token}'}
        self.session.headers.update(self.Region_headers)
        self.Region = self.get_Region()
        # 搞定了之后，将userdict传入此处
        User2faCode[key]= {
            'status':True,
            'userdict':{
                'auth_user_id': self.user_id,
                'access_token': self.access_token,
                'entitlements_token': self.entitlements_token
            },
            'auth': self
        }
        print(f"[EzAuth] k:{key} auth success")


    def get_entitlement_token(self):
        r = self.session.post(URLS.ENTITLEMENT_URL, json={})
        entitlement = r.json()['entitlements_token']
        return entitlement

    def get_emailverifed(self):
        r = self.session.get(url=URLS.VERIFED_URL,json={})
        Emailverifed = r.json()["emailVerified"]
        return Emailverifed

    def get_userinfo(self):
        r = self.session.get(url=URLS.USERINFO_URL,json={})
        data = r.json()
        Sub = data['sub']
        data1 = data['acct']
        Name = data1['game_name']
        Tag = data1['tag_line']
        time4 = data1['created_at']
        time4 = int(time4)
        Createdat = pandas.to_datetime(time4,unit='ms')
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
                        Exp = pandas.to_datetime(time1,unit='ms', errors="ignore")
                        str(Exp)
                    typeban = "TIME_BAN"
                if type == "PERMANENT_BAN":
                    typeban = "PERMANENT_BAN"
        if data3 == [] or "PBE_LOGIN_TIME_BAN" in data3 or "LEGACY_BAN" in data3:
            typeban = "None"
        return [Sub,Name,Tag,Createdat,typeban]
    
    def get_Region(self):
        json = {"id_token": self.id_token}
        r = self.session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant',json=json)
        data = r.json()
        Region = data['affinities']['live']
        return Region
    
    def print(self):
        print()
        print(f"Accestoken: {self.access_token}")
        print("-"*50)
        print(f"Entitlements: {self.entitlements_token}")
        print("-"*50)
        print(f"Userid: {self.user_id}")
        print("-"*50)
        print(f"Region: {self.Region}")
        print("-"*50)
        print(f"Name: {self.Name}#{self.Tag}")
        print("-"*50)
        print(f"Createdat: {self.creationdata}")
        print("-"*50)
        print(f"Bantype: {self.typeban}")

    def get_Token(self):
        userdict = {
            'auth_user_id': self.user_id,
            'access_token': self.access_token,
            'entitlements_token': self.entitlements_token
        }
        return userdict

#EzAuth(username="",password="")


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
def auth2fa(user:str,passwd:str,key:str):
    auth = EzAuth()
    auth.authorize(user,passwd,key=key)

# 轮询检测的等待
async def auth2faWait(key,msg=None):
    while True:
        if key in User2faCode:
            # 如果status为假，代表是2fa用户
            if not User2faCode[key]['status']:
                print(f"[auth2faWait] k:{key} 2fa wait")
                if msg != None:
                    await msg.reply(f"您开启了邮箱双重验证，请使用「/tfa {key} 邮箱码」的方式验证\n栗子：若邮箱验证码为114514，那么您应该键入 `/tfa {key} 114514`")
            
            # 开始循环检测status状态
            while(not User2faCode[key]['status']):
                # 不为none，出现错误
                if User2faCode[key]['err'] != None:
                    if 'rate_limited' in User2faCode[key]['err']:
                        raise auth_exceptions.RiotRatelimitError
                    else:
                        raise Exception(User2faCode[key]['err'])
                # 这里 -3s 是为了让该线程更晚获取到信息，要在auth线程break之后才删除键值
                if (time.time()-User2faCode[key]['start_time']-3)>TFA_TIME_LIMIT: 
                    del User2faCode[key]
                    break # 超过10分钟，以无效处理

                # 睡一会再检测
                await asyncio.sleep(0.3)

            # 如果退出且为真，代表登录成功了
            if User2faCode[key]['status']:
                ret = copy.deepcopy(User2faCode[key])
                del User2faCode[key]
                print(f"[auth2faWait] k:{key} 2fa wait success,del key")
                return ret
            else: # 否则登陆失败
                print(f"[auth2faWait] k:{key} 2fa wait failed") # 因为默认给出的是账户密码错误，而2fa不会是这个问题
                raise Exception("[auth2faWait] 2fa wait failed, auth_failure")
        # key值不在，睡一会后再看看
        await asyncio.sleep(0.2)

async def Get2faWait_Key():
    ran = random.randint(1, 9999)
    while(ran in User2faCode): 
        ran = random.randint(1, 9999) # 创建一个1-9999的随机值
    # 直到创建出了一个不在其中的键值
    return ran