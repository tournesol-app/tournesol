# Generated by Django 4.0.2 on 2022-02-09 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_email_used_as_username'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserPreference',
        ),
    ]
