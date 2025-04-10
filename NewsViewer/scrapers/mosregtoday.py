#'https://mosregtoday.ru/news/'

from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab, Doc

segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab()

def LemmatizeText(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    return " ".join([token.lemma if token.lemma else token.text for token in doc.tokens])

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

DELTA = timedelta(hours=2)

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

    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    last_news_date = current_hour

    while current_hour - last_news_date < DELTA:
        response = requests.get(URL + str(page))
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        page += 1

        for article in soup.select('a > article'):
            title_tag = article.find('h2')
            title = title_tag.text.strip()
            link_tag = article.find_parent('a')
            link = link_tag['href']
            time_tag = article.find('time')
            publication_time =  datetime.strptime(time_tag['datetime'], '%Y-%m-%dT%H:%M%z')
            publication_time = publication_time.replace(tzinfo=None)
            last_news_date = publication_time

            if (current_hour - publication_time > DELTA):
                break

            text =  GetText('https://mosregtoday.ru' + link)
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

