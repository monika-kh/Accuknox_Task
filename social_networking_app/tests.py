from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import NoReverseMatch
from django.contrib.auth import get_user_model
from social_networking_app.models import FriendRequest, Friend

CustomUser = get_user_model()

class TestURLs(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(email='user121@example.com', password='password')
        self.user2 = CustomUser.objects.create_user(email='user222@example.com', password='password')
        self.friend_request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.friend = Friend.objects.create(user=self.user1, friend=self.user2)

    def test_friend_list_url(self):
        try:
            url = reverse('friend-list')
            self.client.force_authenticate(user=self.user1)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Add more assertions as needed
        except NoReverseMatch as e:
            self.fail(f"Reversing URL failed with error: {e}")

    def test_friend_requests_url(self):
        try:
            url = reverse('friend-requests')
            data = {'to_user': self.user2.email}  # Provide valid data for friend request creation
            self.client.force_authenticate(user=self.user1)
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Update expected status code
            # Add more assertions as needed
        except NoReverseMatch as e:
            self.fail(f"Reversing URL failed with error: {e}")

    def test_user_search_url(self):
        try:
            url = reverse('user-search')
            data = {'q': 'use'}  # Provide search keyword
            self.client.force_authenticate(user=self.user1)
            response = self.client.get(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Write more test methods for other URLs...
        except NoReverseMatch as e:
            self.fail(f"Reversing URL failed with error: {e}")

    def test_list_pending_requests_url(self):
        try:
            url = reverse('list-pending-requests')
            self.client.force_authenticate(user=self.user2)
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Add more assertions as needed
        except NoReverseMatch as e:
            self.fail(f"Reversing URL failed with error: {e}")
