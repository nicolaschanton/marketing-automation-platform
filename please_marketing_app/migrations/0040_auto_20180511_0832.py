# Generated by Django 2.0.3 on 2018-05-11 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0039_auto_20180509_1254'),
    ]

    operations = [
        migrations.RenameField(
            model_name='intercomevent',
            old_name='item_id',
            new_name='mw_item_id',
        ),
        migrations.RenameField(
            model_name='intercomevent',
            old_name='offer_id',
            new_name='mw_offer_id',
        ),
        migrations.RenameField(
            model_name='intercomevent',
            old_name='supplier_id',
            new_name='mw_supplier_id',
        ),
        migrations.RenameField(
            model_name='intercomevent',
            old_name='universe_id',
            new_name='mw_universe_id',
        ),
    ]
