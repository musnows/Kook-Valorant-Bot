import json
import aiofiles
import traceback

def open_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    return tmp

async def write_file_aio(path:str, value):
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(value, indent=2, sort_keys=True,ensure_ascii=False))

def write_file(path:str, value):
    with open(path, 'w', encoding='utf-8') as fw2:
        json.dump(value, fw2, indent=2, sort_keys=True, ensure_ascii=False)

class FileManage:
    # 初始化构造
    def __init__(self,path:str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            tmp = json.load(f)
        self.value = tmp
        self.type = type(tmp)
        self.path = path
    # 操作符重载
    def __getitem__(self,index):
        return self.value[index]
    # 打印重载
    def __str__(self) -> str:
        return str(self.value)
    # 获取成员
    def get_instance(self):
        return self.value
    # 保存
    def save(self):
        with open(self.path, 'w', encoding='utf-8') as fw:
            json.dump(self.value, fw, indent=2, sort_keys=True, ensure_ascii=False)
    # 异步保存
    async def save_aio(self):
        async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
            await f.write(json.dump(self.value,indent=2, sort_keys=True, ensure_ascii=False))

###################################################################################################

config = FileManage("./config/config.json")            # 机器人配置文件
BotUserDict = FileManage("./log/BotUserLog.json")      # 机器人用户信息
ApiTokenDict = FileManage("./log/ApiToken.json")       # API token
ColorIdDict = FileManage("./log/color_idsave.json")    # 自动上色 信息保存
EmojiDict = FileManage("./config/color_emoji.json")    # 自动上色 服务器角色配置
SponsorDict = FileManage("./log/sponsor_roles.json")   # 感谢助力者 信息保存

ValErrDict = FileManage("./log/ValErrCode.json")       # valorant错误码解决办法
ValSkinList = FileManage("./log/ValSkin.json")         # valorant皮肤
ValPriceList = FileManage("./log/ValPrice.json")       # valorant皮肤价格
ValBundleList = FileManage("./log/ValBundle.json")     # valorant捆绑包
ValItersList = FileManage("./log/ValIters.json")       # valorant皮肤等级

SkinRateDict = FileManage("./log/ValSkinRate.json")     # valorant皮肤评分信息
SkinNotifyDict = FileManage("./log/UserSkinNotify.json")# 皮肤提醒 用户记录
GameIdDict = FileManage("./log/game_idsave.json")       # 玩家游戏id保存
UserTokenDict = FileManage("./log/UserAuthID.json")     # riot用户游戏id和uuid

VipUuidDict = FileManage("./log/VipUuid.json")         # vip uuid文件
VipUserDict = FileManage("./log/VipUser.json")         # vip 用户列表
VipShopBgDict = FileManage("./log/VipUserShopBg.json") # vip 背景图设置；商店图缓存
RollVipDcit = FileManage("./log/VipRoll.json")         # vip 抽奖信息


FileList = [config,BotUserDict,ApiTokenDict,ColorIdDict,EmojiDict,SponsorDict,
            ValErrDict,ValSkinList,ValPriceList,ValBundleList,ValItersList,
            SkinRateDict,SkinNotifyDict,GameIdDict,UserTokenDict,
            VipUuidDict,VipUserDict,VipShopBgDict,RollVipDcit]
# 保存所有文件
async def Save_All_File():
    for i in FileList:
        try:
            await i.save_aio()
        except:
            print(f"ERR! [Save.All.File] {i.path}\n{traceback.format_exc()}")