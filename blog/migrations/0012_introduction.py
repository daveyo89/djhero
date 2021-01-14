# Generated by Django 3.1.2 on 2020-10-29 23:32

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_remove_postimage_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Introduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('message', tinymce.models.HTMLField()),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'In Active')], default='I', max_length=1)),
            ],
        ),
    ]
