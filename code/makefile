.PHONY:run
run:
	nohup python3.10 -u start.py >> ./log/out.log 2>&1 &

.PHONY:ps
ps:
	ps jax | head -1 && ps jax | grep start.py | grep -v grep