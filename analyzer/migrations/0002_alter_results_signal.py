# Generated by Django 3.2.8 on 2021-11-18 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='results',
            name='signal',
            field=models.CharField(max_length=250),
        ),
    ]