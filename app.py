from flask import Flask,render_template
from flask import url_for,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

WIN = sys.platform.startswith('win')
if WIN: #是否Windows系统
	prefix = 'sqlite:///'
else:
	prefix = 'sqlite:////'

app = Flask(__name__) #创建一个Flask对象

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev' #设置签名所需的密钥
#在扩展类实例化前加载配置
db = SQLAlchemy(app)

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import login_required, logout_user
from flask_login import login_user, current_user
class User(db.Model, UserMixin): 
	#每一个类属性(字段)要实例化db.Column
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	username = db.Column(db.String(20))
	password_hash = db.Column(db.String(128)) #密码散列

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	
	def validate_password(self, password):
		return check_password_hash(self.password_hash, password)

class Movie(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(60))
	year = db.Column(db.String(4))

from flask_login import LoginManager
login_manager = LoginManager(app) #实例化扩展类
login_manager.login_view = 'login' #登录示图端点
@login_manager.user_loader
#创建用户加载回调函数，接收用户ID作为参数
def load_user(user_id):
	user = User.query.get(int(user_id))
	return user
#自定义命令admin，创建管理员
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login')
@click.option('--password', prompt=True, hide_input=True,\
	confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
	"""Create user."""
	db.create_all()
	user = User.query.first()
	if user is not None:
		click.echo('Updating user...')
		user.username = username
		user.set_password(password)
	else:
		click.echo('Creating user...')
		user = User(username=username, name ='Admin')
		user.set_password(password)
		db.session.add(user)
	db.session.commit()
	click.echo('Done')

#自定义命令initdb
@app.cli.command() #注册为命令
@click.option('--drop',is_flag=True,help='Create after drop.') #设置选项
def initdb(drop):
	"""Initialize the database"""
	if drop:
		db.drop_all()
	db.create_all()
	click.echo('Initialized database')

#自定义命令forge
@app.cli.command()
def forge():
	"""Generate fake data"""
	db.create_all()
	name = 'Luo' 
	movies = [ 
		{'title': 'My Neighbor Totoro', 'year': '1988'}, 
		{'title': 'Dead Poets Society', 'year': '1989'}, 
		{'title': 'A Perfect World', 'year': '1993'}, 
		{'title': 'Leon', 'year': '1994'}, 
		{'title': 'Mahjong', 'year': '1996'}, 
		{'title': 'Swallowtail Butterfly', 'year': '1996'}, 
		{'title': 'King of Comedy', 'year': '1999'},
		{'title': 'Devils on the Doorstep', 'year': '1999'}, 
		{'title': 'WALL-E', 'year': '2008'}, 
		{'title': 'The Pork of Music', 'year': '2012'}, 
	]
	user = User(name=name)
	db.session.add(user)
	for m in movies:
		movie = Movie(title=m['title'],year=m['year'])
		db.session.add(movie)
	db.session.commit()
	click.echo('Done')

#模板上下文处理函数，处理多个模板内都需要使用的变量
#减少重复代码
@app.context_processor
def inject_user():
	user = User.query.first()
	return dict(user=user)
#404错误处理函数
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.route('/', methods=['GET','POST']) 
def index():
	if request.method == 'POST':
		if not current_user.is_authenticated: #用户未认证
			return redirect(url_for('index'))
		#获取表单数据, request.form是一个字典
		title = request.form.get('title')
		year = request.form.get('year')
		#服务端验证数据
		if not title or not year or len(year) > 4 or len(title) > 60:
			flash('Invalid input.') #显示错误提示
			return redirect(url_for('index')) #重定向回主页
		#保存表单数据到数据库
		movie = Movie(title=title, year=year) #创建记录
		db.session.add(movie)
		db.session.commit()
		flash('Item created.') #显示成功创建的提示
		return redirect(url_for('index')) #重定向回主页
	user = User.query.first()
	movies = Movie.query.all()
	return render_template('index.html', user=user,movies=movies)

@app.route('/user/<name>')
def user_page(name):
	return 'User: %s' % name

#编辑电影条目
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required #登录保护
def edit(movie_id):
	movie = Movie.query.get_or_404(movie_id)
	if request.method == 'POST':
		title = request.form.get('title')
		year = request.form.get('year')
		#服务端验证数据
		if not title or not year or len(year) > 4 or len(title) > 60:
			flash('Invalid input.') #显示错误提示
			return redirect(url_for('edit',movie_id=movie_id)) #重定回对应的编辑页面
		#保存表单数据到数据库
		movie.title = title
		movie.year = year
		db.session.commit()
		flash('Item updated.')
		return redirect(url_for('index')) #重定向回主页
	return render_template('edit.html', movie=movie) #传入被编辑的电影记录

#删除电影条目
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required #登录保护
def delete(movie_id):
	movie = Movie.query.get_or_404(movie_id)
	db.session.delete(movie)
	db.session.commit()
	flash('Item deleted')
	return redirect(url_for('index'))

#用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if not username or not password:
			flash('Invalid input.')
			return redirect(url_for('login'))
		
		user = User.query.first()
		#验证用户名和密码
		if username == user.username and user.validate_password(password):
			login_user(user)
			flash('Login success')
			return redirect(url_for('index'))
		flash('Invalid username or password')
		return redirect(url_for('login'))
	return render_template('login.html')

#登出
@app.route('/logout')
@login_required #用于视图保护
def logout():
	logout_user()
	flash('Goodbye')
	return redirect(url_for('index'))

#设置用户名
@app.route('/settings', methods=['GET','POST'])
@login_required
def settings():
	if request.method == 'POST':
		name = request.form['name']
		if not name or len(name) > 20:
			flash('Invalid input.')
			return redirect(url_for('settings'))
		current_user.name = name
		db.session.commit()
		flash('Settings updated.')
		return redirect(url_for('index'))
	return render_template('settings.html')


