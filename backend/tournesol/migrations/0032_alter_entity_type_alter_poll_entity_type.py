# Generated by Django 4.0.2 on 2022-03-04 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0031_entity_tournesol_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='type',
            field=models.CharField(choices=[('video', 'Video'), ('candidate_fr_2022', 'Candidate (FR 2022)')], max_length=32),
        ),
        migrations.AlterField(
            model_name='poll',
            name='entity_type',
            field=models.CharField(choices=[('video', 'Video'), ('candidate_fr_2022', 'Candidate (FR 2022)')], max_length=32),
        ),
    ]
