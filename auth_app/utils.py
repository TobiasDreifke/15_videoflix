"""Utility helpers for authentication emails."""

import logging
from email.mime.image import MIMEImage
from pathlib import Path
from urllib.parse import urlencode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

logger = logging.getLogger(__name__)
LOGO_CID = 'videoflix-logo'
LOGO_PATH = Path(__file__).resolve().parent / 'static' / 'auth_app' / 'logo.png'


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


def send_activation_email(user, request):
    """Send the account activation email for a newly registered user."""

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    query = urlencode({'uid': uid, 'token': token})
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    activation_link = f"{frontend_url}/pages/auth/activate.html?{query}"
    context = {
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
    try:
        send_templated_email('activation', user.email, context)
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
    reset_link = f"{frontend_url}/pages/auth/confirm_password.html?{query}"
    context = {
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
    try:
        send_templated_email('password_reset', user.email, context)
        logger.info('Password reset email sent to %s', user.email)
    except Exception:
        logger.exception('Failed to send password reset email to %s', user.email)
        raise
