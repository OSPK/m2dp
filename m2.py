from flask import Flask
from flask import render_template
from flask import jsonify
import urllib, json
import pymongo
import pprint
from flask.ext.cache import Cache

application = Flask(__name__)
conn = pymongo.MongoClient("mongodb://m2user:hailmyas$@localhost/test?authMechanism=SCRAM-SHA-1")
db = conn.test
col = db.news

cache = Cache(application,config={'CACHE_TYPE': 'simple'})

@application.route('/')
@cache.cached(timeout=120)
def index():
	url = ('http://dailypakistan.com.pk/mobile_api/homepage_news_listing/format/json/limit_start/0/num_of_records/20/print_or_digital/digital/news_image_size/small')
	response = urllib.urlopen(url);
	news = json.load(response)

	return render_template('index.html', news=news)

@application.route('/category/<categoryname>/')
def show_category_page(categoryname):
	return 'Category %s' % categoryname

@application.route('/<category>/<date>/<int:news_id>/')
def show_news(category,date,news_id):
	nid = str(news_id)
	mid = None
	exists = False

	news = col.find_one({'news_id': nid})

	if news is not None:
		mid = news.get('_id')

		if "news_title" in news:
			status = "database"

	else:
		url = ('http://dailypakistan.com.pk/mobile_api/news_detail/news_id/%d/format/json/news_image_size/100' % news_id)
		response = urllib.urlopen(url);
		news = json.load(response)

		if "news_title" in news:
			col.insert(news)
			status = "INTERNET"


		else:
			status = news['result']
		
	return render_template('news.html', news=news, category=category, status=status, mid=mid)

@application.route('/<category>/<date>/<int:news_id>/update')
def update_news(category,date,news_id):
	url = ('http://dailypakistan.com.pk/mobile_api/news_detail/news_id/%d/format/json/news_image_size/100' % news_id)
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

	return render_template('news.html', news=news, category=category, status=status)

if __name__ == '__main__':
	application.run(debug=True,host='0.0.0.0')
