# Generated by Django 4.1.7 on 2023-04-03 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texas_api', '0007_game_turn'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='is_turn',
            field=models.BooleanField(default=False),
        ),
    ]