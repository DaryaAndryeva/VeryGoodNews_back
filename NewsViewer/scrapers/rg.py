# 'https://rg.ru/news.html'
# DONE
from datetime import datetime, timedelta
import time
import requests
import json
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
    soup = BeautifulSoup(response.text, 'html.parser')

    lead = soup.find("div", class_="PageArticleContent_lead__l9TkG")
    text = lead.get_text(" ", strip=True) if lead else ""
    news_content = soup.find("div", class_="PageContentCommonStyling_text__CKOzO")
    text = text + "\n\n".join(p.get_text(strip=True) for p in news_content.find_all("p"))
    return text

def scrape(): 
    cur_time = int(time.time())
    URL = 'https://apifilter.rg.ru/filter?query=%7B%22news%22:%7B%22size%22:10,%22priority%22:100,%22is_news%22:true,%22tag%22:%7B%22slug%22:%22stranicanovostey%22%7D,%22source_type%22:%22article%22,%22fields%22:[%22id%22,%22custom_fields%22,%22url%22,%22label%22,%22title%22,%22link_title%22,%22is_title_priority%22,%22sub_title%22,%22alternate_title%22,%22sub_title_as_link_title%22,%22is_adv%22,%22publish_at%22,%22kind%22,%22source_type%22,%22is_sport%22,%22is_rodina%22],%22offset%22:'
    response = requests.get(URL + str(cur_time) + '%7D%7D')
    
    if response.status_code != 200:
        return []
    data = response.json()['news']['hits']

    titles = []
    links = []
    texts = []
    dates = []

    today_midnight = datetime.now().replace(minute=0, second=0, microsecond=0)
    last_news_date = today_midnight

    while (today_midnight - last_news_date) < timedelta(hours=2):
        for item in data:
            title = item['_source']['link_title']
            link = 'https://rg.ru' + item['_source']['url']
            publication_time = datetime.fromtimestamp(item['_source']['publish_at'])
            text = LemmatizeText(title + " " + GetText(link))

            last_news_date = min(last_news_date, publication_time)
            if today_midnight - publication_time > timedelta(hours=2):
                break

            titles.append(title)
            links.append(link)
            dates.append(publication_time)
            texts.append(text)
        
        response = requests.get(URL + str(int(last_news_date.timestamp())) + '%7D%7D')
        if response.status_code != 200:
            return []
        data = response.json()['news']['hits']
    
    data = [
        {'title': title, 'date': date, 'link': link, 'text': text}
        for title, date, link, text in zip(titles, dates, links, texts)
    ]

    return(data)

# print(scrape())
