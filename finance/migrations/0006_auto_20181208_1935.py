# Generated by Django 2.0.8 on 2018-12-08 19:35

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_debt_total_pay_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('plain_document', django_cryptography.fields.encrypt(models.TextField(max_length=1024))),
            ],
        ),
        migrations.AddField(
            model_name='debt',
            name='contract_filename',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]