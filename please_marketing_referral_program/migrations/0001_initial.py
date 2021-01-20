# Generated by Django 2.0.3 on 2018-09-20 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('please_marketing_app', '0077_auto_20180920_1218'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralLead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lead_email', models.CharField(blank=True, max_length=500, null=True)),
                ('lead_sms', models.CharField(blank=True, max_length=500, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
                ('referrer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='please_marketing_app.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='ReferralMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_sent', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
                ('referee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='referee', to='please_marketing_app.Customer')),
                ('referrer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='referrer', to='please_marketing_app.Customer')),
            ],
        ),
    ]