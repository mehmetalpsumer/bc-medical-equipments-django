# Generated by Django 2.2.12 on 2020-04-12 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200410_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentletter',
            name='bank',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Organization'),
        ),
    ]
