from time import time
from .FileManage import FileManage,Boolean
from ..log.Logging import _log
from ..Gtime import get_time

StartTime = get_time()
"""机器人启动时间 str"""

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
ValMissionDict = FileManage("./log/ValMission.json")
"""valorant任务id和名字对照表（收集自用户）"""
ValAgentDict = FileManage("./log/ValAgent.json")
"""valorant英雄相关信息"""

# valorant功能相关
GameIdDict = FileManage("./log/game_idsave.json") 
"""玩家游戏id保存"""
SkinRateDict = FileManage("./log/ValSkinRate.json")
"""valorant皮肤评分信息"""
SkinNotifyDict = FileManage("./log/UserSkinNotify.json")
"""皮肤提醒 用户记录"""
UserAuthID = FileManage("./log/UserAuthID.json")
"""用户游戏id/uuid，账户密码重登记录，api/vip登录用户记录"""
UserPwdReauth = UserAuthID['ap_log']
"""riot账户密码重登记录。如果机器人有使用过账户密码进行重登，会在这里记录"""
ApiAuthLog:dict = UserAuthID['api_auth_log']
"""api 缓存用户的riot_user_uuid记录。格式 `account:uuid`"""
VipAuthLog:dict = UserAuthID["vip_auth_log"]
"""vip 已登录用户的记录。格式 `vip_userid:[uuid1,uuid2]`"""

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
UserAuthCache = {'api':{},'kook':{},'data':{},'acpw':{},'tfa':{}}  
"""api/bot 公用EzAuth对象缓存:
- api  | `用户账户:riot_user_uuid`
- kook | `kook_user_id:[uuid1,uuid2]`  值为list,支持多账户登录
- data | `riot_user_uuid:{"auth": EzAuth Obj, "2fa": EzAuth.is2fa}`
- acpw | `riot_user_uuid:{'a':账户,'p':密码}`  用于bot中的账户密码存储。只存储在全局变量中，不写入磁盘
- tfa  | `用户id:EzAuth Obj`  临时使用的缓存
"""
LoginRateLimit = {'limit': False, 'time': time()}
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
"""valorant皮肤等级对应的kook自定义表情。

对应配置文件`./config/color_emoji.json`中的 `val_iters_emoji` 键值
"""

# 实例化一个khl的bot，方便其他模组调用
from khl import Bot,Cert
bot = Bot(token=config['token']['bot']['token'])  # websocket
"""main bot"""
if not config['token']['bot']['ws']: # webhook
    _log.info(f"[BOT] using webhook at port {config['token']['bot']['webhook_port']}")
    bot = Bot(cert=Cert(token=config['token']['bot']['token'],
                        verify_token=config['token']['bot']['verify_token'],
                        encrypt_key=config['token']['bot']['encrypt']),
              port=config['token']['bot']['webhook_port'])
# 上传图片测试的机器人
bot_upd_img = Bot(token=config['token']['img_upload_token'])
"""用来上传图片的bot"""
_log.info(f"Loading all files") # 走到这里代表所有文件都打开了