from ...file.Files import  ValItersList, ValPriceList, ValSkinList, _log

SKIN_ICON_ERR = "https://img.kookapp.cn/assets/2023-02/ekwdy7PiQC0e803m.png"
"""用于替换错误的皮肤图片"""

# 用lc代表本地获取
def lc_fetch_item_price(item_id:str) -> dict:
    """从本地list中获取价格,字段如下
    - ['Cost']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'] 
    """
    for item in ValPriceList['Offers']:  #遍历查找指定uuid
        if item_id == item['OfferID']:
            return item
    return {}


def lc_fetch_item_iters(iter_id:str) -> dict:
    """从list中获取物品的等级"""
    res = {}
    for iter in ValItersList['data']:  #遍历查找指定uuid
        if iter_id == iter['uuid']:
            res = {'data': iter}  #所以要手动创建一个带data的dict作为返回值
    return res

def lc_fetch_skin(item_id:str) -> dict:
    """从list中获取皮肤"""
    res = {}  #下面我们要操作的是获取通行证的皮肤，但是因为遍历的时候已经跳过data了，返回的时候就不好返回
    for item in ValSkinList['data']:  #遍历查找指定uuid
        if item_id == item['levels'][0]['uuid']:
            res['data'] = item  #所以要手动创建一个带data的dict作为返回值
            # 可能出现图标为空的情况（异星霸主 斗牛犬）
            while (res['data']['displayIcon'] == None):
                for level in item['levels']:  # 在等级里面找皮肤图标
                    if level["displayIcon"] != None:
                        res['data']['displayIcon'] = level["displayIcon"]
                        break  # 找到了，退出循环
                # 没找到，替换成err图片
                res['data']['displayIcon'] = SKIN_ICON_ERR

    return res


def lc_fetch_skin_by_name(name:str) -> list[dict]:
    """从list中，通过皮肤名字获取皮肤列表"""
    wplist = list()  #包含该名字的皮肤list
    for skin in ValSkinList['data']:
        if name in skin['displayName']:
            data = {'displayName': skin['displayName'], 'lv_uuid': skin['levels'][0]['uuid']}
            wplist.append(data)
    return wplist

def lc_fetch_skin_iters(item_id) -> dict:
    """从list中通过皮肤lv0uuid获取皮肤等级"""
    res_iters = {}
    for it in ValSkinList['data']:
        if it['levels'][0]['uuid'] == item_id:
            res_iters = lc_fetch_item_iters(it['contentTierUuid'])
    return res_iters

async def lc_fetch_bundle_weapen_by_name(name:str) -> list[dict]:
    """在本地用`名字`查询捆绑包包含什么枪"""
    # 捆绑包的所有皮肤
    WeapenList = list()
    for skin in ValSkinList['data']:
        if name in skin['displayName']:
            # 为了方便查询价格，在这里直接把skin的lv0-uuid也给插入进去
            data = {'displayName': skin['displayName'], 'lv_uuid': skin['levels'][0]['uuid']}
            WeapenList.append(data)

    return WeapenList