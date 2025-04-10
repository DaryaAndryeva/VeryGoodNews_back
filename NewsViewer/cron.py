import pytz
from django.utils import timezone
from .models import News, Source
from .scrapers import kp, mn, rg, tass, lenta, mosregtoday, mos_ru

def add_to_db(all_news, source):
    for news in all_news:
        if not News.objects.filter(url = news['link']):
            News.objects.create(
                url = news['link'],
                publication_date = news['date'],
                source = source,
                title = news['title'],
                content = news['text']
            )

def scrape_kp():
    all_news = kp.scrape()
    source, created = Source.objects.get_or_create(name = 'Комсомольская правда', url = 'https://www.msk.kp.ru/online/')
    add_to_db(all_news, source)
    
def scrape_mn():
    all_news = mn.scrape()
    source, created = Source.objects.get_or_create(name = 'Московские новости', url = 'https://www.mn.ru/short')
    add_to_db(all_news, source)

def scrape_tass():
    all_news = tass.scrape()
    source, created = Source.objects.get_or_create(name = 'ТАСС', url = 'https://tass.ru')
    add_to_db(all_news, source)

def scrape_rg():
    all_news = rg.scrape()
    source, created = Source.objects.get_or_create(name = 'Российская газета', url = 'https://rg.ru/news.html')
    add_to_db(all_news, source)

def scrape_lenta():
    all_news = lenta.scrape()
    source, created = Source.objects.get_or_create(name = 'Лента', url = 'https://lenta.ru/parts/news/')
    add_to_db(all_news, source)

def scrape_mosregtoday():
    all_news = mosregtoday.scrape()
    source, created = Source.objects.get_or_create(name = 'Подмосковье Сегодня', url = 'https://mosregtoday.ru/news/')
    add_to_db(all_news, source)

def scrape_mos_ru():
    all_news = mos_ru.scrape()
    source, created = Source.objects.get_or_create(name = 'mos.ru', url = 'https://www.mos.ru/news/')
    add_to_db(all_news, source)
    
def job():
    scrape_kp()
    scrape_mn()
    scrape_tass()
    scrape_rg()
    scrape_lenta()
    scrape_mosregtoday()
    scrape_mos_ru()
    