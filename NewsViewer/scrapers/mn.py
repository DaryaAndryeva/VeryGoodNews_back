#'https://www.mn.ru/short'

from datetime import datetime, timedelta, timezone
import requests
from .scrape_utils import TIMEDELTA, LemmatizeText


def scrape():
    URL = 'https://www.mn.ru/api/v1/articles/categories/short/more?page=1&page_size=20'
    response = requests.get(URL)

    if response.status_code != 200:
        return []

    data = response.json()['data']
    next_page = 'https://www.mn.ru' + response.json()['links']['next']
    titles = []
    links = []
    texts = []
    dates = []

    utc_now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    last_news_date = utc_now

    while (utc_now - last_news_date) < TIMEDELTA:
        for item in data:
            title = item['attributes']['title']
            link = item['attributes']['url']
            publication_time = datetime.strptime(item['attributes']['published_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            publication_time = publication_time.replace(tzinfo=timezone.utc)


            text = LemmatizeText(title + " " + item['attributes']['content']) 

            last_news_date = min(last_news_date, publication_time)
            if utc_now - publication_time > TIMEDELTA:
                break

            titles.append(title)
            links.append(link)
            dates.append(publication_time)
            texts.append(text)
        
        response = requests.get(next_page)
        if response.status_code != 200:
            return []
        data = response.json()['data']
        next_page = 'https://www.mn.ru' + response.json()['links']['next']
    
    data = [
        {'title': title, 'date': date, 'link': link, 'text': text}
        for title, date, link, text in zip(titles, dates, links, texts)
    ]

    return(data)

# print(scrape())
