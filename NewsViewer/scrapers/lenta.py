'https://lenta.ru/parts/news/'
#DONE
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
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    content = [p.text for p in soup.find_all('p', class_='topic-body__content-text')]
    text = ''
    for block in content:
        text += block
    return text


def scrape():
    URL = "https://api.lenta.ru/v4-alfa/topics/all?limit=80&filter[type]=Topic::News"
    response = requests.get(URL)

    if response.status_code != 200:
        return []

    data = response.json()['topics']
    titles = []
    links = []
    texts = []
    dates = []

    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)

    for item in data:
        title = item['headline']['info']['title']
        link = item['headline']['links']['public']
        publication_time = datetime.fromtimestamp(item['headline']['info']['modified_at'])
        
        if current_hour - publication_time > timedelta(hours=2):
            break
        if not link.startswith('https://lenta.ru'):
            continue
        
        text = LemmatizeText(title + " " + GetText(link))

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