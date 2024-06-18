from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from watchlist_app.api import serializers
from watchlist_app import models


class StreamPlatformTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="user1",password="password")
        self.token = Token.objects.get(user__username= self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.stream = models.StreamPlatform.objects.create(
                name =  "testingplatform",
                about = "streaming platform",
                website = "http://testingplatform.com"
            )
    
    def test_streamplatform_create(self):
        data = {
            "name": "testingplatform",
            "about": "streaming platform",
            "website": "http://testingplatform.com"
        }

        response = self.client.post(reverse('streamplatform-list'),data)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        
    def test_streamplatform_list(self):
        response = self.client.get(reverse('streamplatform-list'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    def test_streamplatform_individual_list(self):
        response = self.client.get(reverse('streamplatform-detail',args=(self.stream.id,)))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        
    
    def test_streamplatform_update(self):
        data = {
            "name": "testingplatform - Updated",
            "about": "streaming platform",
            "website": "http://testingplatform.com"
        }
        
        response = self.client.put(reverse('streamplatform-detail',args=(self.stream.id,)),data)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        
class WatchListTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="user1",password="password")
        self.token = Token.objects.get(user__username= self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.stream = models.StreamPlatform.objects.create(
                name =  "testingplatform",
                about = "streaming platform",
                website = "http://testingplatform.com"
            )
        
        self.watchlist = models.Watchlist.objects.create(platform=self.stream,title="testing movie",
                                                         storyline="example move",active=True)
    
    
    def test_watchlist_create(self):
        data = {
            "platfrom":self.stream,
            "title": "testing title",
            "storyline": "good to watch",
            "active": True
        }
        
        response = self.client.post(reverse('movie-list'),data)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        
    def test_watchlist_get(self):
        response = self.client.get(reverse('movie-list'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    def test_watchlist_individual_list(self):
        response = self.client.get(reverse('movie-details',args=(self.watchlist.id,)))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(models.Watchlist.objects.count(), 1)
        self.assertEqual(models.Watchlist.objects.get().title, 'testing movie')


class ReviewTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="user1",password="password")
        self.token = Token.objects.get(user__username= self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.stream = models.StreamPlatform.objects.create(
                name =  "testingplatform",
                about = "streaming platform",
                website = "http://testingplatform.com"
            )
        
        self.watchlist = models.Watchlist.objects.create(platform=self.stream,title="testing movie",
                                                         storyline="example move",active=True)
        self.watchlist2 = models.Watchlist.objects.create(platform=self.stream,title="testing movie",
                                                         storyline="example move",active=True)
        self.review = models.Review.objects.create(review_user = self.user,rating = 5,
                                                   description = "Okay movie",watchlist = self.watchlist2,active = False)
    
    def test_review_create(self):
        data = {
            "review_user" : self.user,
            "rating" : 4,
            "description" : "Must watch movie",
            "watchlist" : self.watchlist,
            "active" : True
        }
        
        response = self.client.post(reverse('review-create',args=(self.watchlist.id,)),data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(models.Review.objects.count(), 2)
        
        response = self.client.post(reverse('review-create',args=(self.watchlist.id,)),data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
    
    def test_review_create_unauth(self):
        data = {
            "review_user" : self.user,
            "rating" : 5,
            "description" : "Okay movie",
            "watchlist" : self.watchlist,
            "active" : True
        }
        
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('review-create',args=(self.watchlist.id,)),data)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
    
    def test_review_update(self):
        data = {
            "review_user" : self.user,
            "rating" : 4,
            "description" : "Okay movie - Updated",
            "watchlist" : self.watchlist,
            "active" : False
        }
    
        # response = self.client.put('/watch/review/'+str(self.review.id)+"/",data)    
        response = self.client.put(reverse('review-detail',args=(self.review.id,)),data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    def test_review_list(self):
        response = self.client.get(reverse('review-list',args=(self.watchlist.id,)))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        
    def test_review_list_individual(self):
        # response = self.client.get('/watch/review/' + str(self.review.id) + "/")
        response = self.client.get(reverse('review-detail',args=(self.review.id,)))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    def test_user_reviews(self):
        response = self.client.get('/watch/reviews/?username='+self.user.username)
        self.assertEqual(response.status_code,status.HTTP_200_OK)