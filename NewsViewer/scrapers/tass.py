#'https://tass.ru/'
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
    
    soup = BeautifulSoup(response.text, "html.parser")
    text = " ".join(p.get_text() for p in soup.find_all("p", class_="Paragraph_paragraph__9WAFK"))
    return text


def scrape():
    URL = 'https://tass.ru/tgap/api/v1/messages/?lang=ru&limit=60'
    response = requests.get(URL)

    if response.status_code != 200:
        return []

    data = response.json()['result']
    titles = []
    links = []
    texts = []
    dates = []

    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)

    for item in data:
        title_html = item['body']
        title_soup = BeautifulSoup(title_html, 'html.parser')
        title = title_soup.get_text()
        print(title)
        link = 'https://tass.ru' + item['content_url']
        publication_time = datetime.fromisoformat(item['published_dt']) + timedelta(hours=3)
        if current_hour - publication_time > timedelta(hours=2):
            break
        
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