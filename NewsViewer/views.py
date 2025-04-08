from django.shortcuts import render

# Create your views here.
from rest_framework import generics, viewsets
from .models import News, Source
from .serializers import NewsSerializer, SourceSerializer
from django.db.models import Value, Case, When, IntegerField, Q
from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab, Doc
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab() 



class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    queryset = News.objects.all()

    def get_queryset(self):
        filtered_queryset = self.queryset

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        keyword = self.request.query_params.get('keyword')
        source_ids = self.request.query_params.get('source')

        if start_date:
            filtered_queryset = filtered_queryset.filter(publication_date__gte=start_date)

        if end_date:
            filtered_queryset = filtered_queryset.filter(publication_date__lte=end_date)

        if source_ids:
            source_id_list = [int(id.strip()) for id in source_ids.split(',') if id.strip().isdigit()]
            filtered_queryset = filtered_queryset.filter(source__id__in=source_id_list)
        
        if keyword:
            text = keyword
            doc = Doc(text)
            doc.segment(segmenter) 
            doc.tag_morph(morph_tagger)

            for token in doc.tokens:
                token.lemmatize(morph_vocab)  

            keyword = " ".join([token.lemma if token.lemma else token.text for token in doc.tokens])

            regex_pattern = r'\b{}\b'.format(keyword)
            filtered_queryset = filtered_queryset.annotate(
                relevance=Case(
                    When(content__iregex=regex_pattern, then=Value(2)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).filter(relevance__gt=0).order_by('-relevance', 'source__name')
        else:
            filtered_queryset = filtered_queryset.order_by('-publication_date')

        return filtered_queryset


class SourceViewSet(viewsets.ModelViewSet):
    serializer_class = SourceSerializer
    queryset = Source.objects.all()