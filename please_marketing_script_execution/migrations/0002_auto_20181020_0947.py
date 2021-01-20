# Generated by Django 2.0.3 on 2018-10-20 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_script_execution', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scriptexecution',
            name='ended_date',
        ),
        migrations.RemoveField(
            model_name='scriptexecution',
            name='started_date',
        ),
        migrations.AddField(
            model_name='scriptexecution',
            name='status',
            field=models.CharField(choices=[('s', 'Started'), ('d', 'Done')], default='s', max_length=1),
        ),
    ]
