# Generated by Django 3.0.6 on 2020-06-20 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20200620_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='value',
            field=models.CharField(db_index=True, default='', max_length=255),
            preserve_default=False,
        ),
    ]
