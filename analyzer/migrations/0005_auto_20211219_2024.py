# Generated by Django 3.2.8 on 2021-12-19 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0004_alter_results_today_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='results',
            name='actual_price',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='results',
            name='predicted_price',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
