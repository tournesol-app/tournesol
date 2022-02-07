from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournesol', '0018_fill_missing_video_duration'),
        ('twitterbot', '0001_initial')
    ]

    operations = [
        # remove unused fields
        migrations.RemoveField(
            model_name='video',
            name='caption_text',
        ),
        migrations.RemoveField(
            model_name='video',
            name='embedding',
        ),
        migrations.RemoveField(
            model_name='video',
            name='info',
        ),
        migrations.RemoveField(
            model_name='video',
            name='pareto_optimal',
        ),
        migrations.RemoveField(
            model_name='video',
            name='wrong_url',
        ),

        # remove unused models
        migrations.DeleteModel(
            name='VideoRatingThankYou',
        ),
        migrations.DeleteModel(
            name='VideoSelectorSkips',
        ),

        # rename existing models
        migrations.RenameModel('Video', 'Entity'),
        migrations.RenameModel('VideoCriteriaScore', 'EntityCriteriaScore'),

        migrations.AlterModelOptions(
            name='entity',
            options={'verbose_name_plural': 'entities'},
        ),
        migrations.AlterField(
            model_name='entity',
            name='language',
            field=models.CharField(blank=True, choices=[('af', 'Afrikaans'), ('ar', 'Arabic'), ('ar-dz', 'Algerian Arabic'), ('ast', 'Asturian'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('dsb', 'Lower Sorbian'), ('el', 'Greek'), ('en', 'English'), ('en-au', 'Australian English'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-co', 'Colombian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('ga', 'Irish'), ('gd', 'Scottish Gaelic'), ('gl', 'Galician'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hr', 'Croatian'), ('hsb', 'Upper Sorbian'), ('hu', 'Hungarian'), ('hy', 'Armenian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('ig', 'Igbo'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kab', 'Kabyle'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('ky', 'Kyrgyz'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('mr', 'Marathi'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmål'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('tg', 'Tajik'), ('th', 'Thai'), ('tk', 'Turkmen'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('uz', 'Uzbek'), ('vi', 'Vietnamese'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese')], help_text='Language of the video', max_length=10, null=True),
        ),

        # add new entity fields
        migrations.AddField(
            model_name='entity',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='entity',
            name='type',
            field=models.CharField(choices=[('video', 'Video')], max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='uid',
            field=models.CharField(help_text='A unique identifier, build with a namespace and an external id.',
                                   max_length=144, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='contributorrating',
            name='video',
            field=models.ForeignKey(help_text='Entity being scored', on_delete=django.db.models.deletion.CASCADE,
                                    related_name='contributorvideoratings', to='tournesol.entity'),
        ),
    ]
