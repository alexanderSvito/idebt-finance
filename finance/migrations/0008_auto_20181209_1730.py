# Generated by Django 2.0.8 on 2018-12-09 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_auto_20181209_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debt',
            name='loan_size',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
        migrations.AlterField(
            model_name='debt',
            name='total_pay_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=50),
        ),
        migrations.AlterField(
            model_name='issue',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
        migrations.AlterField(
            model_name='issue',
            name='max_overpay',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
        migrations.AlterField(
            model_name='offer',
            name='credit_fund',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
        migrations.AlterField(
            model_name='offer',
            name='max_loan_size',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
        migrations.AlterField(
            model_name='offer',
            name='min_loan_size',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
        migrations.AlterField(
            model_name='offer',
            name='used_funds',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50),
        ),
    ]