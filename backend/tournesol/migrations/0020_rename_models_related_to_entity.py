# Generated by Django 3.2.11 on 2022-02-03 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0019_rename_video_to_entity'),
    ]

    operations = [
        migrations.RenameModel('VideoCriteriaScore', 'EntityCriteriaScore')
    ]
