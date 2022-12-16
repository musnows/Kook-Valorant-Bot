import aiohttp
import json
import copy
import requests


# 所有皮肤
with open("../code/log/ValSkin.json", 'r', encoding='utf-8') as frpr:
    ValSkinList = json.load(frpr)
# 所有商品价格
with open("../code/log/ValPrice.json", 'r', encoding='utf-8') as frpr:
    ValPriceList = json.load(frpr)
# 所有皮肤等级
with open("../code/log/ValIters.json", 'r', encoding='utf-8') as frpr:
    ValItersList = json.load(frpr)


#从list中获取价格
def fetch_item_price_bylist(item_id):
    for item in ValPriceList['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item
#从list中获取皮肤
def fetch_skin_bylist(item_id):
    res = {}  #下面我们要操作的是获取通行证的皮肤，但是因为遍历的时候已经跳过data了，返回的时候就不好返回
    for item in ValSkinList['data']:  #遍历查找指定uuid
        if item_id == item['levels'][0]['uuid']:
            res['data'] = item  #所以要手动创建一个带data的dict作为返回值
            return res
#从list中获取等级
def fetch_item_iters_bylist(iter_id):
    for iter in ValItersList['data']:  #遍历查找指定uuid
        if iter_id == iter['uuid']:
            res = {'data': iter}  #所以要手动创建一个带data的dict作为返回值
            return res
#从list中通过皮肤lv0uuid获取皮肤等级
def fetch_skin_iters_bylist(item_id):
    for it in ValSkinList['data']:
        if it['levels'][0]['uuid'] == item_id:
            res_iters = fetch_item_iters_bylist(it['contentTierUuid'])
            return res_iters



# 获取vp和r点
async def fetch_valorant_point(u):
    url = "https://pd.ap.a.pvp.net/store/v1/wallet/" + u['auth_user_id']
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token']
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())
    return res

# 获取每日商店
async def fetch_daily_shop(u):
    url = "https://pd.ap.a.pvp.net/store/v2/storefront/" + u['auth_user_id']
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": u['entitlements_token'],
        "Authorization": "Bearer " + u['access_token']
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            res = json.loads(await response.text())
    return res

#获取用户游戏id
async def fetch_user_gameID(auth):
    url = "https://pd.ap.a.pvp.net/name-service/v2/players"
    payload = json.dumps([auth['auth_user_id']])
    headers = {
        "Content-Type": "application/json",
        "X-Riot-Entitlements-JWT": auth['entitlements_token'],
        "Authorization": "Bearer " + auth['access_token']
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, data=payload) as response:
            res = json.loads(await response.text())
    return res

# 开机获取所有需要获取的变量
def fetch_data():
    print("[start] fetch_data start")
    global ValItersList,ValPriceList,ValSkinList
    #获取所有皮肤
    url = "https://valorant-api.com/v1/weapons/skins"
    headers = {'Connection': 'close'}
    params = {"language": "zh-TW"}
    res = requests.get(url,headers=headers,params=params)
    ValSkinList = copy.deepcopy(res.json())
    with open("./log/ValSkin.json", 'w', encoding='utf-8') as fw1:
        json.dump(ValSkinList, fw1, indent=2, sort_keys=True, ensure_ascii=False)
    #print(ValSkinList)
    #获取皮肤等级
    url = f"https://valorant-api.com/v1/contenttiers/"
    res = requests.get(url,headers=headers,params=params)
    ValItersList = copy.deepcopy(res.json())
    #print(ValItersList)
    with open("./log/ValIters.json", 'w', encoding='utf-8') as fw1:
        json.dump(ValItersList, fw1, indent=2, sort_keys=True, ensure_ascii=False)
    print("[start] fetch_data end")