from flask import Flask
from flask import url_for
app = Flask(__name__) #创建一个Flask对象

#注册处理函数，app.route()装饰器为这个函数绑定对应的URL
#把'/'理解为地址，请求http://127.0.0.1:5000时就会调用hello()
@app.route('/') 
def hello():
	return '<h1>Hello</h1>'

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

