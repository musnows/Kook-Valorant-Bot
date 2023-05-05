import json
import aiohttp
import traceback
import urllib.request
import urllib.parse
from khl import Bot, Message
from khl.card import Card, CardMessage, Element, Module, Types

# 读取彩云的key
from ..utils.file.Files import config,_log
from ..utils.log import BotLog
from ..Admin import is_admin

CyKey = config['caiyun']
"""彩云小译 key"""


def youdao_translate(txt: str):
    """youdao code from https://github.com/Chinese-boy/Many-Translaters"""
    _log.debug(txt)
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&sessionFrom=https://www.baidu.com/link'
    data = {
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': '1500092479607',
        'sign': 'c98235a85b213d482b8e65f6b1065e26',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_CL1CKBUTTON',
        'typoResult': 'true',
        'i': txt
    }

    data = urllib.parse.urlencode(data).encode('utf-8')
    wy = urllib.request.urlopen(url, data)
    html = wy.read().decode('utf-8')
    ta = json.loads(html)
    _log.debug(ta['translateResult'][0][0]['tgt'])
    return ta['translateResult'][0][0]['tgt']

async def caiyun_translate(source, direction):
    """caiyun translte
    - source: word text
    - direction: see caiyun-api docs
    """
    url = "http://api.interpreter.caiyunai.com/v1/translator"
    # WARNING, this token is a test token for new developers,
    # and it should be replaced by your token
    token = CyKey
    payload = {
        "source": source,
        "trans_type": direction,
        "request_id": "demo",
        "detect": True,
    }
    headers = {
        "content-type": "application/json",
        "x-authorization": "token " + token,
    }

    #用aiohttp效率更高
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=headers) as response:
            return json.loads(await response.text())["target"]


# 由于彩云不支持输入中文自动翻译成英文（目前只支持其他语种自动转中文）
# 所以需要判断来源是否是中文，如果是中文自动翻译成English
def is_chinese(word:str):
    """判断str是否为中文"""
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def delete_by_start_end(word:str, start:str, end:str):
    """给出start和end字符串，删除中间内容
    - 用于单独处理met和rol消息，不翻译这部分内容
    """
    # 找出两个字符串在原始字符串中的位置
    # 开始位置是：开始始字符串的最左边第一个位置；
    # 结束位置是：结束字符串的最右边的第一个位置
    while word.find(start) != -1:
        x1 = word.find(start)
        # index()函数算出来的是字符串的最左边的第一个位置，所以需要加上长度找到末尾
        x2 = word.find(end, x1 + len(start)) + len(end) 
        # 找出两个字符串之间的内容
        x3 = word[x1:x2]
        # 将内容替换为空字符串s
        word = word.replace(x3, "")

    _log.info(f'Handel {start} | {word}')
    return word


# 调用翻译,有道和彩云两种引擎（有道寄了就用彩云）
async def translate_main(msg: Message, *arg):
    word = " ".join(arg)
    ret = word
    if '(met)' in word:
        ret = delete_by_start_end(word, '(met)', '(met)')
    elif '(rol)' in word:
        ret = delete_by_start_end(word, '(rol)', '(rol)')
    # 重新赋值
    word = ret
    try:
        text = "**翻译结果(Result):**\n"
        cm = CardMessage()
        try:
            c1 = Card(Module.Section(Element.Text(f"{text}{youdao_translate(word)}", Types.Text.KMD)),
                    Module.Context('来自: 有道翻译'))
            cm.append(c1)
            await msg.reply(cm)
        except Exception as result:
            # 如果为空，rasie到外层except
            if CyKey=="":raise result
            # 彩云的key不为空，才调用它
            if is_chinese(word):
                c1 = Card(
                    Module.Section(
                        Element.Text(f"{text}{await caiyun_translate(word,'auto2en')}", Types.Text.KMD)),
                    Module.Context('来自: 彩云小译，中译英'))
            else:
                c1 = Card(
                    Module.Section(
                        Element.Text(f"{text}{await caiyun_translate(word,'auto2zh')}", Types.Text.KMD)),
                    Module.Context('来自: 彩云小译，英译中'))

            cm.append(c1)
            await msg.reply(cm)
    except:
        _log.exception(f"translate error")
        await msg.reply(f"翻译出错了！\n```\n{traceback.format_exc()}\n```")


# 实时翻译栏位
ListTL = ['0', '0', '0', '0', '0', '0']


# 查看目前已经占用的容量
def tl_check():
    sum = 0
    for i in ListTL:
        if i != '0':
            sum += 1
    return sum


async def tl_shutdown(bot: Bot, msg: Message):
    global ListTL
    if tl_check() == 0:
        await msg.reply(f"实时翻译栏位为空: {tl_check()}/{len(ListTL)}")
        return
    i = 0
    while i < len(ListTL):
        if (ListTL[i]) != '0':  #不能对0的频道进行操作
            channel = await bot.client.fetch_public_channel(ListTL[i])
            await bot.client.send(channel, "不好意思，阿狸的主人已经清空了实时翻译的栏位！")
            ListTL[i] = '0'
        i += 1
    await msg.reply(f"实时翻译栏位已清空！目前为: {tl_check()}/{len(ListTL)}")


# 开启频道实时翻译
async def tl_open(msg: Message):
    global ListTL
    if tl_check() == len(ListTL):
        await msg.reply(f"目前栏位: {tl_check()}/{len(ListTL)}，已满！")
        return
    #发现bug，同一个频道可以开启两次实时翻译，需要加一个判断
    if msg.ctx.channel.id in ListTL:
        await msg.reply(f"本频道已经开启了实时翻译功能，请勿重复操作!")
        return
    i = 0
    while i < len(ListTL):
        if ListTL[i] == '0':
            ListTL[i] = msg.ctx.channel.id
            break
        i += 1
    ret = tl_check()
    await msg.reply(f"Real-Time Translation ON\n阿狸现在会实时翻译本频道的对话啦！\n目前栏位: {ret}/{len(ListTL)}，使用`/TLOFF`可关闭实时翻译哦~")


#关闭频道实时翻译
async def tl_close(msg: Message):
    global ListTL
    i = 0
    while i < len(ListTL):
        if ListTL[i] == msg.ctx.channel.id:
            ListTL[i] = '0'
            await msg.reply(f"Real-Time Translation OFF！目前栏位: {tl_check()}/{len(ListTL)}")
            return
        i += 1
    await msg.reply(f"本频道并没有开启实时翻译功能！目前栏位: {tl_check()}/{len(ListTL)}")


################################################################################################


def init(bot:Bot):
    """bot: main bot"""
    # 普通翻译指令
    @bot.command(name='TL', case_sensitive=False)
    async def translation_cmd(msg: Message, *arg):
        BotLog.logMsg(msg)
        await translate_main(msg, ' '.join(arg))


    #查看当前占用的实时翻译栏位
    @bot.command(name='tlck',case_sensitive=False)
    async def translation_check_cmd(msg: Message):
        BotLog.logMsg(msg)
        await msg.reply(f"目前已使用栏位:{tl_check()}/{len(ListTL)}")


    # 关闭所有栏位的实时翻译（避免有些人用完不关）
    @bot.command(name='ShutdownTL', aliases=['tlsd'],case_sensitive=False)
    async def translation_shutdown_cmd(msg: Message):
        try:
            BotLog.logMsg(msg)
            if not is_admin(msg.author_id):
                return  #这条命令只有bot的作者可以调用
            await tl_shutdown(bot, msg)
        except:
            await BotLog.BaseException_Handler("tlsd",traceback.format_exc(),msg)

    # 通过频道id判断是否实时翻译本频道内容
    @bot.on_message()
    async def translation_realtime_on_msg(msg: Message):
        if msg.ctx.channel.id in ListTL:  #判断频道是否已开启实时翻译
            word = msg.content
            # 不翻译关闭实时翻译的指令
            ignore_list = ["/TLOFF","/tloff","/tlon","/TLON"]
            for i in ignore_list:
                if i in word:
                    return
            # 翻译
            BotLog.logMsg(msg)
            await translate_main(msg,word)

    # 开启实时翻译功能
    @bot.command(name='TLON',case_sensitive=False)
    async def translation_on(msg: Message):
        BotLog.logMsg(msg)
        await tl_open(msg)


    # 关闭实时翻译功能
    @bot.command(name='TLOFF',case_sensitive=False)
    async def translation_off(msg: Message):
        BotLog.logMsg(msg)
        await tl_close(msg)