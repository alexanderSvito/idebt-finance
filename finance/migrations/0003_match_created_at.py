# Generated by Django 2.0.8 on 2018-10-05 09:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_auto_20180925_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]