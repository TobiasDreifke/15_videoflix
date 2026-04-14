"""Custom authentication classes for cookie-based JWT auth."""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """Read and validate JWT access tokens from cookies."""

    def authenticate(self, request):
        """Authenticate the request using the ``access_token`` cookie."""
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
        except TokenError:
            return None
        return self.get_user(validated_token), validated_token
