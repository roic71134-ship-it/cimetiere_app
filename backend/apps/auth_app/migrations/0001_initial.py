from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(choices=[('ADMIN', 'Administrateur'), ('AGENT', 'Agent de terrain'), ('SECRETARIAT', 'Secrétariat'), ('CLIENT', 'Client')], max_length=20, unique=True)),
                ('peut_valider_reservations', models.BooleanField(default=False)),
                ('peut_modifier_carte', models.BooleanField(default=False)),
                ('peut_voir_finances', models.BooleanField(default=False)),
                ('peut_gerer_concessions', models.BooleanField(default=False)),
                ('peut_gerer_exhumations', models.BooleanField(default=False)),
                ('peut_enregistrer_paiements', models.BooleanField(default=False)),
                ('peut_exporter_donnees', models.BooleanField(default=False)),
                ('peut_voir_audit', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Rôle',
                'verbose_name_plural': 'Rôles',
            },
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('adresse', models.TextField(blank=True)),
                ('est_actif', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('mfa_active', models.BooleanField(default=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('derniere_connexion_app', models.DateTimeField(blank=True, null=True)),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='utilisateurs', to='auth_app.role')),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Utilisateur',
                'verbose_name_plural': 'Utilisateurs',
            },
        ),
        migrations.CreateModel(
            name='SessionMFA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('expire_a', models.DateTimeField()),
                ('est_utilise', models.BooleanField(default=False)),
                ('adresse_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('cree_le', models.DateTimeField(auto_now_add=True)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions_mfa', to='auth_app.utilisateur')),
            ],
            options={
                'verbose_name': 'Session MFA',
            },
        ),
    ]