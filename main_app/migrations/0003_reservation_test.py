# Generated by Django 4.1.3 on 2023-01-24 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_remove_reservation_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='test',
            field=models.CharField(default=1, max_length=120),
            preserve_default=False,
        ),
    ]