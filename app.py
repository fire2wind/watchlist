from flask import Flask,render_template
from flask import url_for
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
#在扩展类实例化前加载配置
db = SQLAlchemy(app)

#创建数据库模型
class User(db.Model): #模板类要声明继承db.Model
	#每一个类属性(字段)要实例化db.Column
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
class Movie(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(60))
	year = db.Column(db.String(4))

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

@app.route('/') 
def index():
	#user = User.query.first()
	movies = Movie.query.all()
	return render_template('index.html', movies=movies)

@app.route('/user/<name>')
def user_page(name):
	return 'User: %s' % name

@app.route('/test')
def test_url_for():
	print(url_for('hello'))
	print(url_for('user_page', name='greyli'))
	print(url_for('user_page', name='peter'))
	print(url_for('test_url_for'))
	print(url_for('test_url_for', num=2))
	return 'Test page'

