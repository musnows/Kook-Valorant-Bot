import traceback
import io
from khl import Message, Bot
from PIL import Image
from ..utils.ShopImg import img_requestor
from ..utils.file.Files import ValBundleList,UserAuthCache, ValSkinList, ValPriceList
from ..utils.valorant.api import Assets
from ..utils.log.Logging import _log
from ..utils.log import BotLog


async def update_skins(msg: Message) -> bool:
    """更新本地保存的皮肤"""
    try:
        global ValSkinList
        skins = await Assets.fetch_skins()
        ValSkinList.value = skins
        # 写入文件
        ValSkinList.save()
        _log.info(f"update_skins finished!")
        return True
    except Exception as result:
        _log.exception("Exception occur")
        await msg.reply(f"ERR! update_skins\n```\n{traceback.format_exc()}\n```")
        return False


async def update_bundle_url(msg: Message, bot_upimg: Bot) -> bool:
    """更新捆绑包，并将捆绑包的图片上传到kook"""
    try:
        global ValBundleList
        resp = await Assets.fetch_bundles_all()  #从官方获取最新list
        if len(resp['data']) == len(ValBundleList):  #长度相同代表没有更新
            _log.info(f"len is the same, not need update")
            await msg.reply("BundleList_len相同，无需更新")
            return True

        for b in resp['data']:
            flag = 0
            for local_B in ValBundleList:  #不在
                if b['uuid'] == local_B['uuid']:  #相同代表存在无需更新
                    flag = 1  #找到了，无需更新
                    break

            if flag != 1:  #不存在,创建图片准备上传 (原有捆绑包图片如果每次都上传，会让bot很卡)
                bg_bundle_icon = Image.open(io.BytesIO(await img_requestor(b['displayIcon'])))
                imgByteArr = io.BytesIO()
                bg_bundle_icon.save(imgByteArr, format='PNG')
                imgByte = imgByteArr.getvalue()
                _log.info(f"Uploading | {b['displayName']}")
                bundle_img_src = await bot_upimg.client.create_asset(imgByte)
                _log.info(f"{b['displayName']} | url: {bundle_img_src}")
                b['displayIcon2'] = bundle_img_src  #修改url
                ValBundleList.append(b)  #插入

        ValBundleList.save()
        _log.info(f"update_bundle_url finished!")
        return True
    except Exception as result:
        _log.exception("Exception occur")
        await msg.reply(f"ERR! update_bundle_url\n```\n{traceback.format_exc()}\n```")
        return False


async def update_price(msg: Message, riot_user_token) -> bool:
    """更新本地存储的物品价格
    - 获取物品价格的操作需要authtoken，自动更新容易遇到token失效的情况，所以需要手动更新
    - riot_user_token: EzAuth.RiotUserToken
    """
    try:
        global ValPriceList
        # 调用api获取价格列表
        prices = await Assets.fetch_item_price_all(riot_user_token)
        test = prices["Offers"] # 暴力判断是否有这个键值，没有则keyerr
        ValPriceList.value = prices  # 所有价格的列表
        # 写入文件
        ValPriceList.save()
        _log.info(f"update_item_price finished!")
        return True
    except Exception as result:
        _log.exception("Exception occur")
        await msg.reply(f"ERR! update_price\n```\n{traceback.format_exc()}\n```")
        return False
    

async def update_agents(msg:Message,riot_user_token) -> bool:
    """更新本地保存的英雄(用于战绩查询)"""



################################################################################################

def init(bot:Bot,bot_upimg:Bot,master_id:str):
    """master_id: bot master user_id"""
    async def update(msg:Message,bot_upimg:Bot):
        """更新valorant相关资源
        """
        if await update_skins(msg):
            await msg.reply(f"成功更新：商店皮肤")
        if await update_bundle_url(msg, bot_upimg):
            await msg.reply(f"成功更新：捆绑包")
        # 获取物品价格需要登录
        riot_user_id = UserAuthCache['kook'][msg.author_id][0]
        auth = UserAuthCache['data'][riot_user_id]['auth']
        riotUser = auth.get_riotuser_token()
        if await update_price(msg, riotUser):
            await msg.reply(f"成功更新：物品价格")

    # 手动更新商店物品和价格
    @bot.command(name='update_spb', aliases=['upd'])
    async def update_skin_price_bundle(msg: Message):
        BotLog.logMsg(msg)
        try:
            if msg.author_id == master_id:
                await update(msg,bot_upimg)
        except Exception as result:
            await BotLog.BaseException_Handler("update_spb",traceback.format_exc(),msg)

    _log.info("[plugins] load ValFileUpd.py")