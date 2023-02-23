import json
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import fake_useragent


def get_soup(url):
    ua = fake_useragent.UserAgent()
    headers = {'User-agent': ua.random}
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup

def get_news_dict(soup):
    all_articles = soup.findAll('a', class_='article-card inline-card')
    news_dict= {}
    for article in all_articles:
        news_name = article.find('h2', class_='article-card-title').text
        news_description = article.find('p').text
        news_time = article.find('time').get('datetime')
        date_from_iso = datetime.fromisoformat(news_time)
        date_time =datetime.strftime(date_from_iso, '%Y-%m-%d %H:%M:%S')
        news_datetime = time.mktime(datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').timetuple())

        news_url = f'https://www.securitylab.ru{article.get("href")}'
        news_id = news_url.split('/')[-1][:-4]

        news_dict[news_id] = {
            'time': news_datetime,
            'name': news_name,
            'description': news_description,
            'url': news_url
         }
    return news_dict

def write_news_dict(news_dict, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)

def read_news_dict(filename):
    with open(filename, encoding='utf-8') as file:
        news_dict = json.load(file)
    return news_dict

def check_news_update():
    news_dict = read_news_dict('news.json')
    soup = get_soup('https://www.securitylab.ru/news/')
    fresh_dict = {}
    for article in soup.findAll('a', class_='article-card inline-card'):
        news_url = f'https://www.securitylab.ru{article.get("href")}'
        news_id = news_url.split('/')[-1][:-4]


        if news_id in news_dict:
            continue
        else:
            news_name = article.find('h2', class_='article-card-title').text
            news_description = article.find('p').text
            news_time = article.find('time').get('datetime')
            date_from_iso = datetime.fromisoformat(news_time)
            date_time = datetime.strftime(date_from_iso, '%Y-%m-%d %H:%M:%S')
            news_datetime = time.mktime(datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').timetuple())

            fresh_dict[news_id] = {
                'time': news_datetime,
                'name': news_name,
                'description': news_description,
                'url': news_url
            }
    return fresh_dict

def notify_about_news(news_dict, fresh_dict):
    new_news = []
    for news_id in fresh_dict:
        new_news.append(news_dict[news_id])
    for news in new_news:
        print(f'New news: {news["name"]}\nDescription: {news["description"]}\nUrl: {news["url"]}\n')

def main_news():
    soup = get_soup('https://www.securitylab.ru/news/')
    news_dict = get_news_dict(soup)
    write_news_dict(news_dict, 'news.json')
    fresh_dict = check_news_update()
    if fresh_dict:
        notify_about_news(news_dict, fresh_dict)
        news_dict.update(fresh_dict)
        write_news_dict(news_dict, 'news.json')


main_news()
