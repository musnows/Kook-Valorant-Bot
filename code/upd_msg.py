import json
from typing import Union
from khl import Bot,ChannelPrivacyTypes

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])

# 图标
class icon:
    val_logo = "https://img.kookapp.cn/assets/2022-09/gVBtXI0ZSg03n03n.png"
    val_logo_gif ="https://img.kookapp.cn/assets/2022-09/5skrwZcjGJ0dc07i.gif" 
    whats_that="https://img.kookapp.cn/assets/2022-09/uhm2AewC1i0e80e8.png"
    dont_do_that="https://img.kookapp.cn/assets/2022-09/wUNDAfzBlr0e80e8.png"
    lagging="https://img.kookapp.cn/assets/2022-09/D1nqrTszjQ0e80e8.png"
    correct="https://img.kookapp.cn/assets/2022-09/DknXSpwrlQ0e80e8.gif"
    duck="https://img.kookapp.cn/assets/2022-09/qARsaxW6lp0e80e8.gif"
    that_it = "https://img.kookapp.cn/assets/2022-09/LqD0pQY2P70e80e8.png"
    to_much_money="https://img.kookapp.cn/assets/2022-09/y17ZhjjaVf0e80e8.png"
    shaka = "https://img.kookapp.cn/assets/2022-09/kMWT5AoEic0e80e8.png"

#更新卡片消息
async def upd_card(msg_id: str, content, target_id='', 
                    channel_type: Union[ChannelPrivacyTypes, str] = 'public',bot=bot):
    content = json.dumps(content)
    data = {'msg_id': msg_id, 'content': content}
    if target_id != '':
        data['temp_target_id'] = target_id
    if channel_type == 'public' or channel_type == ChannelPrivacyTypes.GROUP:
        result = await bot.client.gate.request('POST', 'message/update', data=data)
    else:
        result = await bot.client.gate.request('POST', 'direct-message/update', data=data)
    return result