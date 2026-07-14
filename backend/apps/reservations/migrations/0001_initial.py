from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth_app', '0001_initial'),
        ('caveaux', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Defunt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('date_deces', models.DateField(verbose_name='Date de décès')),
                ('lieu_naissance', models.CharField(blank=True, max_length=200)),
                ('lieu_deces', models.CharField(blank=True, max_length=200)),
                ('nationalite', models.CharField(default='Congolaise', max_length=100)),
                ('sexe', models.CharField(choices=[('M', 'Masculin'), ('F', 'Féminin'), ('A', 'Autre')], default='M', max_length=1)),
                ('numero_acte_deces', models.CharField(blank=True, max_length=100)),
                ('numero_permis_inhumer', models.CharField(blank=True, max_length=100)),
                ('nom_famille_responsable', models.CharField(blank=True, max_length=200)),
                ('telephone_famille', models.CharField(blank=True, max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Défunt',
                'verbose_name_plural': 'Défunts',
                'ordering': ['-date_deces'],
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(db_index=True, max_length=20, unique=True)),
                ('type_concession', models.CharField(choices=[('TEMPORAIRE', 'Temporaire (5 ans)'), ('TRENTENAIRE', 'Trentenaire (30 ans)'), ('PERPETUELLE', 'Perpétuelle'), ('FAMILIALE', 'Familiale')], max_length=20)),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente de validation'), ('VALIDEE', 'Validée'), ('REFUSEE', 'Refusée'), ('ANNULEE', 'Annulée'), ('EXPIREE', 'Expirée')], db_index=True, default='EN_ATTENTE', max_length=15)),
                ('montant_total_xaf', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('date_soumission', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_validation', models.DateTimeField(blank=True, null=True)),
                ('date_refus', models.DateTimeField(blank=True, null=True)),
                ('notes_client', models.TextField(blank=True)),
                ('motif_refus', models.TextField(blank=True)),
                ('notes_admin', models.TextField(blank=True)),
                ('facture_pdf', models.FileField(blank=True, null=True, upload_to='factures/')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations_client', to='auth_app.utilisateur')),
                ('agent_validation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reservations_validees', to='auth_app.utilisateur')),
                ('caveau', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to='caveaux.caveau')),
                ('defunt', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='reservation', to='reservations.defunt')),
            ],
            options={
                'verbose_name': 'Réservation',
                'verbose_name_plural': 'Réservations',
                'ordering': ['-date_soumission'],
            },
        ),
    ]