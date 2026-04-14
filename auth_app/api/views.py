"""API views for authentication and account management."""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken

from .serializers import RegisterSerializer
from ..utils import send_activation_email


User = get_user_model()
GENERIC_ERROR = 'Bitte überprüfe deine Eingaben und versuche es erneut.'


class RegisterView(APIView):
    """Register a new inactive user account and send an activation email."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Create a user account from the submitted registration data."""
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': GENERIC_ERROR}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        send_activation_email(user, request)
        return Response({'message': 'Registrierung erfolgreich.'}, status=status.HTTP_201_CREATED)


class ActivateAccountView(APIView):
    """Activate a user account from a tokenized activation link or payload."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Activate an account from a legacy GET-based activation link."""
        return activate_account(uidb64, token)

    def post(self, request):
        """Activate an account from posted activation credentials."""
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        if not uidb64 or not token:
            return Response({'error': 'Ungültige Aktivierungsdaten.'}, status=status.HTTP_400_BAD_REQUEST)
        return activate_account(uidb64, token)


class LoginView(APIView):
    """Authenticate a user and issue JWT cookies."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate credentials and return a response with auth cookies."""
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate_user(email, password)
        if not user:
            return Response({'error': GENERIC_ERROR}, status=status.HTTP_401_UNAUTHORIZED)
        response = build_token_response(user)
        return response


class LogoutView(APIView):
    """Clear authentication cookies for the current client."""

    authentication_classes = []

    def post(self, request):
        """Delete auth cookies and confirm the logout."""
        response = Response(
            {'message': 'Erfolgreich abgemeldet.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class PasswordResetRequestView(APIView):
    """Start the password reset flow for an email address."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Send a password reset email when the address exists."""
        email = normalize_email(request.data.get('email'))
        if not email:
            return Response({'error': 'E-Mail ist erforderlich.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email__iexact=email).first()
        if user:
            from ..utils import send_password_reset_email
            send_password_reset_email(user, request)
        return Response({'message': 'Falls die E-Mail existiert, wurde eine Nachricht gesendet.'})


class PasswordResetConfirmView(APIView):
    """Complete the password reset flow with a valid token."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Set a new password for the user referenced by the reset link."""
        user = get_user_from_uid(uidb64)
        if not user or not default_token_generator.check_token(user, token):
            return Response({'error': 'Ungültiger Link.'}, status=status.HTTP_400_BAD_REQUEST)
        new_password = request.data.get('password')
        if not new_password or len(new_password) < 8:
            return Response({'error': GENERIC_ERROR}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Passwort erfolgreich geändert.'})


def get_user_from_uid(uidb64):
    """Return the user decoded from a base64 uid, or ``None`` if invalid."""

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        return None


def activate_account(uidb64, token):
    """Activate the user account identified by the uid and token."""

    user = get_user_from_uid(uidb64)
    if not user or not default_token_generator.check_token(user, token):
        return Response({'error': 'Ungültiger Link.'}, status=status.HTTP_400_BAD_REQUEST)
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])
    return Response({'message': 'Account erfolgreich aktiviert.'}, status=status.HTTP_200_OK)


def authenticate_user(email, password):
    """Return the active user for the provided credentials."""

    email = normalize_email(email)
    user = User.objects.filter(email__iexact=email).first()
    if not user or not user.check_password(password) or not user.is_active:
        return None
    return user


def normalize_email(email):
    """Normalize email input for case-insensitive lookups."""

    if not email:
        return ''
    return email.strip().lower()


def build_token_response(user):
    """Build a login response that stores JWT tokens in cookies."""

    refresh = RefreshToken.for_user(user)
    response = Response({'message': 'Login erfolgreich.'},
                        status=status.HTTP_200_OK)
    response.set_cookie('access_token', str(
        refresh.access_token), httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', str(refresh),
                        httponly=True, samesite='Lax')
    return response


class CookieTokenRefreshView(APIView):
    """Refresh the access token from the refresh token cookie."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Issue a fresh access token when a valid refresh cookie exists."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Kein Refresh Token gefunden.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = SimpleJWTRefreshToken(refresh_token)
            response = Response(
                {'message': 'Token erneuert.'}, status=status.HTTP_200_OK)
            response.set_cookie('access_token', str(
                refresh.access_token), httponly=True, samesite='Lax')
            return response
        except TokenError:
            return Response({'error': 'Ungültiger Refresh Token.'}, status=status.HTTP_401_UNAUTHORIZED)
