# Generated by Django 3.2.6 on 2021-10-15 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0011_alter_comparison_datetime_lastedit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='rating_n_contributors',
        ),
        migrations.RemoveField(
            model_name='video',
            name='rating_n_ratings',
        ),
    ]
