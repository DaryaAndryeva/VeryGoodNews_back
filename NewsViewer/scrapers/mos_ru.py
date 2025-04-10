#'https://www.mos.ru/news/'

from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from .scrape_utils import TIMEDELTA, LemmatizeText

proxies = {
    "http": "http://9V7JjjNS7T:NaI0U0SY1W@193.168.224.61:25766",
    "https": "http://9V7JjjNS7T:NaI0U0SY1W@193.168.224.61:25766",
}

def GetText(link):
    response = requests.get(link, proxies=proxies)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("section", class_="news-article__text")
    if content:
        text = content.get_text(separator=" ", strip=True)
    return text


def scrape():
    URL = 'https://www.mos.ru/api/newsfeed/v4/frontend/json/ru/articles?expand=spheres&fields=id%2Ctitle%2Clabel%2Cdate%2Cplace%2Cfree%2Cdepartment_id&page=1&per-page=9&sort=-date'
    response = requests.get(URL, proxies=proxies)

    if response.status_code != 200:
        return []

    data = response.json()['items']
    next_page = response.json()['_links']['next']['href']
    titles = []
    links = []
    texts = []
    dates = []

    utc_now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    last_news_date = utc_now

    while (utc_now - last_news_date) < TIMEDELTA:
        for item in data:
            title = item['title']
            link = 'https://www.mos.ru/news/item/' + str(item['id'])
            publication_time = datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S") - timedelta(hours = 3)
            publication_time = publication_time.replace(tzinfo=timezone.utc)

            last_news_date = min(last_news_date, publication_time)
            if utc_now - publication_time > TIMEDELTA:
                break
            text = GetText(link)
            text = LemmatizeText(title + " " + text) 

            # print(title)
            titles.append(title)
            links.append(link)
            dates.append(publication_time)
            texts.append(text)
        
        response = requests.get(next_page)
        if response.status_code != 200:
            return []
        data = response.json()['items']
        next_page = response.json()['_links']['next']['href']

    
    data = [
        {'title': title, 'date': date, 'link': link, 'text': text}
        for title, date, link, text in zip(titles, dates, links, texts)
    ]

    return(data)

# print(scrape())
