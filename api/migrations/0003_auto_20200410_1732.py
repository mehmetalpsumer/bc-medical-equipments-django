# Generated by Django 2.2.12 on 2020-04-10 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200408_0942'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentLetter',
            fields=[
                ('id', models.CharField(max_length=2056, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AlterField(
            model_name='organization',
            name='key',
            field=models.CharField(blank=True, default=None, max_length=2056, null=True),
        ),
        migrations.AlterField(
            model_name='organizationuser',
            name='key',
            field=models.CharField(blank=True, default=None, max_length=2056, null=True),
        ),
        migrations.CreateModel(
            name='MinistryOrder',
            fields=[
                ('id', models.CharField(max_length=2056, primary_key=True, serialize=False)),
                ('ministry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='HospitalOrder',
            fields=[
                ('id', models.CharField(max_length=2056, primary_key=True, serialize=False)),
                ('hospital', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.CharField(max_length=2056, primary_key=True, serialize=False)),
                ('producer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.CharField(max_length=2056, primary_key=True, serialize=False)),
                ('letter', models.CharField(max_length=2056)),
                ('producer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Organization')),
            ],
        ),
    ]
