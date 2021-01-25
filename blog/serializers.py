from rest_framework import serializers
from blog.models import Post


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'status', 'content', 'title', 'author', 'category', 'image', 'date')
