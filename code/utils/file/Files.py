from time import time
from .FileManage import FileManage
from ..log.Logging import _log

# 配置相关
config = FileManage("./config/config.json", True) 
"""机器人配置文件"""
BotUserDict = FileManage("./log/BotUserLog.json")
"""机器人用户信息记录"""
ApiTokenDict = FileManage("./log/ApiToken.json")
"""API token"""
ColorIdDict = FileManage("./log/color_idsave.json") 
"""自动上色的信息保存"""
EmojiDict = FileManage("./config/color_emoji.json", True)  
"""自动上色 服务器角色配置"""
SponsorDict = FileManage("./log/sponsor_roles.json")  
"""感谢助力者 信息保存"""
AfdWebhook = FileManage("./log/AfdWebhook.json")
"""爱发电的wh请求"""

# valorant资源相关
ValErrDict = FileManage("./log/ValErrCode.json") 
"""valorant错误码解决办法"""
ValSkinList = FileManage("./log/ValSkin.json")
"""valorant皮肤"""
ValPriceList = FileManage("./log/ValPrice.json")
"""valorant皮肤价格"""
ValBundleList = FileManage("./log/ValBundle.json")
"""valorant皮肤捆绑包"""
ValItersList = FileManage("./log/ValIters.json")
"""valorant皮肤等级"""

# valorant功能相关
GameIdDict = FileManage("./log/game_idsave.json") 
"""玩家游戏id保存"""
SkinRateDict = FileManage("./log/ValSkinRate.json")
"""valorant皮肤评分信息"""
SkinNotifyDict = FileManage("./log/UserSkinNotify.json")
"""皮肤提醒 用户记录"""
UserAuthID = FileManage("./log/UserAuthID.json")
"""用户游戏id/uuid，账户密码重登记录"""
UserRiotName = UserAuthID['data']
"""riot用户游戏id和uuid"""
UserPwdReauth = UserAuthID['ap_log']
"""riot账户密码重登记录"""
ApiAuthLog = UserAuthID['api_log']
"""api 缓存用户的account记录"""

# vip相关
VipUuidDict = FileManage("./log/VipUuid.json")
"""vip uuid文件"""
VipShopBgDict = FileManage("./log/VipUserShopBg.json")
"""vip 背景图设置；商店图缓存"""
VipUser = FileManage("./log/VipUser.json")
"""vip 用户列表/抽奖记录"""
VipUserDict = VipUser['data']
"""vip 用户列表"""
VipRollDcit = VipUser['roll']
"""vip 抽奖记录"""

# 缓存相关
LoginForbidden = False
"""出现403错误，禁止重登"""
NightMarket = False
"""夜市是否开启？False没开，True开"""
UserAuthCache = {'api':{},'kook':{},'data':{},'acpw':{},'tfa':{}}  
"""api/bot 公用EzAuth对象缓存:
- api  | 用户账户:riot_user_uuid
- kook | kook_user_id:[uuid1,uuid2]  值为list,支持多账户登录
- data | riot_user_uuid:{"auth": EzAuth Obj, "2fa": EzAuth.is2fa}
- acpw | riot_user_uuid:{'a':账户,'p':密码}  用于bot中的账户密码存储。只存储在全局变量中，不写入磁盘
- tfa  | 用户id:EzAuth对象  临时使用的缓存
"""
ApiAuthCache = {'data':{}}       
"""api EzAuth对象缓存"""
login_rate_limit = {'limit': False, 'time': time()}
"""全局的速率限制，如果触发了速率限制的err，则阻止所有用户login
- {'limit': False, 'time': time()}
"""
UserShopCache = { 'clear_time':time(),'data':{}}
"""用来存放用户每天的商店（早八会清空）
- { 'clear_time':time(),'data':{}}
"""
UserRtsDict = {}
"""用户皮肤评分rate选择列表"""
UserStsDict = {}
"""用户商店皮肤提醒notify功能选择列表"""
ValItersEmoji = EmojiDict['val_iters_emoji']
"""valorant皮肤等级对应的kook自定义表情"""

# 实例化一个khl的bot，方便其他模组调用
from khl import Bot
bot = Bot(token=config['token']['bot'])
"""main bot"""
_log.info(f"Loading all files") # 走到这里代表所有文件都打开了