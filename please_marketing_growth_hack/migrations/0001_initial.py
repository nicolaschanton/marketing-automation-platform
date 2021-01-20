# Generated by Django 2.0.3 on 2018-09-22 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSiren',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('siren', models.CharField(blank=True, max_length=9, null=True, unique=True)),
                ('nic', models.CharField(blank=True, max_length=5, null=True)),
                ('l1_normalisee', models.CharField(blank=True, max_length=38, null=True)),
                ('l2_normalisee', models.CharField(blank=True, max_length=38, null=True)),
                ('l3_normalisee', models.CharField(blank=True, max_length=38, null=True)),
                ('l4_normalisee', models.CharField(blank=True, max_length=38, null=True)),
                ('l5_normalisee', models.CharField(blank=True, max_length=38, null=True)),
                ('l6_normalisee', models.CharField(blank=True, max_length=38, null=True)),
                ('l1_declaree', models.CharField(blank=True, max_length=38, null=True)),
                ('l2_declaree', models.CharField(blank=True, max_length=38, null=True)),
                ('l3_declaree', models.CharField(blank=True, max_length=38, null=True)),
                ('l4_declaree', models.CharField(blank=True, max_length=38, null=True)),
                ('l5_declaree', models.CharField(blank=True, max_length=38, null=True)),
                ('l6_declaree', models.CharField(blank=True, max_length=38, null=True)),
                ('numvoie', models.CharField(blank=True, max_length=4, null=True)),
                ('indrep', models.CharField(blank=True, max_length=1, null=True)),
                ('typvoie', models.CharField(blank=True, max_length=4, null=True)),
                ('libvoie', models.CharField(blank=True, max_length=32, null=True)),
                ('codpos', models.CharField(blank=True, max_length=5, null=True)),
                ('cedex', models.CharField(blank=True, max_length=5, null=True)),
                ('rpet', models.CharField(blank=True, max_length=2, null=True)),
                ('libreg', models.CharField(blank=True, max_length=70, null=True)),
                ('depet', models.CharField(blank=True, max_length=2, null=True)),
                ('arronet', models.CharField(blank=True, max_length=2, null=True)),
                ('ctonet', models.CharField(blank=True, max_length=3, null=True)),
                ('comet', models.CharField(blank=True, max_length=3, null=True)),
                ('libcom', models.CharField(blank=True, max_length=32, null=True)),
                ('du', models.CharField(blank=True, max_length=2, null=True)),
                ('tu', models.CharField(blank=True, max_length=1, null=True)),
                ('uu', models.CharField(blank=True, max_length=2, null=True)),
                ('epci', models.CharField(blank=True, max_length=9, null=True)),
                ('tcd', models.CharField(blank=True, max_length=2, null=True)),
                ('zemet', models.CharField(blank=True, max_length=4, null=True)),
                ('siege', models.CharField(blank=True, max_length=1, null=True)),
                ('enseigne', models.CharField(blank=True, max_length=50, null=True)),
                ('ind_publio', models.CharField(blank=True, max_length=1, null=True)),
                ('diffcom', models.CharField(blank=True, max_length=1, null=True)),
                ('amintret', models.CharField(blank=True, max_length=6, null=True)),
                ('natetab', models.CharField(blank=True, max_length=1, null=True)),
                ('libnatetab', models.CharField(blank=True, max_length=30, null=True)),
                ('apet700', models.CharField(blank=True, max_length=5, null=True)),
                ('libapet', models.CharField(blank=True, max_length=65, null=True)),
                ('dapet', models.CharField(blank=True, max_length=4, null=True)),
                ('tefet', models.CharField(blank=True, max_length=2, null=True)),
                ('libtefet', models.CharField(blank=True, max_length=23, null=True)),
                ('efetcent', models.CharField(blank=True, max_length=6, null=True)),
                ('defet', models.CharField(blank=True, max_length=4, null=True)),
                ('origine', models.CharField(blank=True, max_length=2, null=True)),
                ('dcret', models.CharField(blank=True, max_length=8, null=True)),
                ('ddebact', models.CharField(blank=True, max_length=8, null=True)),
                ('activnat', models.CharField(blank=True, max_length=2, null=True)),
                ('lieuact', models.CharField(blank=True, max_length=2, null=True)),
                ('actisurf', models.CharField(blank=True, max_length=2, null=True)),
                ('saisonat', models.CharField(blank=True, max_length=2, null=True)),
                ('modet', models.CharField(blank=True, max_length=1, null=True)),
                ('prodet', models.CharField(blank=True, max_length=1, null=True)),
                ('prodpart', models.CharField(blank=True, max_length=1, null=True)),
                ('auxilt', models.CharField(blank=True, max_length=1, null=True)),
                ('nomen_long', models.CharField(blank=True, max_length=131, null=True)),
                ('sigle', models.CharField(blank=True, max_length=20, null=True)),
                ('nom', models.CharField(blank=True, max_length=100, null=True)),
                ('prenom', models.CharField(blank=True, max_length=30, null=True)),
                ('civilite', models.CharField(blank=True, max_length=1, null=True)),
                ('rna', models.CharField(blank=True, max_length=10, null=True)),
                ('nicsiege', models.CharField(blank=True, max_length=5, null=True)),
                ('rpen', models.CharField(blank=True, max_length=2, null=True)),
                ('depcomen', models.CharField(blank=True, max_length=5, null=True)),
                ('adr_mail', models.CharField(blank=True, max_length=80, null=True)),
                ('nj', models.CharField(blank=True, max_length=4, null=True)),
                ('libnj', models.CharField(blank=True, max_length=100, null=True)),
                ('apen700', models.CharField(blank=True, max_length=5, null=True)),
                ('libapen', models.CharField(blank=True, max_length=65, null=True)),
                ('dapen', models.CharField(blank=True, max_length=4, null=True)),
                ('aprm', models.CharField(blank=True, max_length=6, null=True)),
                ('ess', models.CharField(blank=True, max_length=1, null=True)),
                ('dateess', models.CharField(blank=True, max_length=8, null=True)),
                ('tefen', models.CharField(blank=True, max_length=2, null=True)),
                ('libtefen', models.CharField(blank=True, max_length=23, null=True)),
                ('efencent', models.CharField(blank=True, max_length=6, null=True)),
                ('defen', models.CharField(blank=True, max_length=4, null=True)),
                ('categorie', models.CharField(blank=True, max_length=5, null=True)),
                ('dcren', models.CharField(blank=True, max_length=8, null=True)),
                ('amintren', models.CharField(blank=True, max_length=6, null=True)),
                ('monoact', models.CharField(blank=True, max_length=1, null=True)),
                ('moden', models.CharField(blank=True, max_length=1, null=True)),
                ('proden', models.CharField(blank=True, max_length=1, null=True)),
                ('essaann', models.CharField(blank=True, max_length=4, null=True)),
                ('tca', models.CharField(blank=True, max_length=1, null=True)),
                ('esaapen', models.CharField(blank=True, max_length=5, null=True)),
                ('esasec1n', models.CharField(blank=True, max_length=5, null=True)),
                ('esasec2n', models.CharField(blank=True, max_length=5, null=True)),
                ('esasec3n', models.CharField(blank=True, max_length=5, null=True)),
                ('esasec4n', models.CharField(blank=True, max_length=5, null=True)),
                ('vmaj', models.CharField(blank=True, max_length=1, null=True)),
                ('vmaj1', models.CharField(blank=True, max_length=1, null=True)),
                ('vmaj2', models.CharField(blank=True, max_length=1, null=True)),
                ('vmaj3', models.CharField(blank=True, max_length=1, null=True)),
                ('datemaj', models.CharField(blank=True, max_length=19, null=True)),
            ],
        ),
    ]