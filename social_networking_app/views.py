import logging
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser, Friend, FriendRequest
from .serializers import (
    FriendRequestSerializer,
    FriendSerializer,
    UserSignupSerializer
)
from .throttles import FriendRequestThrottle
import sentry_sdk
from rest_framework import filters
from django.db.models import Q

# Get an instance of a logger
logger = logging.getLogger(__name__)



class FriendRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for managing friend requests.
    """

    permission_classes = [
        IsAuthenticated
    ]  # Ensure user is authenticated to access this endpoint
    throttle_classes = [FriendRequestThrottle]

    def create(self, request):
        """
        Handle POST request for creating friend requests.
        """
        try:
            logger.info("Friend request creation request received")  # Log an info message
            serializer = FriendRequestSerializer(data=request.data)
            if serializer.is_valid():
                to_email = serializer.validated_data.get("to_user")
                try:
                    to_user = CustomUser.objects.get(email=to_email)
                except CustomUser.DoesNotExist:
                    logger.error(
                        f"User with email {to_email} does not exist."
                    )  # Log an error message
                    return Response(
                        {"error": f"User with email {to_email} does not exist."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if to_user == request.user:
                    logger.warning(
                        "User attempted to send a friend request to themselves"
                    )  # Log a warning message
                    return Response(
                        {"error": "You cannot send a friend request to yourself."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                existing_request_to_user = FriendRequest.objects.filter(
                    from_user=to_user, to_user=request.user
                ).exists()
                if existing_request_to_user:
                    logger.warning(
                        "User attempted to send a friend request to a user who has already sent them a request"
                    )  # Log a warning message
                    return Response(
                        {"error": "You cannot send a friend request to someone who has already sent you a request."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                existing_request_from_user = FriendRequest.objects.filter(
                    from_user=request.user, to_user=to_user
                ).exists()
                if existing_request_from_user:
                    logger.warning(
                        "User attempted to send a duplicate friend request"
                    )  # Log a warning message
                    return Response(
                        {"error": "You have already sent a friend request to this user."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                FriendRequest.objects.create(from_user=request.user, to_user=to_user)
                logger.info("Friend request sent successfully")  # Log an info message
                return Response(
                    {"message": "Friend request sent successfully."},
                    status=status.HTTP_201_CREATED,
                )
            logger.error(
                "Invalid data provided for friend request creation"
            )  # Log an error message
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
class FriendRequestStatus(viewsets.ViewSet):
    """
    ViewSet for managing friend request status (accept, reject, list pending requests).
    """

    def accept(self, request, pk):

        # Handle accepting a friend request.
        try:
            friend_request = self.get_friend_request(pk)
        except FriendRequest.DoesNotExist:
            logger.error("Friend request not found")  # Log an error message
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Ensure that the request recipient is the current user
            if friend_request.to_user != request.user:
                raise PermissionDenied("You are not authorized to perform this action.")
            elif friend_request.accepted:
                # If the friend request is already accepted, return an error
                logger.warning(
                    "Attempted to accept already accepted friend request"
                )  # Log a warning message
                return Response(
                    {"error": "This friend request has already been accepted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                # Accept the friend request and delete it
                friend_request.accept()
                friend_request.delete()
                logger.info(
                    "Friend request accepted successfully"
                )  # Log an info message
        except AttributeError as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            logger.error(
                "Failed to process friend request acceptance"
            )  # Log an error message
            return Response(
                {"error": "Failed to process friend request acceptance"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"detail": "Friend request Accepted successfully."})

    def reject(self, request, pk):

        # Handle rejecting a friend request.
        try:
            friend_request = self.get_friend_request(pk)
        except FriendRequest.DoesNotExist:
            logger.error("Friend request not found")  # Log an error message
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Ensure that the request recipient is the current user
            if friend_request.to_user != request.user:
                raise PermissionDenied("You are not authorized to perform this action.")
            elif friend_request.accepted:
                # If the friend request is already accepted, return an error
                logger.warning(
                    "Attempted to reject already accepted friend request"
                )  # Log a warning message
                return Response(
                    {"error": "This friend request has already been accepted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                # Reject the friend request
                friend_request.reject()
                logger.info(
                    "Friend request rejected successfully"
                )  # Log an info message
        except AttributeError as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            logger.error(
                "Failed to process friend request rejection"
            )  # Log an error message
            return Response(
                {"error": "Failed to process friend request rejection"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"detail": "Friend request rejected successfully."})

    def get_friend_request(self, pk):

        # Retrieve a friend request by its ID.
        try:
            return FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            logger.error("Friend request not found")  # Log an error message
            return None

    def list_pending_requests(self, request):

        # List pending friend requests for the current user.
        friend_requests = FriendRequest.objects.filter(
            to_user=request.user, accepted=False
        )
        friend_requests_with_emails = []
        for request in friend_requests:
            from_user_email = request.from_user.email
            friend_requests_with_emails.append({"from_user_email": from_user_email})
        return Response(friend_requests_with_emails, status=status.HTTP_200_OK)


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class to handle paginated responses.
    """

    page_size = 10  # Specify the number of items per page
    page_size_query_param = "page_size"
    max_page_size = 1000  # Optionally specify the maximum page size

    def get_paginated_response(self, data):
        """
        Generate paginated response.
        """
        try:
            logger.debug("Paginated response created")  # Log a debug message
            return Response(
                {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "count": self.page.paginator.count,
                    "results": data,
                }
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserFilter(django_filters.FilterSet):
    """
    Define filters for user search.
    """

    class Meta:
        model = CustomUser
        fields = ["email", "username"]  # Define the fields you want to filter on

class UserSearchViewSet(viewsets.ViewSet):
    """
    ViewSet for searching users.
    """

    pagination_class = CustomPagination  # Use the custom pagination class
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]  # Add SearchFilter for search functionality
    filterset_class = UserFilter  # Specify the filter class

    def list(self, request):
        """
        List users based on search query.
        """
        try:
            logger.info("User search request received")  # Log an info message
            
            queryset = CustomUser.objects.all().order_by('id')
            
            # Apply filters if provided
            filterset = self.filterset_class(request.query_params, queryset=queryset)
            filtered_queryset = filterset.qs
            
            # Apply search filter
            search_keyword = request.query_params.get("q")
            if search_keyword:
                filtered_queryset = filtered_queryset.filter(
                    Q(username__icontains=search_keyword) | Q(email__icontains=search_keyword)
                )
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(filtered_queryset, request)
            serializer = UserSignupSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        except Exception as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class FriendViewSet(generics.ListAPIView):
    """
    ViewSet for managing friend relationships.
    """

    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination  # Use the custom pagination class

    def get_queryset(self):
        # Get the list of friends for the authenticated user.
        try:
            logger.info("Friend list request received")  # Log an info message
            user = self.request.user
            queryset = Friend.objects.filter(user=user).order_by("id")
            return queryset
        except Exception as e:
            sentry_sdk.capture_exception(e)  # Capture exception with Sentry
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)