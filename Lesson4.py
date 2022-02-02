from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36'}

client = MongoClient('127.0.0.1', 27017)
db = client['news_db']
news_collection = db.news_collection
news_collection.drop()


def mailru_news():
    url = 'https://news.mail.ru/'
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    news_list = []

    top_news = dom.xpath('//tr/td/div/a/@href')
    list_news = dom.xpath('//ul/li/a/@href')
    news = set(top_news)
    news.update(set(list_news))
    for url in news:
        response = requests.get(url, headers=headers)
        dom = html.fromstring(response.text)
        news_el = dom.xpath('//div[contains(@class, "js-article")]')[0]
        date = news_el.xpath('.//span[@datetime]/@datetime')[0][:10].replace('-', '.')
        source = news_el.xpath('.//a/span/text()')[0]
        title = news_el.xpath('.//h1/text()')[0]
        news_list.append({
            'title': title,
            'date': date,
            'source': source,
            'url': url
        })
        try:
            news_collection.insert_one({
                'title': title,
                'date': date,
                'source': source,
                'url': url
            })
        except:
            pass

    return news_list

if __name__ == '__main__':
    mailru_news()
    for doc in news_collection.find({}):
        pprint(doc)