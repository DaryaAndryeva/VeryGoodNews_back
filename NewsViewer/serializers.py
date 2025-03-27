from rest_framework import serializers
from .models import News, Source

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'