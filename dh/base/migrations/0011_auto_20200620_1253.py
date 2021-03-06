# Generated by Django 3.0.6 on 2020-06-20 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_metadata_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaDataObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='metadata',
            name='metadata_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.MetaDataObject'),
        ),
    ]
