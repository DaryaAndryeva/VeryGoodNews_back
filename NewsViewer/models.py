from django.db import models


class Source(models.Model):
    name = models.CharField(max_length = 200, verbose_name = "Name of the source")
    url = models.URLField(verbose_name = "link to the sourse", unique = True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Source"
        verbose_name_plural = "Sources"

class News(models.Model):
    title = models.CharField(max_length = 200, verbose_name = "Title of the news")
    content = models.TextField(verbose_name = "Content of the news", default = "")
    publication_date = models.DateTimeField(verbose_name = "publication date")
    source = models.ForeignKey(Source, on_delete = models.CASCADE, related_name = "news", verbose_name = "source")
    url = models.URLField(verbose_name = "link to the news", unique = True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"