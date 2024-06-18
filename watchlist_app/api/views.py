from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle,ScopedRateThrottle

from watchlist_app.api.permissions import IsAdminOrReadOnly,IsReviewUserOrReadOnly

# from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import generics
# from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import viewsets

from watchlist_app.models import Watchlist,StreamPlatform,Review
from watchlist_app.api.serializers import (WatchlistSerializer,StreamPlatformSerializer,ReviewSerializer)

from watchlist_app.api.throttling import ReviewCreateThrottle,ReviewListThrottle

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from watchlist_app.api.pagination import WatchListPagination,WatchListLOPagination,WatchListCPagination

class UserReview(generics.ListAPIView):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        username = self.request.query_params.get('username',None)
        if username is not None:
            return Review.objects.filter(review_user__username=username)
        
        return username
    
    # def get_queryset(self):
    #     username = self.kwargs['username']
    #     return Review.objects.filter(review_user__username=username)

# Generic class-based views
class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]
    # throttle_classes = [ReviewListThrottle,AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']
    
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewCreateThrottle,AnonRateThrottle]
    
    def get_queryset(self):
        return Review.objects.all()
    
    def perform_create(self,serializer):
        pk = self.kwargs.get('pk')
        watchlist = Watchlist.objects.get(pk=pk)
        
        review_user = self.request.user 
        review_queryset = Review.objects.filter(watchlist=watchlist,review_user=review_user)
        
        if review_queryset.exists():
            raise ValidationError("You have already reviewed this movie!")
        
        
        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else:
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating'])/2
        
        watchlist.number_rating = watchlist.number_rating + 1
        watchlist.save()    
        
        serializer.save(watchlist=watchlist,review_user=review_user)
        
    
class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]
    # throttle_classes = [UserRateThrottle,AnonRateThrottle]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'




# Using Mixins
# class ReviewDetails(mixins.RetrieveModelMixin,generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

# class ReviewList(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


# ReadOnlyModelViewSet
class StreamPlatformVS(viewsets.ModelViewSet):
    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer
    permission_classes = [IsAdminOrReadOnly]


# Model ViewSet
# class StreamPlatformVS(viewsets.ModelViewSet):
#     queryset = StreamPlatform.objects.all()
#     serializer_class = StreamPlatformSerializer
    
    
    
# ViewSet 
# class StreamPlatformVS(viewsets.ViewSet):
    
#     def list(self,request):
#         queryset = StreamPlatform.objects.all()
#         serializer = StreamPlatformSerializer(queryset,many=True)
#         return Response(serializer.data)
    
#     def retrieve(self, request, pk=None):
#         queryset = StreamPlatform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlatformSerializer(watchlist)
#         return Response(serializer.data)
    
#     def create(self,request):
#         serializer = StreamPlatformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)
        
#     def destroy(self,request,pk):
#         platform = StreamPlatform.objects.get(pk=pk)
#         platform.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
        
        

class StreamPlatformAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self,request):
        platform = StreamPlatform.objects.all()
        serializer = StreamPlatformSerializer(platform,many=True)
        return Response(serializer.data)
    
    
    def post(self,request):
        serializer = StreamPlatformSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

class StreamPlatformDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self,request,pk):
        try:
            platform = StreamPlatform.objects.get(pk=pk)
        except StreamPlatform.DoesNotExist:
            return Response({'Error':'Not found'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = StreamPlatformSerializer(platform)
        return Response(serializer.data)
    
    def put(self,request,pk):
        platform = StreamPlatform.objects.get(pk=pk)
        serializer = StreamPlatformSerializer(platform,data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)


    def delete(self,request,pk):
        platform = StreamPlatform.objects.get(pk=pk)
        platform.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchListGV(generics.ListAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    pagination_class = WatchListCPagination
    
    
    # filter_backends = [filters.OrderingFilter]
    # ordering_fields = ['avg_rating']
    
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['title', 'platform__name']
    
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['title', 'platform__name']


class WatchListAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self,request):
        movies = Watchlist.objects.all()
        serializer = WatchlistSerializer(movies,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        


class WatchDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self,request,pk):
        try:
            movie = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response({'Error':'Not found'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = WatchlistSerializer(movie)
        return Response(serializer.data)
    
    def put(self,request,pk):
        movie = Watchlist.objects.get(pk=pk)
        serializer = WatchlistSerializer(movie,data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
        
    def delete(self,request,pk):
        movie = Watchlist.objects.get(pk=pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        
        
    














































# @api_view(['GET','POST'])
# def movie_list(request):
#     if request.method == 'GET':
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies,many=True)
#         return Response(serializer.data)
    
#     if request.method == 'POST':
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)

# @api_view(['GET','PUT','DELETE'])
# def movie_details(request,pk):
#     if request.method == 'GET':
        
#         try:
#             movie = Movie.objects.get(pk=pk)
#         except Movie.DoesNotExist:
#             return Response({'Error':'Movie not found'},status=status.HTTP_404_NOT_FOUND) 
           
#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)
    
#     if request.method == 'PUT':
#         movie = Movie.objects.get(pk=pk)
#         serializer = MovieSerializer(movie,data=request.data)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
#     if request.method == 'DELETE':
#         movie = Movie.objects.get(pk=pk)
#         movie.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)