from rest_framework import serializers
from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    writer = serializers.ReadOnlyField(source='writer.username')
    class Meta:
        model = Article
        fields = ('writer', 'content', 'tag')

