# Generated by Django 4.0.8 on 2022-10-20 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("faq", "0003_rename_faquestion_faqentry"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="faqentry",
            options={
                "ordering": ["rank"],
                "verbose_name": "FAQ Entry",
                "verbose_name_plural": "FAQ Entries",
            },
        ),
    ]
