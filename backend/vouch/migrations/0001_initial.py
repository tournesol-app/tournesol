# Generated by Django 4.0.4 on 2022-05-17 17:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_public', models.BooleanField(default=False, help_text='Should the voucher be public?')),
                ('trust_value', models.FloatField(default=0, help_text='The trust value given by the vouching user to receiving user.')),
                ('by', models.ForeignKey(help_text='The user giving the voucher.', on_delete=django.db.models.deletion.CASCADE, related_name='vouchers_given', to=settings.AUTH_USER_MODEL)),
                ('to', models.ForeignKey(help_text='The user receiving the voucher.', on_delete=django.db.models.deletion.CASCADE, related_name='vouchers_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
