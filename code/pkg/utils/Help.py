from khl.card import CardMessage, Card, Module, Element, Types


def help_main(start_time: str):
    cm = CardMessage()
    c3 = Card(
        Module.Header('你可以用下面这些指令呼叫本狸哦！'),
        Module.Context(
            Element.Text(f"开源代码见[Github](https://github.com/Aewait/Valorant-Kook-Bot)，开机于 [{start_time}]",
                         Types.Text.KMD)))
    c3.append(Module.Section('「/hello」来和本狸打个招呼吧！\n「/Ahri」 帮助指令\n'))
    c3.append(Module.Divider())
    c3.append(Module.Header('上号，瓦一把！'))
    text = "「/val 错误码」 游戏错误码的解决方法，0为已包含的val报错码信息\n"
    text += "「/dx」 关于DirectX Runtime报错的解决方案\n"
    text += "「/saveid 游戏id」 保存(修改)您的游戏id\n"
    text += "「/myid」 让阿狸说出您的游戏id\n"
    text += "「`/vhelp`」瓦洛兰特游戏查询相关功能的帮助\n"
    #text += "[如果你觉得这些功能还不错，可以支持一下阿狸吗?](https://afdian.net/a/128ahri?tab=shop)"
    c3.append(Module.Section(Element.Text(text, Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Header('和阿狸玩小游戏吧~ '))
    text = "「/roll 1 100」掷骰子1-100，范围可自主调节。可在末尾添加第三个参数实现同时掷多个骰子\n"
    text += "「/countdown 秒数」倒计时，默认60秒\n"
    text += "「/TL 内容」翻译内容，支持多语译中和中译英\n"
    text += "「/TLON」 在本频道打开实时翻译\n"
    text += "「/TLOFF」在本频道关闭实时翻译\n"
    text += "「/we 城市」查询城市未来3天的天气情况\n"
    text += "「更多…」还有一些隐藏指令哦~\n"
    c3.append(Module.Section(Element.Text(text, Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Section(' 游戏打累了？想来本狸的家坐坐吗~', Element.Button('让我康康', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c3)
    return cm


def help_val():
    cm = CardMessage()
    c3 = Card(
        Module.Header('目前阿狸支持查询的valorant信息如下'),
        Module.Context(
            Element.Text("开源代码见[Github](https://github.com/Aewait/Valorant-Kook-Bot)，更多查询功能上线中...", Types.Text.KMD)))
    text = "使用前，请确认您知晓相关功能可能有风险：\n"
    text += "1.阿狸的后台不会做任何`打印`您的游戏账户密码的操作，若在使用相关功能后被盗号，阿狸可不承担任何责任;\n"
    text += "2.如果您发现登陆后阿狸还提醒您没有登录，那是因为阿狸的作者正在调试阿狸，重启后登录信息会消失。感谢谅解;\n"
    text += "3.目前查询功能稳定性尚可，但无法排除`封号`风险;\n"
    text += "4.指定save后，账户密码是存在全局变量(内存)中的，并不会存到硬盘里面。只要bot下线(进程退出)就会被清除;\n"
    text += "若担心相关风险，请不要使用如下功能\n"
    c3.append(Module.Section(Element.Text(text, Types.Text.KMD)))
    c3.append(Module.Divider())
    help_1 = "「/bundle 皮肤名」 查询皮肤系列包含什么枪械\n"
    help_1 += "「/login 账户 密码」请`私聊`使用，登录您的riot账户\n"
    help_1 += "「/login 账户 密码 save」登录并临时保存账户密码 [说明](https://img.kookapp.cn/assets/2023-02/iA5rabCKtT1210az.png)\n"
    help_1 += "「/login-l」查看已登录账户\n"
    help_1 += "「/logout」取消登录\n"
    help_1 += "「/shop」 查询您的每日商店\n"
    help_1 += "「/night」查询您的夜市\n"
    help_1 += "「/uinfo」查询当前装备的卡面/称号/剩余vp和r点\n"
    help_1 += "「/mission」查询您的每日/每周任务（开发中，[说明](https://img.kookapp.cn/assets/2023-03/THlb3FlXWo0q40j0.png)）\n"
    help_1 += "「/match」查询最近5场比赛的历史记录\n"
    help_1 += "「/notify-a 皮肤名」查询皮肤，并选择指定皮肤加入每日商店提醒\n"
    help_1 += "「/notify-l 」查看当前设置了提醒的皮肤\n"
    help_1 += "「/notify-d 皮肤uuid」删除不需要提醒的皮肤\n"
    help_1 += "「/rate 皮肤名」查找皮肤，选择指定皮肤进行打分\n"
    help_1 += "「/rts 序号 打分 吐槽」选中皮肤序号，给该皮肤打个分(0~100) 再吐槽一下!\n"
    help_1 += "「/kkn」查看昨日评分最高/最低的用户\n"
    c3.append(Module.Section(Element.Text(help_1, Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Header("以下进阶功能，发电支持阿狸即可解锁哦~"))
    help_2 =  "「/vip-u 激活码」兑换阿狸的vip\n"
    help_2 += "「/vip-c」 查看vip的剩余时间\n"
    help_2 += "「全新商店展示图」vip用户将获取到16-9的超帅商店返回值\n"
    help_2 += "「/vip-shop」查看已保存的商店查询diy背景图\n"
    help_2 += "「/vip-shop 图片url」添加商店查询diy背景图\n"
    help_2 += "「/vip-shop-s 图片编号」切换商店查询的背景图\n"
    help_2 += "「保存登录信息」vip用户登陆后，阿狸会自动保存您的cookie。在阿狸维护重启的时候，您的登录信息不会丢失\n"
    help_2 += "「早八商店提醒」阿狸将在早8点获取vip用户的每日商店并私聊发图给用户。同时会对这张图片进行缓存，当天使用`/shop`命令的时候，只需2s获取结果，三倍于普通用户的响应速度！\n\n"
    help_2 += "1.目前商店查询diy背景图支持16-9(横屏)的图片，图片url获取：PC端将图片上传到kook→点击图片→底部`...`处复制图片链接→使用`/vip-shop`命令设置背景 [教程图](https://img.kookapp.cn/assets/2022-12/nICYcewY8a0u00yt.png)\n"
    help_2 += "2.请不要设置违规图片(擦边也不行)！若因为您上传违禁图片后导致阿狸被封，您将被剥夺vip并永久禁止兑换vip\n"
    c3.append(Module.Section(Element.Text(help_2, Types.Text.KMD)))
    c3.append(
        Module.Context(
            Element.Text("[如果你觉得这些功能还不错，可以发电支持一下阿狸吗?](https://afdian.net/a/128ahri?tab=shop)", Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Section('若有任何问题，欢迎加入帮助频道', Element.Button('来狸', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c3)
    return cm


def help_develop():
    text = f"主人有何吩咐呀~\n```\n"
    text += f"[/Color_Set] 发送一个用于设置用户颜色的消息，只能在valorant社区使用\n"
    text += f"[/Color_Set_GM 消息id] 在不修改代码的前提下设置上色功能的服务器和监听消息\n"
    text += f"[/ShutdownTL] 关闭所有实时翻译的栏位\n"
    text += f"[/vip-a 天数 数量] 生成新的vip激活码\n"
    text += f"[/vip-l] 查看当前vip用户列表\n"
    text += f"[/vip-img] 检查vip用户的自定义背景图（防止违规图片）\n"
    text += f"[/vip-r 天数 数量 抽奖天数] 开启vip抽奖\n"
    text += f"[/vip-ta 天数] 给所有vip用户添加时长\n"
    text += f"[/ckau] 查看已登录的用户个数\n"
    text += f"[/upd] 手动更新商店物品和价格\n"
    text += f"[/open-nm] 打开/关闭夜市\n"
    text += f"[/ban-r 用户id] 禁止用户使用rate相关功能\n"
    text += f"[/notify-test] 执行遍历用户皮肤notify列表\n"
    text += f"[/lf] 实际上是LoginForbidden的缩写，在login函数403时屏蔽所有需要login的命令\n"
    text += f"[/log] 显示当前阿狸加入的服务器以及用户数量\n"
    text += f"[/mem] 显示当前阿狸进程的内存占用和cpu占用\n```"
    return text