## 一次瞎升级python导致的错误记录

本README和这个文件夹没有任何关系，只是写出来给自己留档做个记录

### 1.不要瞎改配置文件

>* https://blog.csdn.net/u010377516/article/details/108603559
>* https://blog.csdn.net/weixin_41829333/article/details/110141988

我先是参考了一些奇葩博客，里面说道了下载完python新版本后，需要修改下面两个yum的配置文件

~~~
/usr/bin/yum
/usr/libexec/urlgrabber-ext-down
~~~

说是要把开头的`#!/usr/bin/python2.7`修改为升级后的版本

实际上，压根不要修改这个配置文件！！！！

因为修改了之后执行yum会出现下面这个报错

~~~
-bash: /usr/bin/yum: /usr/bin/python: 坏的解释器: 没有那个文件或目录
~~~

> 参考这篇博客，把配置文件该回去才让yum复活[【链接】](https://www.cxymm.net/article/weixin_41857283/101363002)

yum是基于`python2.7`的，你没事把人家依赖环境改了干哈子？

----

### 2.要对症下药

教程博客里面提到了，需要重新创建软连接，这是没错

~~~
ln -sf /usr/local/bin/python3.8 /usr/bin/python
ln -sf /usr/local/bin/python3.8-config /usr/bin/python-config
~~~

但是，并不是所有人的软连接都是用上面的代码创建！

在执行完python新版本的`make`后，你需要通过下面的两个指令找到新版本py的安装路径

~~~
[root@bt-7274:~]# whereis python
python: /usr/bin/python3.6m /usr/bin/python3.6 /usr/bin/python /usr/bin/python2.7-config /usr/bin/python2.7 /usr/lib/python3.6 /usr/lib/python2.7 /usr/lib64/python3.6 /usr/lib64/python2.7 /etc/python /usr/local/bin/python3.9-config /usr/local/bin/python3.9 /usr/local/lib/python3.9 /usr/include/python3.6m /usr/include/python2.7 /usr/local/python3/bin/python3.7 /usr/local/python3/bin/python3.9-config /usr/local/python3/bin/python3.7-config /usr/local/python3/bin/python3.9 /usr/local/python3/bin/python3.7m-config /usr/local/python3/bin/python3.7m /usr/share/man/man1/python.1.gz

[root@bt-7274:~]# which python
/usr/bin/python
~~~

比如我这里很明显能看出来，我的新版本`python3.9`是安装在`/usr/local/bin`里面，而不是`/usr/bin`里面的

同时，当我执行py出错时，报错的路径也是下面这个

~~~
-bash: /usr/local/bin/python3: 没有那个文件或目录
~~~

所以创建软链接的时候，需要对症下药进行修改！

~~~
ln -s /usr/local/python3/bin/python3 /usr/local/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip3
~~~

这样才能让py成功升级！

### 3.请重下依赖库

本项目的机器人是基于`khl.py`的，而下载依赖库的时候，其实是只安装在了对应版本的python里面，也就是我的旧版本`python3.7.8`

所以在升级py之后，需要重下`khl.py`

---

行吧，要说的好像就这么多

吓死我了