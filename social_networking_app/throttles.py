from rest_framework.throttling import UserRateThrottle


class FriendRequestThrottle(UserRateThrottle):
    scope = "friend_request"

    def get_rate(self):
        return "3/minute"
