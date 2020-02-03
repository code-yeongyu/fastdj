from article.models import Article
from article.serializers import ArticleSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.AllowAny)

class PostOverall(generics.ListAPIView, APIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)

    def post(self, request):
        if request.user.is_authenticated:
            serializer = ArticleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(writer=request.user)
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
        
@api_view(['GET'])
def my_posts_view(request, ):
    object_to_return = get_object_or_404(Article, writer=request.user).values()
    return Response(ArticleSerializer(object_to_return).data)
@api_view(['GET'])
def user_posts_view(request, username):
    object_to_return = get_object_or_404(Article, writer=username).values()
    return Response(ArticleSerializer(object_to_return).data)
