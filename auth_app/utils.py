import logging
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

logger = logging.getLogger(__name__)


def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    backend_url = settings.BACKEND_URL
    activation_link = f"{backend_url}/api/activate/{uid}/{token}/"
    try:
        send_mail(
            subject='Videoflix - Account aktivieren',
            message=f'Klicke hier um deinen Account zu aktivieren: {activation_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        logger.info('Activation email sent to %s', user.email)
    except Exception:
        logger.exception('Failed to send activation email to %s', user.email)
        raise


def send_password_reset_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    backend_url = settings.BACKEND_URL
    reset_link = f"{backend_url}/reset-password/{uid}/{token}/"
    try:
        send_mail(
            subject='Videoflix - Passwort zuruecksetzen',
            message=f'Klicke hier um dein Passwort zurueckzusetzen: {reset_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        logger.info('Password reset email sent to %s', user.email)
    except Exception:
        logger.exception('Failed to send password reset email to %s', user.email)
        raise