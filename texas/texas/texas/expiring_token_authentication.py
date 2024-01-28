# The TokenAuthentication provided by Django REST Framework does not support tokens expiring.
# It is important for security that users are automatically logged out after a certain period of time,
# so here I am subclassing TokenAuthentication to implement token expiration
# so that users will have to re-authenticate after 60 days of inactivity.

# I took inspiration from https://stackoverflow.com/questions/14567586/token-authentication-for-restful-api-should-the-token-be-periodically-changed

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
import datetime


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if (token.created < (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=60))):
            raise AuthenticationFailed('Token has expired. Please authenticate again.')
        return (user, token)
