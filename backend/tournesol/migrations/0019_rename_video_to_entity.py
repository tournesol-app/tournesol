from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0018_fill_missing_video_duration'),
    ]

    operations = [
        migrations.RenameModel('Video', 'Entity')
    ]
