import json
import aiohttp

from khl import Bot, Message
from main import master_id,bot

# 本部分暂时没有启用！


# 监看邀请链接
ListIV = ['0','0','0','0']

# 查看目前已经占用的容量
def checkIV():
    sum=0
    for i in ListIV:
        if i !='0':
            sum+=1
    return sum

# 查看监看邀请的频道
@bot.command()
async def CheckIV(msg:Message):
    global ListIV
    await msg.reply(f"目前已使用栏位:{checkIV()}/{len(ListIV)}")


# 关闭所有栏位的实时翻译（避免有些人用完不关）
@bot.command()
async def ShutdownIV(msg:Message):
    if msg.author.id != master_id:
        return #这条命令只有bot的作者可以调用
    global ListIV
    if checkIV()==0:
        await msg.reply(f"邀请链接实时监控栏位为空: {checkIV()}/{len(ListIV)}")
        return
    i=0
    while i< len(ListIV):
        if(ListIV[i])!='0': #不能对0的频道进行操作
            ListIV[i] = '0'
        i+=1
    await msg.reply(f"邀请链接实时监控已清空！目前为: {checkIV()}/{len(ListIV)}")

# 监看url
async def invite(msg:Message,url:str):
    print(url)
    num=url.find('https://kook.top/')#返回子串开头的下标
    if num != -1:
        code = url[num+17:num+23]
        url = 'https://www.kaiheila.cn/api/v2/invites/'+code
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                    ret =json.loads(await response.text())
                    print(ret['guild'])
                    if ret['guild']['id'] != msg.ctx.guild.id:
                        await msg.reply(f"(met){ret['inviter']['id']}(met) 请不要发送其他频道的邀请链接！")
                        await msg.delete()


# 通过频道id判断是否实时监看本频道的邀请链接
@bot.command(regex=r'(.+)')
async def IV_Realtime(msg:Message,*arg):
    word = " ".join(arg)
    # 不翻译关闭监看的指令
    if word == "/IVOFF" or word =='/IVON':
        return
    global ListIV
    if msg.ctx.channel.id in ListIV:
        await invite(msg,' '.join(arg))
        return


# 开启实时翻译功能
@bot.command(name='TLON',aliases=['tlon'])
async def IVON(msg: Message):
    #print(msg.ctx.channel.id)
    global ListIV
    if checkIV() == len(ListIV):
        await msg.reply(f"目前栏位: {checkIV()}/{len(ListIV)}，已满！")
        return

    if msg.ctx.channel.id in ListIV:
         await msg.reply(f"邀请链接实时监控已开启，请勿重复操作!")
         return
    i=0
    while i< len(ListIV):
        if ListIV[i] == '0':
            ListIV[i] = msg.ctx.channel.id
            break
        i+=1
    ret = checkIV()
    await msg.reply(f"邀请链接实时监控已开启！目前栏位: {ret}/{len(ListIV)}")


# 关闭实时监看
@bot.command(name='TLOFF',aliases=['tloff'])
async def IVOFF(msg: Message):
    global ListIV
    i=0
    while i< len(ListIV):
        if ListIV[i] == msg.ctx.channel.id:
            ListIV[i] = '0'
            await msg.reply(f"已关闭邀请链接实时监控，目前栏位: {checkIV()}/{len(ListIV)}")
            return
        i+=1
    await msg.reply(f"本频道并没有开启实时监控！目前栏位: {checkIV()}/{len(ListIV)}")