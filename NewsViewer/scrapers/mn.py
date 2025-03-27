#'https://www.mn.ru/short'
#DONE
from datetime import datetime, timedelta
import requests
import json
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

    today_midnight = datetime.now().replace(minute=0, second=0, microsecond=0)
    last_news_date = today_midnight

    while (today_midnight - last_news_date) < timedelta(hours = 2):
        for item in data:
            title = item['attributes']['title']
            link = item['attributes']['url']
            publication_time = datetime.strptime(item['attributes']['published_at'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours = 3)
            text = LemmatizeText(title + " " + item['attributes']['content']) #-- текст новости в формате html

            last_news_date = min(last_news_date, publication_time)
            if today_midnight - publication_time > timedelta(hours=2):
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
