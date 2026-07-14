from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth_app', '0001_initial'),
        ('caveaux', '0001_initial'),
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Concession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_contrat', models.CharField(db_index=True, max_length=30, unique=True)),
                ('type_concession', models.CharField(choices=[('TEMPORAIRE', 'Temporaire (5 ans)'), ('TRENTENAIRE', 'Trentenaire (30 ans)'), ('PERPETUELLE', 'Perpétuelle'), ('FAMILIALE', 'Familiale perpétuelle')], max_length=20)),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField(blank=True, null=True)),
                ('date_alerte_renouvellement', models.DateField(blank=True, null=True)),
                ('nombre_renouvellements', models.PositiveIntegerField(default=0)),
                ('statut', models.CharField(choices=[('ACTIVE', 'Active'), ('EN_RENOUVELLEMENT', 'En cours de renouvellement'), ('EXPIREE', 'Expirée'), ('RESILIEE', 'Résiliée')], db_index=True, default='ACTIVE', max_length=20)),
                ('montant_initial_xaf', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('montant_renouvellement_xaf', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('contrat_pdf', models.FileField(blank=True, null=True, upload_to='concessions/')),
                ('date_resiliation', models.DateField(blank=True, null=True)),
                ('motif_resiliation', models.TextField(blank=True)),
                ('beneficiaires_json', models.JSONField(default=list)),
                ('notes', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('caveau', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='concessions', to='caveaux.caveau')),
                ('titulaire', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='concessions', to='auth_app.utilisateur')),
                ('reservation_origine', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='concession', to='reservations.reservation')),
                ('resilie_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='concessions_resiliees', to='auth_app.utilisateur')),
            ],
            options={
                'verbose_name': 'Concession',
                'verbose_name_plural': 'Concessions',
                'ordering': ['-date_debut'],
            },
        ),
        migrations.CreateModel(
            name='RenouvellementConcession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_ancienne_fin', models.DateField()),
                ('date_nouvelle_fin', models.DateField()),
                ('montant_xaf', models.DecimalField(decimal_places=0, max_digits=12)),
                ('date_traitement', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('concession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='renouvellements', to='concessions.concession')),
                ('traite_par', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth_app.utilisateur')),
            ],
            options={
                'verbose_name': 'Renouvellement',
                'ordering': ['-date_traitement'],
            },
        ),
    ]