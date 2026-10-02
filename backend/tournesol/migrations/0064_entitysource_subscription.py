import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0063_data_mark_compared_entities_as_seen'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EntitySource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(help_text='A unique identifier, built with a namespace and an external id.', max_length=144, unique=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('entity_source', models.ForeignKey(help_text='The source the user subscribes to.', on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='tournesol.entitysource')),
                ('user', models.ForeignKey(help_text='The user who subscribes to the source.', on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', '-created_at'],
                'unique_together': {('user', 'entity_source')},
            },
        ),
    ]
