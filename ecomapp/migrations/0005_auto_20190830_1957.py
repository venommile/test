# Generated by Django 2.2.4 on 2019-08-30 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0004_auto_20190830_1956'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='title',
        ),
    ]
