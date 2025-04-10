#'https://www.msk.kp.ru/online/'

from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from .scrape_utils import TIMEDELTA, LemmatizeText

def GetText(id):
    link = 'https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json?pages.direction=page&pages.target.class=10&pages.target.id=' + str(id)
    response = requests.get(link)
    if response.status_code != 200:
        return []
    data = response.json()['childs'][0]['childs']
    text = ''
    for item in data:
        if not 'ru' in item:
            continue
        if not 'text' in item['ru']:
            continue
        text += str(item['ru']['text'])
    return text


def scrape():
    year = datetime.now().year
    month = datetime.now().month
    URL = 'https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json?pages.age.month=' + str(month) + '&pages.age.year=' + str(year) + '&pages.direction=page&pages.number=100&pages.target.class=100&pages.target.id=1'
    response = requests.get(URL)

    if response.status_code != 200:
        return []

    data = response.json()['childs']
    titles = []
    links = []
    texts = []
    dates = []

    utc_now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    for item in data:
        title = item['ru']['title']
        link = 'https://www.msk.kp.ru/online/news/' + str(item['@id'])
        publication_time = next((cur['value'] for cur in item['meta'] if cur['name'] == 'published'), None)
        publication_time = datetime.fromisoformat(publication_time) - timedelta(hours = 3)
        publication_time = publication_time.replace(tzinfo=timezone.utc)


        if utc_now - publication_time > TIMEDELTA:
            break
        
        text = LemmatizeText(title + " " + GetText(item['@id']))

        titles.append(title)
        links.append(link)
        dates.append(publication_time)
        texts.append(text)
       

    data = [
        {'title': title, 'date': date, 'link': link, 'text': text}
        for title, date, link, text in zip(titles, dates, links, texts)
    ]

    return(data)
        
# print(scrape())