.PHONY:run
run:
	nohup py3 -u start.py >> ./log/bot.log 2>&1 &

.PHONY:ps
ps:
	ps jax | head -1 && ps jax | grep start.py | grep -v grep