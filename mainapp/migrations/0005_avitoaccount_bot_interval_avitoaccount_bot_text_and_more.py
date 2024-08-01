# Generated by Django 5.0.7 on 2024-07-29 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_alter_avitoaccount_time_to_shutdown_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='avitoaccount',
            name='bot_interval',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='avitoaccount',
            name='bot_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='avitoaccount',
            name='manager_interval',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='avitoaccount',
            name='triggers_ai',
            field=models.TextField(blank=True, null=True),
        ),
    ]