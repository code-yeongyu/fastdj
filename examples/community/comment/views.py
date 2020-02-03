from comment.models import Comment
from comment.serializers import CommentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from django.http import JsonResponse


@api_view(['GET'])
def get_comments_view(request, article_pk):
    object_to_return = get_object_or_404(Comment, article_id=article_pk).values()
    return Response(CommentSerializer(object_to_return).data)
class create_comment_view(generics.ListAPIView, APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)

    def post(self, request):
        if request.user.is_authenticated:
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(writer=request.user)
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
        
