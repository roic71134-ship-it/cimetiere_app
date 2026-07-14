from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth_app', '0001_initial'),
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_xaf', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='Montant (FCFA)')),
                ('canal', models.CharField(choices=[('ESPECES', 'Espèces'), ('AIRTEL_MONEY', 'Airtel Money'), ('MTN_MOMO', 'MTN Mobile Money'), ('VIREMENT', 'Virement bancaire'), ('CHEQUE', 'Chèque')], max_length=20, verbose_name='Canal de paiement')),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('CONFIRME', 'Confirmé'), ('ECHEC', 'Échec'), ('REMBOURSE', 'Remboursé')], db_index=True, default='EN_ATTENTE', max_length=15)),
                ('reference', models.CharField(blank=True, max_length=100, verbose_name='Référence de transaction')),
                ('numero_transaction', models.CharField(blank=True, max_length=100, verbose_name='Numéro de transaction')),
                ('notes', models.TextField(blank=True)),
                ('date_paiement', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_confirmation', models.DateTimeField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('reservation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='paiements', to='reservations.reservation')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='paiements', to='auth_app.utilisateur')),
                ('enregistre_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='paiements_enregistres', to='auth_app.utilisateur')),
            ],
            options={
                'verbose_name': 'Paiement',
                'verbose_name_plural': 'Paiements',
                'ordering': ['-date_paiement'],
            },
        ),
    ]