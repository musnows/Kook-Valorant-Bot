import json
# import requests
import aiohttp
import urllib.request
import urllib.parse

# youdao code is from https://github.com/Chinese-boy/Many-Translaters
def youdao_translate(*args):
        txt = " ".join(args)
        #print(txt)
        url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&sessionFrom=https://www.baidu.com/link'
        data = {'from': 'AUTO', 'to': 'AUTO', 'smartresult': 'dict', 'client': 'fanyideskweb', 'salt': '1500092479607',
                'sign': 'c98235a85b213d482b8e65f6b1065e26', 'doctype': 'json', 'version': '2.1', 'keyfrom': 'fanyi.web',
                'action': 'FY_BY_CL1CKBUTTON', 'typoResult': 'true', 'i': txt}

        data = urllib.parse.urlencode(data).encode('utf-8')
        wy = urllib.request.urlopen(url, data)
        html = wy.read().decode('utf-8')
        ta = json.loads(html)
        #print(ta['translateResult'][0][0]['tgt'])
        return ta['translateResult'][0][0]['tgt']


# 读取彩云的key
with open('./config/caiyun.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

CyKey = config['token']

# caiyun translte
async def caiyun_translate(source, direction):
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

#     response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
#     return json.loads(response.text)["target"]
        #用这个效率更高
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=headers) as response:
                return json.loads(await response.text())["target"]



# 由于彩云不支持输入中文自动翻译成英文（目前只支持其他语种自动转中文）
# 所以需要判断来源是否是中文，如果是中文自动翻译成English
def is_CN(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


# # for test
# txt = input()
# if is_Chinese(txt):
#     target = tranlate(txt, "auto2en")
# else:
#     target = tranlate(txt, "auto2zh")
# print(target)