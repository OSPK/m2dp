import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import urllib, json
import pymongo
import pprint
from flask.ext.cache import Cache
from pyga.requests import Tracker, Page, Session, Visitor

application = Flask(__name__)
conn = pymongo.MongoClient("mongodb://m2:12345@localhost/test?authMechanism=SCRAM-SHA-1")
db = conn.test
col = db.news

#PYGA ANALYTICS START
tracker = Tracker('UA-63492173-1', 'telenornews.pk')
visitor = Visitor()
#visitor.ip_address = 
session = Session()
# page = Page('/path')
# tracker.track_pageview(page, session, visitor)
#PYGA ANALYTCIS STOP

cache = Cache(application,config={'CACHE_TYPE': 'simple'})

ADMINSs = ['waqas@opensource.com.pk']
mail_handler = SMTPHandler('127.0.0.1','server-error@example.com', ADMINSs, 'YourApplication Failed')
mail_handler.setLevel(logging.ERROR)

@application.route('/')
@cache.cached(timeout=120)
def index():
	url = ('http://dailypakistan.com.pk/mobile_api/homepage_news_listing/format/json/limit_start/0/num_of_records/15/print_or_digital/digital/news_image_size/small')
	response = urllib.urlopen(url);
	news = json.load(response)

	#GA Track
	visitor.ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	page = Page('/')
	tracker.track_pageview(page, session, visitor)
	#/GA track

	return render_template('index.html', news=news)

@application.route('/categories/')
def show_category_index():

	#GA Track
	page = Page('/categories/')
	visitor.ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	tracker.track_pageview(page, session, visitor)
	#/GA track
	
	return render_template('categories.html')

@application.route('/category/<categoryname>/')
@cache.cached(timeout=120)
def show_category_page(categoryname):
	url = ('http://dailypakistan.com.pk/mobile_api/category_news_listing/format/json/category_slug/%s/start_limit/0/num_of_records/15/news_image_size/small' % categoryname)
	response = urllib.urlopen(url);
	news = json.load(response)

	#GA Track
	page = Page('/categories/%s' % categoryname)
	visitor.ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	tracker.track_pageview(page, session, visitor)
	#/GA track

	return render_template('index.html', news=news)

@application.route('/<category>/<date>/<int:news_id>/')
@cache.cached(timeout=920)
def show_news(category,date,news_id):
	nid = str(news_id)
	mid = None
	exists = False

	news = col.find_one({'news_id': nid})

	if news is not None:
		mid = news.get('_id')

		if "news_title" in news:
			status = "db"
			titl = news.get('news_title')

	else:
		url = ('http://dailypakistan.com.pk/mobile_api/news_detail/news_id/%d/format/json/news_image_size/medium' % news_id)
		response = urllib.urlopen(url);
		news = json.load(response)

		if "news_title" in news:
			col.insert(news)
			status = "api"
			titl = news.get('news_title')

		else:
			status = news['result']
			titl = "None"


	#GA Track
	page = Page('/c/d/%s' % news_id)
	visitor.ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	tracker.track_pageview(page, session, visitor)
	#/GA track
		
	return render_template('news.html', news=news, category=category, status=status, mid=mid)

@application.route('/<category>/<date>/<int:news_id>/update')
def update_news(category,date,news_id):
	url = ('http://dailypakistan.com.pk/mobile_api/news_detail/news_id/%d/format/json/news_image_size/medium' % news_id)
	response = urllib.urlopen(url);
	news = json.load(response)

	nid = str(news_id)
	old_news = col.find_one({'news_id': nid})

	if old_news is not None:
		mid = old_news.get('_id')

		col.update({'_id':mid}, news, upsert=False)

		status = str(mid) + " updated"

	else:
		status = "This story does not exist"

		if "news_title" in news:
			col.insert(news)
			status = "Story did not exist in database but has been added now"


	# if "news_title" in news:
	# 	status = "FOUND IT"
	# else:
	# 	status = news.get('result')

	#GA Track
	page = Page('/c/d/%s/update' % news_id)
	visitor.ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	tracker.track_pageview(page, session, visitor)
	#/GA track

	return render_template('news.html', news=news, category=category, status=status)

if __name__ == '__main__':
	#handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
	#handler.setLevel(logging.INFO)
	app.logger.addHandler(mail_handler)
	#app.logger.addHandler(handler)
	application.run(debug=True,host='0.0.0.0')
