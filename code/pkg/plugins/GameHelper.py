#保存用户的游戏ID操作
import traceback
from khl import Message,Bot
from ..utils.file.Files import GameIdDict,ValErrDict,_log
from ..utils.log import BotLog

async def saveid_main(msg: Message, game_id: str) -> None:
    """保存用户游戏id"""
    global GameIdDict
    # 如果用户id已有，则进行修改
    if msg.author_id in GameIdDict.keys():
        GameIdDict[msg.author_id] = game_id
        await msg.reply(f'本狸已经修改好你的游戏id啦!')
    # 没有该用户信息，进行追加操作
    else:
        GameIdDict[msg.author_id] = game_id
        await msg.reply(f"本狸已经记下你的游戏id喽~")


async def saveid_count(msg: Message) -> None:
    """显示已有id的个数"""
    countD = len(GameIdDict)
    await msg.reply(f"目前狸狸已经记下了`{countD}`个小伙伴的id喽~")


async def myid_main(msg: Message) -> None:
    """实现读取用户游戏ID并返回"""
    if msg.author_id in GameIdDict.keys():
        await msg.reply(f'游戏id: ' + GameIdDict[msg.author_id])
    else:
        countD = len(GameIdDict)
        await msg.reply(f"狸狸不知道你的游戏id呢，用`/saveid`告诉我吧！\n```\n/saveid 你的游戏id```\n目前狸狸已经记下了`{countD}`个小伙伴的id喽！")


async def val_errcode(msg: Message, num: str = "-1") -> None:
    """查询游戏错误码"""
    if num == "-1":
        await msg.reply(
            '目前支持查询的错误信息有：\n```\n0-1,4-5,7-21,29,31,33,38,43-46,49-70,81,84,128,152,1067,9001,9002,9003\n```\n注：van和val错误码都可用本命令查询'
        )
    elif num in ValErrDict:
        await msg.reply(ValErrDict[num])
    else:
        await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[当然!](https://f.wps.cn/w/awM5Ej4g/)')


async def dx123(msg: Message) -> None:
    """关于dx报错的解决方法"""
    await msg.reply(
        '报错弹窗内容为`The following component(s) are required to run this program:DirectX Runtime`\n需要下载微软官方驱动安装，官网搜索[DirectX End-User Runtime Web Installer]\n你还可以下载本狸亲测可用的DX驱动 [链接](https://pan.baidu.com/s/1145Ll8vGtByMW6OKk6Zi2Q)，暗号是1067哦！\n狸狸记得之前玩其他游戏的时候，也有遇到过这个问题呢~'
    )


##################################################################################



def init(bot:Bot):
    # 存储用户游戏id
    @bot.command(name="saveid", case_sensitive=False)
    async def saveid(msg: Message, *args):
        BotLog.logMsg(msg)
        if args == ():
            await msg.reply(f"您没有提供您的游戏id：`{args}`")
            return
        try:
            game_id = " ".join(args)  #避免用户需要输入双引号
            await saveid_main(msg, game_id)
        except Exception as result:
            await BotLog.BaseException_Handler("saveid", traceback.format_exc(), msg)


    # 已保存id总数
    @bot.command(name='saveid-a',case_sensitive=False)
    async def saveid_all(msg: Message):
        BotLog.logMsg(msg)
        try:
            await saveid_count(msg)
        except Exception as result:
            await BotLog.BaseException_Handler("saveid-a", traceback.format_exc(), msg)


    # 实现读取用户游戏ID并返回
    @bot.command(name="myid", case_sensitive=False) 
    async def myid(msg: Message, *args):
        BotLog.logMsg(msg)
        try:
            await myid_main(msg)
        except Exception as result:
            await BotLog.BaseException_Handler("myid", traceback.format_exc(), msg)


    # 查询游戏错误码
    @bot.command(name='val', aliases=['van', 'VAN', 'VAL'],case_sensitive=False)
    async def val_err(msg: Message, numS: str = "-1", *arg):
        BotLog.logMsg(msg)
        try:
            await val_errcode(msg, numS)
        except Exception as result:
            await BotLog.BaseException_Handler("val", traceback.format_exc(), msg,help=f"您输入的错误码格式不正确！\n请提供正确范围的`数字`,而非`{numS}`")


    #关于dx报错的解决方法
    @bot.command(name='DX', case_sensitive=False)
    async def dx(msg: Message):
        BotLog.logMsg(msg)
        await dx123(msg)


    _log.info("[plugins] load GameHelper")