from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from ..utils import send_activation_email

User = get_user_model()
GENERIC_ERROR = 'Bitte überprüfe deine Eingaben und versuche es erneut.'


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': GENERIC_ERROR}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        send_activation_email(user, request)
        return Response({'message': 'Registrierung erfolgreich.'}, status=status.HTTP_201_CREATED)


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = get_user_from_uid(uidb64)
        if not user or not default_token_generator.check_token(user, token):
            return Response({'error': 'Ungültiger Aktivierungslink.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        return Response({'message': 'Account aktiviert.'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate_user(email, password)
        if not user:
            return Response({'error': GENERIC_ERROR}, status=status.HTTP_401_UNAUTHORIZED)
        response = build_token_response(user)
        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response(
            {'message': 'Erfolgreich abgemeldet.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            from ..utils import send_password_reset_email
            send_password_reset_email(user, request)
        return Response({'message': 'Falls die E-Mail existiert, wurde eine Nachricht gesendet.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
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
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        return None


def authenticate_user(email, password):
    user = User.objects.filter(email=email).first()
    if not user or not user.check_password(password) or not user.is_active:
        return None
    return user


def build_token_response(user):
    refresh = RefreshToken.for_user(user)
    response = Response({'message': 'Login erfolgreich.'},
                        status=status.HTTP_200_OK)
    response.set_cookie('access_token', str(
        refresh.access_token), httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', str(refresh),
                        httponly=True, samesite='Lax')
    return response


class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
