from django.db import migrations, models
import django.db.models.deletion
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('terrain', '0001_initial'),
        ('auth_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Caveau',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(db_index=True, max_length=20, unique=True)),
                ('numero', models.PositiveIntegerField()),
                ('statut', models.CharField(choices=[('DISPONIBLE', 'Disponible (Vert)'), ('RESERVE', 'Réservé (Orange)'), ('OCCUPE', 'Occupé (Rouge)'), ('NON_EXPLOITABLE', 'Non exploitable (Gris)'), ('MAINTENANCE', 'En maintenance (Jaune)')], db_index=True, default='DISPONIBLE', max_length=20)),
                ('statut_change_le', models.DateTimeField(blank=True, null=True)),
                ('coordonnees', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('longueur_m', models.DecimalField(decimal_places=2, default=2.5, max_digits=5)),
                ('largeur_m', models.DecimalField(decimal_places=2, default=1.2, max_digits=5)),
                ('profondeur_m', models.DecimalField(decimal_places=2, default=2.0, max_digits=5)),
                ('type_concession_autorise', models.CharField(choices=[('TEMPORAIRE', 'Temporaire (5 ans)'), ('TRENTENAIRE', 'Trentenaire (30 ans)'), ('PERPETUELLE', 'Perpétuelle'), ('FAMILIALE', 'Familiale')], default='TEMPORAIRE', max_length=20)),
                ('est_accessible_pmr', models.BooleanField(default=False)),
                ('capacite_corps', models.PositiveIntegerField(default=1)),
                ('prix_temporaire_xaf', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('prix_trentenaire_xaf', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('prix_perpetuelle_xaf', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('notes', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('bloc', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='caveaux', to='terrain.bloc')),
                ('statut_change_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='caveaux_modifies', to='auth_app.utilisateur')),
            ],
            options={
                'verbose_name': 'Caveau',
                'verbose_name_plural': 'Caveaux',
                'ordering': ['reference'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='caveau',
            unique_together={('bloc', 'numero')},
        ),
    ]