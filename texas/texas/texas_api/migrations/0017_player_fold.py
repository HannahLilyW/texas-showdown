# Generated by Django 4.1.7 on 2023-04-30 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texas_api', '0016_player_bet'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='fold',
            field=models.BooleanField(default=False),
        ),
    ]
