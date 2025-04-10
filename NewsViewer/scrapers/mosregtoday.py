#'https://mosregtoday.ru/news/'

from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from .scrape_utils import TIMEDELTA, LemmatizeText


def GetText(link):
    response = requests.get(link)
    if response.status_code != 200:
        return ''
    
    soup = BeautifulSoup(response.text, "html.parser")
    text = ''
    for p in soup.select("p._1t0safb7"):
        part = p.get_text(strip=True)
        if part:
            text += part
    return text


def scrape():
    URL = 'https://mosregtoday.ru/news/page/' 
    page = 1
    response = requests.get(URL + str(page))

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    titles = []
    links = []
    texts = []
    dates = []

    utc_now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    last_news_date = utc_now

    while utc_now - last_news_date < TIMEDELTA:
        response = requests.get(URL + str(page))
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        page += 1

        for article in soup.select('a > article'):
            title_tag = article.find('h2')
            title = title_tag.text.strip()
            title = title.replace('\xa0', ' ')
            link_tag = article.find_parent('a')
            link = 'https://mosregtoday.ru' + link_tag['href']
            time_tag = article.find('time')
            publication_time =  datetime.strptime(time_tag['datetime'], '%Y-%m-%dT%H:%M%z') - timedelta(hours = 3)
            publication_time = publication_time.replace(tzinfo=timezone.utc)
            last_news_date = publication_time

            if (utc_now - publication_time > TIMEDELTA):
                break

            text =  GetText(link)
            text = LemmatizeText(title + text)

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

