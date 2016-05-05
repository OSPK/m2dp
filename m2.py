from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import json
import requests
from flask.ext.cache import Cache
from gevent.wsgi import WSGIServer

application = Flask(__name__)
app = application

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'fcache',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_URL': 'redis://localhost:6379'
    })
#CACHE_REDIS_URL = "redis://linus@localhost:6379/"

@application.route('/')
@cache.cached(timeout=120)
def index():
	url = 'http://dailypakistan.com.pk/mobile_api/homepage_news_listing/format/json/limit_start/0/num_of_records/15/print_or_digital/digital/news_image_size/small'
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	response = requests.get(url, headers=headers)
	news = response.json()
	return render_template('index.html', news=news)

@application.route('/categories/')
@cache.cached(timeout=1200)
def show_category_index():
	
	return render_template('categories.html')

@application.route('/category/<categoryname>/')
@cache.cached(timeout=120)
def show_category_page(categoryname):
	url = ('http://dailypakistan.com.pk/mobile_api/category_news_listing/format/json/category_slug/%s/start_limit/0/num_of_records/15/news_image_size/small' % categoryname)
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	response = requests.get(url, headers=headers)
	news = response.json()

	return render_template('index.html', news=news)

@application.route('/<category>/<date>/<int:news_id>/')
@cache.cached(timeout=1200000)
def show_news(category,date,news_id):
	nid = str(news_id)
	mid = None
	exists = False

	url = ('http://dailypakistan.com.pk/mobile_api/news_detail/news_id/%d/format/json/news_image_size/medium' % news_id)
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	response = requests.get(url, headers=headers)
	news = response.json()

	if "news_title" in news:
		#col.insert(news)
		status = "api"
		titl = news.get('news_title')

	else:
		status = news['result']
		titl = "None"
		
	return render_template('news.html', news=news, category=category, status=status, mid=mid)

@application.route('/<category>/<date>/<int:news_id>/update')
def update_news(category,date,news_id):
	url = ('http://dailypakistan.com.pk/mobile_api/news_detail/news_id/%d/format/json/news_image_size/medium' % news_id)
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	response = requests.get(url, headers=headers)
	news = response.json()

	return render_template('news.html', news=news)

if __name__ == '__main__':
	application.run(debug=True,host='0.0.0.0')

# http_server = WSGIServer(('', 8080), app)
# http_server.serve_forever()

