from django.db import migrations, models


def set_existing_users_verified(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.all().update(email_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="email_verification_token",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="user",
            name="email_verification_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(set_existing_users_verified, migrations.RunPython.noop),
    ]
