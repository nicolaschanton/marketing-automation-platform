# Generated by Django 2.0.3 on 2019-02-12 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, max_length=150, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=10, null=True)),
                ('raw_address', models.CharField(blank=True, max_length=150, null=True)),
                ('street', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('zip', models.CharField(blank=True, max_length=5, null=True)),
                ('user_agent_data', models.CharField(blank=True, max_length=500, null=True)),
                ('landing_page_name', models.CharField(blank=True, max_length=100, null=True)),
                ('signed_up_please', models.BooleanField(default=False)),
                ('odoo_user_id', models.IntegerField(blank=True, null=True)),
                ('sent_to_intercom', models.BooleanField(default=False)),
                ('campaign_name', models.CharField(blank=True, max_length=100, null=True)),
                ('campaign_zip', models.CharField(blank=True, max_length=5, null=True)),
                ('campaign_keywords', models.CharField(blank=True, max_length=100, null=True)),
                ('campaign_search_terms', models.CharField(blank=True, max_length=100, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]