from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser, Friend, FriendRequest


class UserSignupSerializer(serializers.ModelSerializer):
    # Serializer for user signup
    class Meta:
        model = CustomUser
        fields = ["email", "password"]




class FriendRequestSerializer(serializers.ModelSerializer):
    # Serializer for friend requests
    to_user = serializers.EmailField()

    class Meta:
        model = FriendRequest
        fields = ["to_user"]


class FriendSerializer(serializers.ModelSerializer):
    # Serializer for friends
    class Meta:
        model = Friend
        fields = "__all__"
