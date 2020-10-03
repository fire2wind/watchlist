## pythonanywhere部署时出现的问题

#### No module named 'dotenv'

我 Windows 中的 python 版本为 3.7

可能是版本不匹配的原因，如果直接用 `python -m venv env` 创建虚拟环境，会默认使用 python3.8（内置的最高版本），因此使用 `python3.7 -m venv env` ，在用 requirements.txt的时候用 pip3 ，`pip3 install -r requirements.txt`