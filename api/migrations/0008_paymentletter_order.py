# Generated by Django 2.2.12 on 2020-04-22 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_payment_producer'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentletter',
            name='order',
            field=models.CharField(max_length=2056, null=True),
        ),
    ]
