# Generated by Django 3.1.2 on 2020-10-30 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_introduction'),
    ]

    operations = [
        migrations.AddField(
            model_name='postimage',
            name='description',
            field=models.CharField(default='', max_length=120),
        ),
    ]
