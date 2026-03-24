from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings


def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_url = settings.FRONTEND_URL
    activation_link = f"{frontend_url}/activate/{uid}/{token}/"
    send_mail(
        subject='Videoflix - Account aktivieren',
        message=f'Klicke hier um deinen Account zu aktivieren: {activation_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_password_reset_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_url = settings.FRONTEND_URL
    reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
    send_mail(
        subject='Videoflix - Passwort zurücksetzen',
        message=f'Klicke hier um dein Passwort zurückzusetzen: {reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )