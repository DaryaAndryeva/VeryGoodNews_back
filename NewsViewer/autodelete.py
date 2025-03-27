from .models import News, Source
from datetime import datetime, timedelta

def job():
    date =  datetime.now().replace(hours = 0,minute=0, second=0, microsecond=0) - timedelta(days = 7)
    News.objects.filter(publication_date__lt=date).delete()
