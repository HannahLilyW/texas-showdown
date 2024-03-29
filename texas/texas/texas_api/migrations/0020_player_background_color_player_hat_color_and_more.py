# Generated by Django 5.0.1 on 2024-01-21 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texas_api', '0019_betturnhistory_player_money'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='background_color',
            field=models.CharField(choices=[('BLACK', 'black'), ('RED', 'red'), ('BLUE', 'blue'), ('BROWN', 'brown'), ('GREEN', 'green'), ('YELLOW', 'yellow'), ('PURPLE', 'purple'), ('GRAY', 'gray'), ('WHITE', 'white'), ('SKIN1', 'skin1'), ('SKIN2', 'skin2'), ('SKIN3', 'skin3'), ('SKIN4', 'skin4'), ('BLANK', 'blank')], default='BLANK', max_length=10),
        ),
        migrations.AddField(
            model_name='player',
            name='hat_color',
            field=models.CharField(choices=[('BLACK', 'black'), ('RED', 'red'), ('BLUE', 'blue'), ('BROWN', 'brown'), ('GREEN', 'green'), ('YELLOW', 'yellow'), ('PURPLE', 'purple'), ('GRAY', 'gray'), ('WHITE', 'white'), ('SKIN1', 'skin1'), ('SKIN2', 'skin2'), ('SKIN3', 'skin3'), ('SKIN4', 'skin4'), ('BLANK', 'blank')], default='BLACK', max_length=10),
        ),
        migrations.AddField(
            model_name='player',
            name='is_guest',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='player',
            name='shirt_color',
            field=models.CharField(choices=[('BLACK', 'black'), ('RED', 'red'), ('BLUE', 'blue'), ('BROWN', 'brown'), ('GREEN', 'green'), ('YELLOW', 'yellow'), ('PURPLE', 'purple'), ('GRAY', 'gray'), ('WHITE', 'white'), ('SKIN1', 'skin1'), ('SKIN2', 'skin2'), ('SKIN3', 'skin3'), ('SKIN4', 'skin4'), ('BLANK', 'blank')], default='BLACK', max_length=10),
        ),
        migrations.AddField(
            model_name='player',
            name='skin_color',
            field=models.CharField(choices=[('BLACK', 'black'), ('RED', 'red'), ('BLUE', 'blue'), ('BROWN', 'brown'), ('GREEN', 'green'), ('YELLOW', 'yellow'), ('PURPLE', 'purple'), ('GRAY', 'gray'), ('WHITE', 'white'), ('SKIN1', 'skin1'), ('SKIN2', 'skin2'), ('SKIN3', 'skin3'), ('SKIN4', 'skin4'), ('BLANK', 'blank')], default='BLACK', max_length=10),
        ),
    ]
