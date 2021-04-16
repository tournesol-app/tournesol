from django.db import migrations
from backend.models import DjangoUser, UserInformation, VerifiableEmail
import sys

def create_emails(*args, **kwargs):
    for u in DjangoUser.objects.all():
        u_inf, _ = UserInformation.objects.get_or_create(user=u)
        if not u.email:
            print(u, "No email")
            continue
        v_email, v_email_created = VerifiableEmail.objects.get_or_create(email=u.email)
        print("Setting email for", u, v_email_created)
        v_email.user = u_inf
        v_email.is_verified = u.is_active
        v_email.save()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0048_auto_20201212_2151'),
    ]

    operations = [
        migrations.RunPython(create_emails),
    ]

