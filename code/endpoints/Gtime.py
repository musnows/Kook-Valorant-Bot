import time

#将获取当前时间封装成函数方便使用
def GetTime():  
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
#将获取当前日期成函数方便使用
def GetDate(): 
    return time.strftime("%y-%m-%d", time.localtime())