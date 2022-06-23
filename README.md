## Valorant-kaiheila-bot
这是一个开黑啦的[Valorant]小机器人

## 功能
当前机器人处于极极极其早期版本，目前只支持回复valorant游戏错误码，和一些简单功能
* `/hello`：回复 world！
* `/Ahri`：回复使用方法的help
* `/val 错误码`：回复解决方法
* `/saveid`：保存（修改）用户的游戏id
* `/myid`：显示用户的游戏id
* `/roll 1 100`：掷色子1-100，范围可自行调节
* `/countdown 秒数`： 倒计时，默认60秒

----

## 如何使用？

保证你的Linux中`python`版本高于3.6.8，执行下面的安装库命令

~~~
pip install khl.py
或者 pip3 install khl.py
~~~

当你根据[khl.py](https://github.com/TWT233/khl.py)的`example`教程完成了基本机器人的搭建后，还需要执行下面几个小步骤

### 1.让机器人在后台运行

下面这个代码的功能是让机器人在Linux后台运行，并将输出内容写入log文件。
```
nohup python3 -u main.py>./log/bot.log 2>&1&
```
执行后，Linux会给你返回一个进程编号。

> 为了不让机器人的log也被他人看到，我也将log类型文件写入了`.gitignore`

我们可以通过`ps -e`查看当前正在运行的进程，但这样的缺点是，当你关闭Xshell后，下一次再打开，就会发现之前的进程貌似不见了。这时候就可以用下面这个语句来**具体定位**之前已经在运行的后台程序

~~~
ps -aux|grep main.py|grep -v grep 
~~~

当你想让机器人下岗的时候，可以使用下面这个指令

```
kill -9 进程号
```

### 2.等待补充……

----

## TODO

下面是一些未来的计划

- [x] 增加保存用户游戏id的功能
- [ ] 学习python
- [ ] 学习接入官方的`valorant api`库
- [ ] 实现玩家商店刷枪的查询
- [ ] 实现当商店刷新某一把枪的时候提醒玩家

---

## 依赖

由于本人压根没有学过python，所以本仓库的很多代码都是根据他人教程修改后使用的
* 基本代码参考[khl.py](https://github.com/TWT233/khl.py)提供的api库以及使用教程
* 早期使用了`https://replit.com/`和`https://uptimerobot.com/`提供的服务，无需使用**云服务器**也可部署机器人。这两个网站的使用教程见[B站视频](https://www.bilibili.com/video/BV12U4y1g7JY?spm_id_from=333.1007.top_right_bar_window_history.content.click)，代码可以查看`code/EarlyTest`里面的内容（注意，部署到云服务器的方式和这两个网站是不一样的）


