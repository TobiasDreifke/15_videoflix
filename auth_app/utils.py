"""Utility helpers for authentication emails."""

import logging
from email.mime.image import MIMEImage
from pathlib import Path
from urllib.parse import urlencode

import django_rq
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

logger = logging.getLogger(__name__)
LOGO_CID = 'videoflix-logo'
LOGO_PATH = Path(__file__).resolve().parent / 'static' / 'auth_app' / 'logo.png'
User = get_user_model()


def send_templated_email(template_prefix, recipient, context):
    """Render and send a branded multipart email from text and HTML templates."""

    subject = render_to_string(f'emails/{template_prefix}_subject.txt', context).strip()
    text_body = render_to_string(f'emails/{template_prefix}_body.txt', context)
    html_body = render_to_string(f'emails/{template_prefix}_body.html', context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.attach_alternative(html_body, 'text/html')
    attach_inline_logo(email)
    email.send()


def attach_inline_logo(email):
    """Attach the email logo as an inline image for mail client compatibility."""

    with LOGO_PATH.open('rb') as logo_file:
        logo = MIMEImage(logo_file.read())
    logo.add_header('Content-ID', f'<{LOGO_CID}>')
    logo.add_header('Content-Disposition', 'inline', filename='logo.png')
    email.attach(logo)


def get_email_greeting_name(user):
    """Return a friendly greeting name without falling back to an email address."""

    return user.get_full_name() or user.username or 'there'


def build_activation_email_context(user):
    """Build the template context for account activation emails."""

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    query = urlencode({'uid': uid, 'token': token})
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    activation_link = f"{frontend_url}/pages/auth/activate.html?{query}"
    return {
        'user': user,
        'headline': 'Activate your Videoflix account',
        'preheader': 'Confirm your email address to start using Videoflix.',
        'cta_label': 'Activate Account',
        'cta_url': activation_link,
        'support_email': settings.DEFAULT_FROM_EMAIL,
        'user_name': get_email_greeting_name(user),
        'videoflix_url': frontend_url,
        'logo_url': f'cid:{LOGO_CID}',
    }


def build_password_reset_email_context(user):
    """Build the template context for password reset emails."""

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    query = urlencode({'uid': uid, 'token': token})
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    reset_link = f"{frontend_url}/pages/auth/confirm_password.html?{query}"
    return {
        'user': user,
        'headline': 'Reset your Videoflix password',
        'preheader': 'Use the secure link below to choose a new password.',
        'cta_label': 'Reset Password',
        'cta_url': reset_link,
        'support_email': settings.DEFAULT_FROM_EMAIL,
        'user_name': get_email_greeting_name(user),
        'videoflix_url': frontend_url,
        'logo_url': f'cid:{LOGO_CID}',
    }


def send_activation_email_job(user_id):
    """Send the queued account activation email for the given user."""

    user = User.objects.get(pk=user_id)
    try:
        send_templated_email('activation', user.email, build_activation_email_context(user))
        logger.info('Activation email sent to %s', user.email)
    except Exception:
        logger.exception('Failed to send activation email to %s', user.email)
        raise


def send_activation_email(user, request=None):
    """Queue the account activation email for a newly registered user."""

    queue = django_rq.get_queue('high')
    queue.enqueue('auth_app.utils.send_activation_email_job', user.pk)


def send_password_reset_email_job(user_id):
    """Send the queued password reset email for the given user."""

    user = User.objects.get(pk=user_id)
    try:
        send_templated_email('password_reset', user.email, build_password_reset_email_context(user))
        logger.info('Password reset email sent to %s', user.email)
    except Exception:
        logger.exception('Failed to send password reset email to %s', user.email)
        raise


def send_password_reset_email(user, request=None):
    """Queue the password reset email for the supplied user."""

    queue = django_rq.get_queue('high')
    queue.enqueue('auth_app.utils.send_password_reset_email_job', user.pk)
