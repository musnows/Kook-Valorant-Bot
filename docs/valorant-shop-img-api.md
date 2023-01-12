## 欢迎您使用阿狸瓦洛兰特商店Api

Api链接为`val.outpost54.top`。只有这一个网址！

Api是一个网页链接，能够方便的被用户使用或被开发者调用，以实现特定功能

和阿狸机器人一样，**此api后台不会打印任何params参数**。只要链接不被攻击，你的账户密码只有你自己使用的时候看得到！很是安全

>有任何问题，请用kook和我联系！[kook帮助服务器邀请链接](https://kook.top/gpbTwZ)

| 接口 | 说明                  | 状态 |
| ---------- | --------------------- | -------- |
| /shop-img  | 直接返回并跳转商店的图片  | 正常   |
| /shop-url  | 以`json`格式返回商店图片url  | 正常   |
| /tfa  | 邮箱验证接口，需和/shop-url接口配合使用 | 正常   |


## 1.使用示例

查询每日商店的链接如下，调用`/shop-img`接口，浏览器会直接跳转图片，适合普通用户快捷查看当日每日商店

由于该接口会直接跳转到图片，所以不支持开启了邮箱验证的用户

~~~
https://val.outpost54.top/shop-img?token=API的密钥&account=账户&passwd=密码
~~~

直接丢浏览器里面打开就行，想看商店直接用这个链接看就行辣，可以浏览器收藏一下哦！

* 添加第四个参数`&img_src=图片url`，此参数用于自定义背景图
* 添加第五个参数`&img_ratio=图片比例`，将此参数设置为`1`，代表背景图是 `1-1` 的正方形，最终的成果图也将是正方形；默认比例为 `16-9`
* 注：如果选择 `1-1` 的返回图，则图中不会带vp和rp剩余


若要添加自定义背景图，则链接应该如下
~~~
https://val.outpost54.top/shop-img?token=API的密钥&account=账户&passwd=密码&img_src=背景图片链接
~~~

如果背景图是1-1的正方形
~~~
https://val.outpost54.top/shop-img?token=API的密钥&account=账户&passwd=密码&img_src=背景图片链接&img_ratio=1
~~~

自定义背景图请求示例（16-9）

~~~
https://val.outpost54.top/shop-img?token=API的密钥&account=账户&passwd=密码&img_src=https://img.kookapp.cn/assets/2022-09/KV5krdRx080qo0f0.jpg
~~~

结果示例图（16-9）

<img src="https://img.kookapp.cn/assets/2023-01/2Vffq4s9rX1ry0zj.png" alt="16-9-img-result">

## 2.注意事项

自定义背景图的url请使用国内可以直接访问的图床，如`阿里云OSS/路过图床/白嫖kook的图床`等。否则无法获取到图片链接的内容，api会报错；

> * 路过图床：https://imgse.com/
> * 薄荷图床：https://riyugo.com/
> * kook图床白嫖教程：https://img.kookapp.cn/assets/2022-12/nICYcewY8a0u00yt.png

欢迎大家向朋友宣传此Api，但请不要恶意连续多次调用

## 3.开发者接口

由于服务器是个6m小水管，再加上刚开放的时候本地缓存不足，画图耗时长。所以响应很慢，大约12秒。所以，我估摸着也没有开发者愿意用这种慢吞吞的api吧？

好处就是后台包装了**图片处理+riot登录**，你只需要传入账户密码，剩下的交给api解决！

注：只有`code 0`才是获取正常，`200/400` 都是有错误，会返回错误的原因。

### 3.1 /shop-url

如果你是开发者，请使用`/shop-url`来获取`json`格式的结果

~~~
https://val.outpost54.top/shop-url
~~~

请求方法：`GET`

速率限制：`10r/m`

| params参数 | 说明                  | 是否必填 |
| ---------- | --------------------- | -------- |
| token      | API token             | 是       |
| account    | 拳头账户              | 是       |
| passwd     | 拳头账户密码          | 是       |
| img_src    | 自定义背景图的url链接 | 否       |
| img_ratio    | 自定义背景图比例，值为1代表正方形 | 否       |

返回示例

~~~json
{
    "code": 0, 
    "message": "https://img.kaiheila.cn/attachments/2022-10/12/1GaII87UTd0zk0k0.png", 
    "info": "商店图片获取成功"
}
~~~

### 3.2 /tfa

此接口用于两步验证，适用于开启了邮箱验证的用户；

您需要先请求 `/shop-url` 接口，在用户获取到验证码后，再请求本接口

~~~
https://val.outpost54.top/tfa
~~~

请求方法：`POST`

| params参数 | 说明                  | 是否必填 |
| ---------- | --------------------- | -------- |
| token      | API token             | 是       |
| account    | 拳头账户              | 是       |
| vcode   | 邮箱验证码 | 是       |

返回示例

~~~json
{
    "code": 0, 
    "message": "email verify code post success,wait for shop img return", 
    "info": "两步验证码获取成功，请等待主接口返回",
    "vcode": 114514
}
~~~


## 4.Python示例代码

~~~python
import requests

url = "https://val.outpost54.top/shop-url"
params = {
    "token":"你的api-token",
    "account": "拳头账户",
    "passwd": "拳头密码",
    "img-src": "https://img.kookapp.cn/assets/2022-09/KV5krdRx080qo0f0.jpg"
}
res = requests.get(url,params=params,verify=False)
print(res.json())
~~~

由于ssl证书原因，您使用的时候可能会遇到下面的报错，请忽略。

~~~
/home/muxue/.local/lib/python3.10/site-packages/urllib3/connectionpool.py:1045: InsecureRequestWarning: Unverified HTTPS request is being made to host 'val.outpost54.top'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
  warnings.warn(
~~~

网站使用的是`JOYSSL`提供的ssl证书，直接访问**不会**报不安全。本人很菜，不知道这里的报错是啥原因

可以用下面的办法解除这个报错

~~~python
from urllib3.connectionpool import InsecureRequestWarning
import urllib3
urllib3.disable_warnings(InsecureRequestWarning)
~~~

