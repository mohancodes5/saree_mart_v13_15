"""
Create or update the store administrator account requested for demo/testing.

Run once:
  python manage.py ensure_admin_mohan

Then sign in at /accounts/login/ (User login or Admin login) as:
  username: mohan
  password: mohan@12345
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Creates/updates user 'mohan' as staff admin (password mohan@12345)."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="mohan",
            defaults={
                "email": "mohan@example.com",
                "is_staff": True,
                "is_superuser": True,
                "is_vendor": False,
            },
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_vendor = False
        user.set_password("mohan@12345")
        user.email = user.email or "mohan@example.com"
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} administrator 'mohan'. "
                "Login at /accounts/login/ - User login and Admin login both go to /manage/ for this account."
            )
        )
