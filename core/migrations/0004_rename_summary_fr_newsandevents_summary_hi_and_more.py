# Generated by Django 4.0.8 on 2025-02-19 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_newsandevents_summary_es_newsandevents_summary_fr_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newsandevents',
            old_name='summary_fr',
            new_name='summary_hi',
        ),
        migrations.RemoveField(
            model_name='newsandevents',
            name='title_fr',
        ),
        migrations.AddField(
            model_name='newsandevents',
            name='title_hi',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
