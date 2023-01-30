import json
import aiofiles
import traceback
from endpoints.Gtime import GetTime

FileList = []


def open_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    return tmp


async def write_file_aio(path: str, value):
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def write_file(path: str, value):
    with open(path, 'w', encoding='utf-8') as fw2:
        json.dump(value, fw2, indent=2, sort_keys=True, ensure_ascii=False)


# 保存所有文件
async def Save_All_File(is_Aio=True):
    for i in FileList:
        try:
            if is_Aio:
                await i.save_aio()
            else:
                i.save()
        except:
            print(f"ERR! [{GetTime()}] [Save.All.File] {i.path}\n{traceback.format_exc()}")

    print(f"[Save.All.File] save finished at [{GetTime()}]")


# 文件管理类
class FileManage:
    # 初始化构造
    def __init__(self, path: str, read_only: bool = False) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            tmp = json.load(f)
        self.value = tmp  # 值
        self.type = type(tmp)  # 值的类型
        self.path = path  # 值的文件路径
        self.Ronly = read_only  # 是否只读
        #将自己存全局变量里面
        if not read_only:
            global FileList  # 如果不是只读，那就存list里面
            FileList.append(self)

    # []操作符重载
    def __getitem__(self, index):
        return self.value[index]

    # 打印重载
    def __str__(self) -> str:
        return str(self.value)

    # 删除成员
    def __delitem__(self, index):
        del self.value[index]

    # 长度
    def __len__(self):
        return len(self.value)

    # 索引赋值 x[i] = 1
    def __setitem__(self, index, value):
        self.value[index] = value

    # 迭代
    def __iter__(self):
        return self.value.__iter__()

    def __next__(self):
        return self.value.__next__()

    # 比较==
    def __eq__(self, i):
        if isinstance(i, FileManage):
            return self.value.__eq__(i.value)
        else:
            return self.value.__eq__(i)

    # 比较!=
    def __ne__(self, i):
        if isinstance(i, FileManage):
            return self.value.__ne__(i.value)
        else:
            return self.value.__ne__(i)

    # 获取成员
    def get_instance(self):
        return self.value

    # 遍历dict
    def items(self):
        return self.value.items()

    # 追加
    def append(self, i):
        self.value.append(i)

    # list的删除
    def remove(self, i):
        self.value.remove(i)

    def keys(self):
        return self.value.keys()

    # 保存
    def save(self):
        with open(self.path, 'w', encoding='utf-8') as fw:
            json.dump(self.value, fw, indent=2, sort_keys=True, ensure_ascii=False)

    # 异步保存
    async def save_aio(self):
        async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:  #这里必须用dumps
            await f.write(json.dumps(self.value, indent=2, sort_keys=True, ensure_ascii=False))


###################################################################################################

config = FileManage("./config/config.json", True)  # 机器人配置文件
BotUserDict = FileManage("./log/BotUserLog.json")  # 机器人用户信息
ApiTokenDict = FileManage("./log/ApiToken.json")  # API token
ColorIdDict = FileManage("./log/color_idsave.json")  # 自动上色 信息保存
EmojiDict = FileManage("./config/color_emoji.json", True)  # 自动上色 服务器角色配置
SponsorDict = FileManage("./log/sponsor_roles.json")  # 感谢助力者 信息保存

ValErrDict = FileManage("./log/ValErrCode.json")  # valorant错误码解决办法
ValSkinList = FileManage("./log/ValSkin.json")  # valorant皮肤
ValPriceList = FileManage("./log/ValPrice.json")  # valorant皮肤价格
ValBundleList = FileManage("./log/ValBundle.json")  # valorant捆绑包
ValItersList = FileManage("./log/ValIters.json")  # valorant皮肤等级

SkinRateDict = FileManage("./log/ValSkinRate.json")  # valorant皮肤评分信息
SkinNotifyDict = FileManage("./log/UserSkinNotify.json")  # 皮肤提醒 用户记录
GameIdDict = FileManage("./log/game_idsave.json")  # 玩家游戏id保存
UserAuthID = FileManage("./log/UserAuthID.json")  # 用户游戏id/uuid，账户密码重登记录
UserTokenDict = UserAuthID['data']  # riot用户游戏id和uuid
UserApLog = UserAuthID['ap_log']    # 账户密码重登记录

VipUuidDict = FileManage("./log/VipUuid.json")  # vip uuid文件
VipShopBgDict = FileManage("./log/VipUserShopBg.json")  # vip 背景图设置；商店图缓存
VipUser = FileManage("./log/VipUser.json")  # vip 用户列表
VipUserDict = VipUser['data'] # vip 用户
VipRollDcit = VipUser['roll'] # vip 抽奖信息 

AfdWebhook = FileManage("./log/AfdWebhook.json")  # 爱发电的wh请求
