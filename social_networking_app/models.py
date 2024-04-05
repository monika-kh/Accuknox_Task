from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Create a new user with the given email and password
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Create a new superuser with the given email and password
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    # Custom user model extending AbstractUser
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150, blank=True, null=True
    )  # You can keep username field, but it's not mandatory

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class FriendRequest(models.Model):
    # Model to represent friend requests
    from_user = models.ForeignKey(
        CustomUser, related_name="sent_friend_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        CustomUser, related_name="received_friend_requests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def accept(self):
        # Accept the friend request and create a friendship
        self.accepted = True
        self.save()
        # Create a new friend object to represent the friendship
        Friend.objects.create(user=self.from_user, friend=self.to_user)
        Friend.objects.create(user=self.to_user, friend=self.from_user)

    def reject(self):
        # Reject the friend request
        self.delete()


class Friend(models.Model):
    # Model to represent friendships
    user = models.ForeignKey(
        CustomUser, related_name="friends", on_delete=models.CASCADE
    )
    friend = models.ForeignKey(
        CustomUser, related_name="user_friends", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
