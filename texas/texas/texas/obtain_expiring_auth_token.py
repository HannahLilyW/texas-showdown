# This is meant to be used with ExpiringTokenAuthentication.
# The ObtainAuthToken class provided by DRF for obtaining a token from username and password
# by default does not refresh a user's token.
# So I also subclass that so the token will be valid for 12 hours after the last successful authentication.

# Also, creating a new token upon every login is more secure than re-using tokens from previous logins
# in case a token gets compromised.

# Putting this in a separate file from ExpiringTokenAuthentication to prevent circular import issue.

# I took inspiration from https://stackoverflow.com/questions/14567586/token-authentication-for-restful-api-should-the-token-be-periodically-changed

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            # Delete the existing token and create a new one.
            token.delete()
            token = Token.objects.create(user=user)
        return Response({'token': token.key, 'username': user.username})
