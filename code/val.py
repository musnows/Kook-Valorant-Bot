# encoding: utf-8:
import json
import valorant

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct
from khl.command import Rule

# 用读取来的 config 初始化 bot，字段对应即可
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

bot = Bot(token=config['token'])

# 读取valorant api的key
with open('./config/valorant.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

KEY = config['token']

##########################################################################################
##########################################################################################

# 没啥用的中二病指令
async def kda123(msg: Message):
    await msg.reply('本狸就是女王！\n[https://s1.ax1x.com/2022/07/03/jGFl0U.jpg](https://s1.ax1x.com/2022/07/03/jGFl0U.jpg)')

# 查询皮肤！只支持English皮肤名
async def skin123(msg: Message,name:str):
    try:
        client = valorant.Client(KEY, locale=None)
        skins = client.get_skins()
        #name = input("Search a Valorant Skin Collection: ")
        results = skins.find_all(name=lambda x: name.lower() in x.lower())
        cm = CardMessage()
        c1 = Card(Module.Header('查询到你想看的皮肤了！'),Module.Context('还想查其他皮肤吗...'))
        c1.append(Module.Divider())
        for skin in results:
            c1.append(Module.Section(f"\t{skin.name.ljust(21)} ({skin.localizedNames['zh-TW']})"))
            #print(f"\t{skin.name.ljust(21)} ({skin.localizedNames['zh-CN']})")
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        await msg.reply("未知错误 %s" % result)

# 获取排行榜上的玩家，默认获取前15位胜场超过10的玩家
async def lead123(msg: Message,sz:int,num:int):
    try:
        client = valorant.Client(KEY, locale=None,region='ap',route='asia')
        lb = client.get_leaderboard(size=sz)
        players = lb.players.get_all(numberOfWins=num)# 筛选出胜场超过num的
        cm = CardMessage()
        c1 = Card(Module.Header('查询到你想看的排行榜了！'),Module.Context('什么？你也上榜了嘛...'))
        c1.append(Module.Divider())
        for p in lb.players:
            c1.append(Module.Section(f"#{p.leaderboardRank} - {p.gameName} ({p.numberOfWins} wins)"))
            #print(f"#{p.leaderboardRank} - {p.gameName} ({p.numberOfWins} wins)")
        cm.append(c1)
        await msg.reply(cm)
    except Exception as result:
        await msg.reply("未知错误 %s" % result)


#保存用户id
async def saveid123(msg: Message,game1:str):
     flag=0
     # 需要先保证原有txt里面没有保存该用户的id，才进行追加
     with open("./log/idsave.txt", 'r',encoding='utf-8') as fr1:
        lines=fr1.readlines()   
     #使用r+同时读写（有bug）
     with open("./log/idsave.txt", 'w',encoding='utf-8') as fw1: 
        for line in lines:
            v = line.strip().split(':')
            if msg.author_id == v[0]:
                fw1.write(msg.author_id+ ':' + game1 + '\n')
                await msg.reply(f'本狸已经修改好你的游戏id啦!')
                flag=1#修改完毕后，将flag置为1
            else:
                fw1.write(line)
     fr1.close()
     fw1.close()
     #原有txt内没有该用户信息，进行追加操作
     if flag==0:
        fw2 = open("./log/idsave.txt",'a+',encoding='utf-8')
        #fw.write(str(gamerid))      #把字典转化为str
        fw2.write(msg.author_id+':'+game1+'\n')  
        await msg.reply(f'本狸已经记下你的游戏id啦!')
        fw2.close()


# 计算txt文件中有几行
def countline(file_name):
    with open(file_name,'rb') as f:
        count = 0
        last_data = '\n'
        while True:
            data = f.read(0x400000)
            if not data:
                break
            count += data.count(b'\n')
            last_data = data
        if last_data[-1:] != b'\n':
            count += 1
            
    return count

# 让阿狸记住游戏id的help指令
async def saveid1(msg: Message):
    await msg.reply("基本方式看图就行啦！如果你的id之中有空格，需要用**英文的单引号**括起来哦！就像这样: `/saveid '你的id'`\n[https://s1.ax1x.com/2022/06/27/jV2qqe.png](https://s1.ax1x.com/2022/06/27/jV2qqe.png)\n")

# 显示已有id的个数
async def saveid2(msg: Message):
    ret=countline("./log/idsave.txt")
    await msg.reply("目前狸狸已经记下了%d个小伙伴的id喽~"% (ret))

     
# 实现读取用户游戏ID并返回
async def myid123(msg: Message):
    flag=0
    fr = open("./log/idsave.txt",'r',encoding='utf-8')
    for line in fr:
        v = line.strip().split(':')
        if msg.author_id in v[0]:
           flag=1#找到了对应用户的id
           await msg.reply(f'游戏id: '+v[1])
    fr.close()
    if flag==0:
       ret=countline("./log/idsave.txt")
       await msg.reply("狸狸不知道你的游戏id呢，用`/saveid`告诉我吧！\n基本方式看图就行啦！如果你的id之中有空格，需要用英文的单引号括起来哦！就像这样: `/saveid '你的id'`\n[https://s1.ax1x.com/2022/06/27/jV2qqe.png](https://s1.ax1x.com/2022/06/27/jV2qqe.png)\n目前狸狸已经记下了%d个小伙伴的id喽！"% (ret))



# 查询游戏错误码
async def val123(msg: Message, num: int):
    # msg 触发指令为 '/val 错误码'
    # msg.reply() 根据错误码回复对应解决方法
    if num ==0:
        await msg.reply('目前支持查询的错误信息有：\n「val 1,4-5,7-21,29,31,33,38,43-46,49-70,81,84,128,152,1067,9001,9002」')
    elif num == 1067:
        await msg.reply('1.请检查您的电脑是否有安装「完美对战平台」，可能有冲突；\n2.请在「控制面板-时钟和区域」中尝试修改时区为`美国`或者`香港`，这不会影响您电脑的时间显示；\n3.尝试重启游戏、重启加速器（更换节点）、重启电脑；\n4.可能和您的鼠标驱动有冲突，尝试关闭雷蛇/罗技的鼠标驱动软件;\n5.尝试进入bios开启tmp2.0\n6.卸载valorant，打开csgo/ow/r6。')
    elif num == 1:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 4:
        await msg.reply('您的名称无效，请重新注册账户')
    elif num == 5:
        await msg.reply('1.账户在别处登录；\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 7:
        await msg.reply('账户可能被冻结，请查看注册邮箱是否有相关邮件信息')
    elif num > 7 and num <=11:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 12:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num >= 13 and num <=21:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 29:
        await msg.reply('1.防火墙问题，尝试关闭系统防火墙；\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 31:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 33:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num == 38:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 43:
        await msg.reply('客户端启动超时，检查网络后重启客户端，或重新下载游戏客户端')
    elif num >= 44 and num <= 45:
        await msg.reply('反作弊未初始化：重启拳头客户端,如果未恢复,先卸载Vanguard,重启电脑后再启动游戏')
    elif num == 46:
        await msg.reply('服务器维护中……')
    elif num >= 49 and num <= 60:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 61:
        await msg.reply('哎呀你干了啥，怎么被系统ban了？狸狸可不喜欢你这样哦~')
    elif num >= 62 and num <= 67:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 68:
        await msg.reply('1.请尝试关闭valorant，右键图标以管理员身份运行游戏\n2.网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num >= 69 and num <= 70:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 81:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 84:
        await msg.reply('网络连接问题，请重启游戏、更换加速器（节点）、重启电脑。')
    elif num == 128:
        await msg.reply('1.重启电脑和游戏客户端，卸载Vanguard、卸载游戏进行重装；\n2.需要提醒您，修改系统配置是一项有风险的操作，请确认您需要这么做！\n请查看本图进行操作:[https://s1.ax1x.com/2022/06/24/jFGXBd.png](https://s1.ax1x.com/2022/06/24/jFGXBd.png) ')
        #这里要使用[URL](URL)的方式，让开黑啦识别出图片url并直接显示
    elif num == 152:
        await msg.reply('您的硬件被识别封锁，这可不是一个好兆头。')
    elif num == 9001:
        await msg.reply('`VAN9001_This build of Vanguard requires TPM version 2.0 and secure boot to be enabled in order to play.`\n需要您进电脑主板的bios打开tmp2.0哦！')
    elif num == 9002:
        await msg.reply('`VAN9002—This build of Vanguard requires Control Flow Guard (CFG)to be enabled in system exploit protection settings.`\n设置页面搜索Exploit Protection ，[开启控制流保护（CFG）](https://www.bilibili.com/read/cv11536577)。')
    elif num == 10086:
        await msg.reply('本狸才不给你的手机充话费呢！')
    elif num == 10000:
        await msg.reply('本狸提醒您：谨防电信诈骗哦~')
    else:
        await msg.reply('抱歉，本狸还不会这个呢~ 你能教教我吗？[当然!](https://f.wps.cn/w/awM5Ej4g/)')

#关于dx报错的解决方法
async def dx123(msg: Message):
    await msg.reply('报错弹窗内容为`The following component(s) are required to run this program:DirectX Runtime`\n需要下载微软官方驱动安装，官网搜索[DirectX End-User Runtime Web Installer]\n你还可以下载本狸亲测可用的DX驱动 [链接](https://pan.baidu.com/s/1145Ll8vGtByMW6OKk6Zi2Q)，暗号是1067哦！\n狸狸记得之前玩其他游戏的时候，也有遇到过这个问题呢~')

