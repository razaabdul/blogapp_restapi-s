# Generated by Django 5.0.6 on 2024-05-08 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='value',
            field=models.ImageField(default=0, upload_to=''),
        ),
    ]
