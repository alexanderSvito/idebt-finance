# Generated by Django 2.0.8 on 2018-12-09 17:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_auto_20181208_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='debt',
            name='closed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='debt',
            name='frozen_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='debt',
            name='issue',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='investment', to='finance.Issue'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='offer',
            name='created_at',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='debt',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]