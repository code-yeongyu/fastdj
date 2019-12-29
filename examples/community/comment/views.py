from rest_framework.decorators import api_view
from comment.serializers import CommentSerializer
from rest_framework.response import Response
from comment.models import Comment
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def get_comments_view(request, article_pk):
    object_to_return = get_object_or_404(Comment, article_id=article_pk).values()
    return Response(object_to_return)
