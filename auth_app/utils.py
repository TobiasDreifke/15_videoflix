"""Utility helpers for authentication emails."""

import logging
from urllib.parse import urlencode
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

logger = logging.getLogger(__name__)


def send_activation_email(user, request):
    """Send the account activation email for a newly registered user."""

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    query = urlencode({'uid': uid, 'token': token})
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    activation_link = f"{frontend_url}/pages/auth/activate.html?{query}"
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
    """Send the password reset email for the supplied user."""

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    query = urlencode({'uid': uid, 'token': token})
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    reset_link = f"{frontend_url}/pages/auth/reset-password.html?{query}"
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
