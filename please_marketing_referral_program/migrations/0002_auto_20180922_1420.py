# Generated by Django 2.0.3 on 2018-09-22 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0077_auto_20180920_1218'),
        ('please_marketing_referral_program', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referralmatch',
            name='sms_sent',
        ),
        migrations.AddField(
            model_name='referralmatch',
            name='sms',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='please_marketing_app.SmsHistory'),
        ),
        migrations.AlterField(
            model_name='referralmatch',
            name='referee',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='referee', to='please_marketing_app.Customer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='referralmatch',
            name='referrer',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='referrer', to='please_marketing_app.Customer'),
            preserve_default=False,
        ),
    ]
