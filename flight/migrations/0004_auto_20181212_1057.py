# Generated by Django 2.1.3 on 2018-12-12 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0003_auto_20181207_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='flight',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=1000, null=True),
        ),
    ]
