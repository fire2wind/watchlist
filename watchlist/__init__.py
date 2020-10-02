import os
import sys

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager

WIN = sys.platform.startswith('win')
if WIN: #是否Windows系统
	prefix = 'sqlite:///'
else:
	prefix = 'sqlite:////'

app = Flask(__name__) #创建一个Flask对象
#os.getenv: 读取系统环境变量，否则为默认值
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','dev') 
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),os.getenv('DATABASE_FILE','data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控

db = SQLAlchemy(app) #在扩展类实例化前加载配置
login_manager = LoginManager(app)


#创建用户加载回调函数，接收用户ID作为参数
@login_manager.user_loader
def load_user(user_id):
	#类内导入，避免循环依赖
	from watchlist.models import User 
	user = User.query.get(int(user_id))
	return user

login_manager.login_view = 'login'

#模板上下文处理函数，处理多个模板内都需要使用的变量，减少重复代码
@app.context_processor
def inject_user():
	from watchlist.models import User
	user = User.query.first()
	return dict(user=user)

from watchlist import views, errors, commands
