"""Transactional email via Resend (https://resend.com)."""

from __future__ import annotations

import logging
import secrets

from django.conf import settings
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from shop.models import Order

from .models import User

logger = logging.getLogger(__name__)


def send_resend_email(
    *, to_email: str, subject: str, html: str
) -> tuple[bool, str | None]:
    """Send one HTML email via Resend.

    Returns (True, None) on success, or (False, message) where message is from the
    Resend API when available (e.g. testing-mode restriction or domain verification).
    """
    api_key = getattr(settings, "RESEND_API_KEY", "") or ""
    if not api_key.strip():
        logger.warning("RESEND_API_KEY is not set; email not sent (subject=%r)", subject)
        return False, None

    try:
        import resend
        from resend.exceptions import ResendError
    except ImportError:
        logger.exception("resend package not installed")
        return False, None

    resend.api_key = api_key.strip()
    from_email = getattr(
        settings,
        "RESEND_FROM_EMAIL",
        "onboarding@resend.dev",
    )

    try:
        resend.Emails.send(
            {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html,
            }
        )
        return True, None
    except ResendError as exc:
        msg = (getattr(exc, "message", None) or str(exc)).strip()
        logger.error("Resend API error for %s: %s", to_email, msg)
        return False, msg
    except Exception:
        logger.exception("Resend send failed for %s", to_email)
        return False, None


def build_verification_url(request: HttpRequest, user: User) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = user.email_verification_token
    path = reverse(
        "accounts:verify_email",
        kwargs={"uidb64": uid, "token": token},
    )
    return request.build_absolute_uri(path)


def issue_email_verification_token(user: User) -> None:
    """Generate a new token and mark email as unverified until confirmed."""
    user.email_verification_token = secrets.token_urlsafe(32)
    user.email_verified = False
    user.save(update_fields=["email_verification_token", "email_verified"])


def send_verification_email(request: HttpRequest, user: User) -> tuple[bool, str | None]:
    if not user.email:
        return False, None
    subject = "Verify your email — SareeMart"
    link = build_verification_url(request, user)
    html = render_to_string(
        "emails/verification_email.html",
        {"user": user, "verification_link": link},
    )
    ok, api_message = send_resend_email(
        to_email=user.email, subject=subject, html=html
    )
    if ok:
        user.email_verification_sent_at = timezone.now()
        user.save(update_fields=["email_verification_sent_at"])
    return ok, api_message


def send_order_placed_email(order: Order) -> None:
    user = order.user
    if not user.email:
        return
    order = Order.objects.prefetch_related("items__product").get(pk=order.pk)
    subject = f"Order #{order.pk} received — SareeMart"
    html = render_to_string(
        "emails/order_placed.html",
        {"order": order},
    )
    ok, err = send_resend_email(to_email=user.email, subject=subject, html=html)
    if not ok:
        logger.warning(
            "Order-placed email not sent for order %s: %s",
            order.pk,
            err or "unknown error",
        )


def send_order_status_email(order: Order, previous_status: str) -> None:
    user = order.user
    if not user.email:
        return
    subject = f"Order #{order.pk} is now {order.get_status_display()} — SareeMart"
    html = render_to_string(
        "emails/order_status_update.html",
        {
            "order": order,
            "previous_status": previous_status,
            "previous_label": dict(order.Status.choices).get(
                previous_status, previous_status
            ),
        },
    )
    ok, err = send_resend_email(to_email=user.email, subject=subject, html=html)
    if not ok:
        logger.warning(
            "Order status email not sent for order %s: %s",
            order.pk,
            err or "unknown error",
        )
