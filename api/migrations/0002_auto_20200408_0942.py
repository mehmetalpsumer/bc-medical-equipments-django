# Generated by Django 2.2.12 on 2020-04-08 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='group',
            field=models.CharField(choices=[('MINISTRY', 'MINISTRY'), ('HOSPITAL', 'HOSPITAL'), ('PRODUCER', 'PRODUCER'), ('BANK', 'BANK'), ('OTHER', 'OTHER')], default='OTHER', max_length=32),
        ),
    ]
