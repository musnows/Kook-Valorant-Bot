.PHONY:run
run:
	nohup python3.10 -u start.py >> /dev/null 2>&1 &
# 包含khl输出结果的信息里面会有用户的账户密码，重定向到黑洞，避免打印账户密码
.PHONY:ps
ps:
	ps jax | head -1 && ps jax | grep start.py | grep -v grep