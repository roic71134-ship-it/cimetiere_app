from django.db import migrations, models
import django.db.models.deletion
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Cimetiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(default='Cimetière Municipal de Pointe-Noire', max_length=200)),
                ('adresse', models.TextField()),
                ('ville', models.CharField(default='Pointe-Noire', max_length=100)),
                ('pays', models.CharField(default='République du Congo', max_length=100)),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('email_contact', models.EmailField(blank=True, max_length=254)),
                ('superficie_m2', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('taille_std_longueur', models.DecimalField(decimal_places=2, default=2.5, max_digits=5)),
                ('taille_std_largeur', models.DecimalField(decimal_places=2, default=1.2, max_digits=5)),
                ('taille_std_profondeur', models.DecimalField(decimal_places=2, default=2.0, max_digits=5)),
                ('coordonnees_centre', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('est_actif', models.BooleanField(default=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Cimetière',
                'verbose_name_plural': 'Cimetières',
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10)),
                ('type_zone', models.CharField(choices=[('INHUMATION', "Zone d'inhumation"), ('ALLEE', 'Allée / Chemin'), ('NON_EXPLOITABLE', 'Zone non exploitable'), ('TECHNIQUE', 'Zone technique'), ('ENTREE', 'Entrée / Accueil')], default='INHUMATION', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('couleur_carte', models.CharField(default='#90EE90', max_length=7)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
                ('est_active', models.BooleanField(default=True)),
                ('ordre_affichage', models.PositiveIntegerField(default=0)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('cimetiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zones', to='terrain.cimetiere')),
            ],
            options={
                'verbose_name': 'Zone',
                'verbose_name_plural': 'Zones',
                'ordering': ['ordre_affichage', 'code'],
            },
        ),
        migrations.CreateModel(
            name='Bloc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10)),
                ('capacite_theorique', models.PositiveIntegerField(default=0)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
                ('est_actif', models.BooleanField(default=True)),
                ('ordre_affichage', models.PositiveIntegerField(default=0)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocs', to='terrain.zone')),
            ],
            options={
                'verbose_name': 'Bloc',
                'verbose_name_plural': 'Blocs',
                'ordering': ['ordre_affichage', 'code'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='zone',
            unique_together={('cimetiere', 'code')},
        ),
        migrations.AlterUniqueTogether(
            name='bloc',
            unique_together={('zone', 'code')},
        ),
    ]