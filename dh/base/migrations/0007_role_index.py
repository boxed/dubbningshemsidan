# Generated by Django 3.0.6 on 2020-06-20 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20200611_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='index',
            field=models.IntegerField(default=0),
        ),
    ]
