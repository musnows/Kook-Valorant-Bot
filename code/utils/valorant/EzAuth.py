# repo: https://github.com/musnows/Riot-auth
import ssl
import json
import time
import pandas
import requests
from requests.adapters import HTTPAdapter
from typing import Any
from collections import OrderedDict
from re import compile

from . import EzAuthExp
# get latest version: https://valorant-api.com/v1/version
X_RIOT_CLIENTVERSION = "RiotClient/63.0.9.4909983.4789131"
X_RIOT_CLIENTVPLATFROM =  "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
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


# 用于valorant api调用的UserDict
class RiotUserToken:

    def __init__(self, user_id: str, access_token: str, entitlements: str, region: str) -> None:
        self.user_id = user_id
        self.access_token = access_token
        self.entitlements_token = entitlements
        self.region = region


class EzAuth:

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers = OrderedDict({
            "User-Agent": f"{X_RIOT_CLIENTVERSION} %s (Windows;10;;Professional, x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        })
        self.session.mount('https://', SSLAdapter())
        self.is2fa = False  # 2fa set to false
        self.__mfa_start__ = 0  # 2fa start time
        self.__is_init__ = False # is_init finised?

    def __set_userinfo(self) -> None:
        """set_user_info to value"""
        userinfo = self.get_userinfo()
        self.user_id = userinfo['sub']
        self.Name = userinfo['name']
        self.Tag = userinfo['tag']
        self.creationdata = userinfo['create_data']
        self.typeban = userinfo['typeban']

    def __set_region(self) -> None:
        self.Region_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'{self.token_type} {self.access_token}'
        }
        self.Region = self.get_region(self.Region_headers)

    def __set_access_token(self, data: dict) -> dict[str, Any]:
        """get access_token from response"""
        pattern = compile(
            'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*token_type=((?:[a-zA-Z]|\d|)*).*expires_in=(\d*)'
        )
        p_data = pattern.findall(data['response']['parameters']['uri'])[0]
        tokens = {"access_token": p_data[0], "id_token": p_data[1], "token_type": p_data[2], "expires_in": p_data[3]}
        return tokens

    def __set_info(self, tokens: dict) -> None:
        """auth/reauth success, set entitlements_token, userinfo & region.\n
        Args:
        - tokens: return value of __set_access_token()
        """
        self.access_token = tokens['access_token']
        self.id_token = tokens['id_token']
        self.token_type = tokens['token_type']

        self.base_headers = {
            "User-Agent": f"{X_RIOT_CLIENTVERSION} %s (Windows;10;;Professional, x64)",
            "Authorization": f"{self.token_type} {self.access_token}",
        }
        self.session.headers.update(self.base_headers)

        self.entitlements_token = self.get_entitlement_token()
        self.__set_userinfo()
        self.__set_region()
        self.__is_init__ = True # set init as finised

    async def authorize(self, username, password) -> dict:
        """Authenticate using username and password.\n
        if username & password empty, using cookie reauth\n
        Return: 
         - {"status":True,"auth":self,"2fa":self.is2fa}
         - {"status":False,"auth":self,"2fa_status":self.is2fa}
         if False, using email_verify() to send verify code
        """
        if username and password:
            self.session.cookies.clear()  # not reauth, clear cookie

        token = {"access_token": "", "id_token": "", "token_type": "Bearer", "expires_in": '0'}
        body = {
            "acr_values": "urn:riot:bronze",
            "claims": "",
            "client_id": "riot-client",
            "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
            "redirect_uri": "http://localhost/redirect",
            "response_type": "token id_token",
            "scope": "openid link ban lol_region",
        }
        r = self.session.post(url=URLS.AUTH_URL, json=body)
        data = r.json()
        resp_type = data["type"]

        if resp_type != "response":  # not reauth
            body = {"language": "en_US", "password": password, "remember": "true", "type": "auth", "username": username}
            r = self.session.put(url=URLS.AUTH_URL, json=body)
            data = r.json()

            if data["type"] == "response":
                pass

            elif "auth_failure" in r.text:
                raise EzAuthExp.AuthenticationError("auth_failure, user not exist")

            elif 'rate_limited' in r.text:
                raise EzAuthExp.RatelimitError("auth_failure, rate_limited")

            # 2fa auth
            elif 'multifactor' in r.text:
                self.is2fa = True  # is 2fa user
                self.__mfa_start__ = time.time()
                return {"status": False, "auth": self, "2fa_status": self.is2fa}
            else:
                raise EzAuthExp.UnkownError(r.text)

        # get access_token from response
        if "access_token" in r.text:
            token = self.__set_access_token(data)
            # auth/reauth success
            self.__set_info(tokens=token)
        else:
            raise EzAuthExp.UnkownError(r.text)

        return {"status": True, "auth": self, "2fa_status": self.is2fa}

    async def email_verfiy(self, vcode: str) -> dict:
        """email_verfiy after trying authorize
        Return {"status":True,"auth":self,"2fa":self.is2fa}
        """
        # no need to 2fa
        if self.__mfa_start__ == 0:
            return {"status": True, "auth": self, "2fa": self.is2fa}
        # check time
        if (time.time() - self.__mfa_start__) <= TFA_TIME_LIMIT:
            authdata = {
                'type': 'multifactor',
                'code': vcode,
            }
            r = self.session.put(url=URLS.AUTH_URL, json=authdata)
            data = r.json()

            if data["type"] == "response":
                pass
            elif "auth_failure" in r.text:
                raise EzAuthExp.MultifactorError("2fa auth_failue")
            elif "multifactor_attempt_failed" in r.text:  # verify code err
                raise EzAuthExp.MultifactorError("2fa auth_failue, multifactor_attempt_failed")
            else:
                raise EzAuthExp.MultifactorError("2fa auth_failue, unkown err")
        else:  # 2fa wait overtime
            raise EzAuthExp.WaitOvertimeError("2fa wait overtime, wait failed")

        # get access_token from response
        if "access_token" in r.text:
            token = self.__set_access_token(data)
            # auth/reauth success
            self.__set_info(tokens=token)
        else:
            raise EzAuthExp.UnkownError(r.text)

        self.__mfa_start__ = 0
        return {"status": True, "auth": self, "2fa": self.is2fa}

    async def reauthorize(self) -> bool:
        """reauthorize using cookie
        """
        try:
            await self.authorize("", "")
            return True
        except Exception as result:
            print(f"[EzAuth] reauthoreize err!\n{result}")
            return False

    def get_entitlement_token(self):
        r = self.session.post(URLS.ENTITLEMENT_URL, json={})
        entitlement = r.json()['entitlements_token']
        return entitlement

    def get_emailverifed(self):
        """ get if account has emailverifed (not MFA)"""
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
        return {'sub': Sub, 'name': Name, 'tag': Tag, 'create_data': Createdat, 'typeban': typeban}

    def get_region(self, headers) -> str:
        """headers {'Content-Type': 'application/json', 'Authorization': f'{self.token_type} {self.access_token}'}
        """
        json = {"id_token": self.id_token}
        r = self.session.headers.update(headers)
        r = self.session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', json=json)
        data = r.json()
        Region = data['affinities']['live']
        return Region

    def print(self) -> None:
        print("=" * 50)
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
        print("=" * 50)

    def get_riotuser_token(self) -> RiotUserToken:
        """Return:
        - RiotUserToken(user_id=self.user_id,
                            access_token=self.access_token,
                            entitlements=self.entitlements_token,
                            region=self.Region)
        - if is_init==False, raise init not finished err
        """
        if self.__is_init__:
            ret = RiotUserToken(user_id=self.user_id,
                                access_token=self.access_token,
                                entitlements=self.entitlements_token,
                                region=self.Region)    
            return ret
        else:
            raise EzAuthExp.InitError("EzAuth Obj not initialized")

    def save_cookies(self, path: str) -> None:
        """dump cookies_dict to path (w+)
        """
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies) # type: ignore
        with open(path, "w+") as f:
            f.write(json.dumps(cookies))

    def load_cookies(self, path: str) -> None:
        """load cookies_dic from path (rb)
        """
        with open(path, "r") as f:
            load_cookies = json.loads(f.read())

        self.session.cookies = requests.utils.cookiejar_from_dict(load_cookies) # type: ignore