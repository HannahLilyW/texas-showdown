# Generated by Django 4.1.7 on 2023-04-30 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texas_api', '0015_game_is_betting_round_game_pot_player_money'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='bet',
            field=models.IntegerField(default=0),
        ),
    ]
