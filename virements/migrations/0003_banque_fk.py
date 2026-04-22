from django.db import migrations, models
import django.db.models.deletion


BANQUES_INITIALES = [
    # ── Banques existantes ──────────────────────────────────────────────
    {
        'code': 'bnp_paribas', 'nom': 'BNP Paribas',
        'couleur_principale': '#009652', 'couleur_secondaire': '#0066CC',
        'slogan': "La banque d'un monde qui change",
        'numero_enregistrement': 'RCS Paris 662 042 449',
        'siege_social': '16, boulevard des Italiens — 75009 Paris',
    },
    {
        'code': 'credit_agricole', 'nom': 'Crédit Agricole S.A.',
        'couleur_principale': '#009682', 'couleur_secondaire': '#0066CC',
        'slogan': "La banque qui a du sens",
        'numero_enregistrement': 'RCS Paris 784 608 416',
        'siege_social': '12, place des États-Unis — 92127 Montrouge Cedex',
    },
    {
        'code': 'bnp_paribas_fortis', 'nom': 'BNP Paribas Fortis',
        'couleur_principale': '#0064B4', 'couleur_secondaire': '#004D8A',
        'slogan': "La banque d'un monde qui change",
        'numero_enregistrement': 'RCS Bruxelles 403 199 702',
        'siege_social': 'Montagne du Parc 3 — 1000 Bruxelles, Belgique',
    },
    {
        'code': 'credit_mutuel', 'nom': 'Crédit Mutuel',
        'couleur_principale': '#0050A0', 'couleur_secondaire': '#003D7D',
        'slogan': "La banque qui vous ressemble",
        'numero_enregistrement': 'RCS Strasbourg 588 505 354',
        'siege_social': '34, rue du Wacken — 67000 Strasbourg',
    },
    {
        'code': 'credit_suisse', 'nom': 'Crédit Suisse AG',
        'couleur_principale': '#C8102E', 'couleur_secondaire': '#A00D24',
        'slogan': "Banking on Switzerland",
        'numero_enregistrement': 'CHE-106.831.974',
        'siege_social': 'Paradeplatz 8 — 8070 Zürich, Suisse',
    },
    {
        'code': 'credit_lyonnais', 'nom': 'Crédit Lyonnais (LCL)',
        'couleur_principale': '#003C78', 'couleur_secondaire': '#002D5A',
        'slogan': "La banque qui vous ressemble",
        'numero_enregistrement': 'RCS Paris 954 509 741',
        'siege_social': '20, avenue de Paris — 94811 Villejuif Cedex',
    },
    {
        'code': 'banque_populaire', 'nom': 'Banque Populaire',
        'couleur_principale': '#C83232', 'couleur_secondaire': '#A02828',
        'slogan': "La banque coopérative",
        'numero_enregistrement': 'RCS Paris 552 002 313',
        'siege_social': '50, avenue Pierre Mendès France — 75013 Paris',
    },
    {
        'code': 'societe_generale', 'nom': 'Société Générale',
        'couleur_principale': '#C80000', 'couleur_secondaire': '#A00000',
        'slogan': "La banque qui vous accompagne",
        'numero_enregistrement': 'RCS Paris 552 120 222',
        'siege_social': '29, boulevard Haussmann — 75009 Paris',
    },
    {
        'code': 'intesa_sanpaolo', 'nom': 'Intesa Sanpaolo S.p.A.',
        'couleur_principale': '#003D82', 'couleur_secondaire': '#002D5F',
        'slogan': "La banca che ti ascolta",
        'numero_enregistrement': 'REA MI-1584927',
        'siege_social': 'Piazza San Carlo 156 — 10121 Torino, Italia',
    },
    {
        'code': 'deutsche_bank', 'nom': 'Deutsche Bank AG',
        'couleur_principale': '#0018A8', 'couleur_secondaire': '#001066',
        'slogan': "Leading to a better future",
        'numero_enregistrement': 'HRB 71118 — Amtsgericht Frankfurt',
        'siege_social': 'Taunusanlage 12 — 60325 Frankfurt am Main',
    },
    {
        'code': 'hsbc', 'nom': 'HSBC Bank PLC',
        'couleur_principale': '#DB0011', 'couleur_secondaire': '#B0000E',
        'slogan': "The world's local bank",
        'numero_enregistrement': 'Company No. 14259',
        'siege_social': '8 Canada Square — London E14 5HQ, United Kingdom',
    },
    {
        'code': 'barclays', 'nom': 'Barclays Bank PLC',
        'couleur_principale': '#00AEEF', 'couleur_secondaire': '#0088CC',
        'slogan': "Now there's a thought",
        'numero_enregistrement': 'Company No. 1026167',
        'siege_social': '1 Churchill Place — London E14 5HP, United Kingdom',
    },
    {
        'code': 'citibank', 'nom': 'Citibank N.A.',
        'couleur_principale': '#1B4F9B', 'couleur_secondaire': '#0F3A6B',
        'slogan': "Citi never sleeps",
        'numero_enregistrement': 'FDIC # 7213',
        'siege_social': '388 Greenwich Street — New York, NY 10013, USA',
    },
    {
        'code': 'ubs', 'nom': 'UBS AG',
        'couleur_principale': '#E0001B', 'couleur_secondaire': '#B00015',
        'slogan': "Your world. Your ambitions. Our commitment.",
        'numero_enregistrement': 'CHE-101.329.561',
        'siege_social': 'Bahnhofstrasse 45 — 8098 Zürich, Suisse',
    },
    {
        'code': 'ing_bank', 'nom': 'ING Bank N.V.',
        'couleur_principale': '#FF6200', 'couleur_secondaire': '#CC4E00',
        'slogan': "Do your thing",
        'numero_enregistrement': 'KvK 33031431',
        'siege_social': 'Bijlmerplein 888 — 1102 MG Amsterdam, Pays-Bas',
    },
    # ── Banques belges ──────────────────────────────────────────────────
    {
        'code': 'belfius', 'nom': 'Belfius Banque & Assurances',
        'couleur_principale': '#CC0066', 'couleur_secondaire': '#A30052',
        'slogan': "Proche de vous",
        'numero_enregistrement': 'BE 0403.201.185',
        'siege_social': 'Boulevard Pachéco 44 — 1000 Bruxelles, Belgique',
    },
    {
        'code': 'kbc', 'nom': 'KBC Bank NV',
        'couleur_principale': '#009DE0', 'couleur_secondaire': '#007DB5',
        'slogan': "More than banking",
        'numero_enregistrement': 'RPM Bruxelles BE 0462.920.226',
        'siege_social': 'Havenlaan 2 — 1080 Bruxelles, Belgique',
    },
    {
        'code': 'cbc', 'nom': 'CBC Banque & Assurance',
        'couleur_principale': '#E4002B', 'couleur_secondaire': '#B30022',
        'slogan': "Votre banque de référence",
        'numero_enregistrement': 'RPM Namur 0403.211.380',
        'siege_social': 'Grand-Place de Loverval 1 — 6280 Gerpinnes, Belgique',
    },
    {
        'code': 'beobank', 'nom': 'Beobank NV/SA',
        'couleur_principale': '#00529B', 'couleur_secondaire': '#003E74',
        'slogan': "Better banking",
        'numero_enregistrement': 'RPM Bruxelles 0401.517.147',
        'siege_social': "Rue d'Arlon 80 — 1040 Bruxelles, Belgique",
    },
    {
        'code': 'crelan', 'nom': 'Crelan SA',
        'couleur_principale': '#009A44', 'couleur_secondaire': '#007A36',
        'slogan': "La banque coopérative belge",
        'numero_enregistrement': 'RPM Bruxelles 0256.807.963',
        'siege_social': 'Sylvain Dupuislaan 251 — 1070 Bruxelles, Belgique',
    },
    {
        'code': 'argenta', 'nom': 'Argenta Spaarbank NV',
        'couleur_principale': '#1A3668', 'couleur_secondaire': '#142850',
        'slogan': "Puur bankieren",
        'numero_enregistrement': 'RPM Antwerpen 0404.453.574',
        'siege_social': 'Belgiëlei 49-53 — 2018 Antwerpen, Belgique',
    },
    {
        'code': 'vdk', 'nom': 'VDK Bank NV',
        'couleur_principale': '#00833E', 'couleur_secondaire': '#006630',
        'slogan': "De bank voor een eerlijke economie",
        'numero_enregistrement': 'RPM Gent 0415.490.334',
        'siege_social': 'Sint-Michielsplein 16 — 9000 Gent, Belgique',
    },
    {
        'code': 'ing_belgique', 'nom': 'ING Belgique SA',
        'couleur_principale': '#FF6200', 'couleur_secondaire': '#CC4E00',
        'slogan': "Do your thing",
        'numero_enregistrement': 'RPM Bruxelles 0403.200.393',
        'siege_social': 'Avenue Marnix 24 — 1000 Bruxelles, Belgique',
    },
]


def create_banques(apps, schema_editor):
    Banque = apps.get_model('virements', 'Banque')
    for data in BANQUES_INITIALES:
        Banque.objects.get_or_create(code=data['code'], defaults=data)


def migrate_banque_emettrice(apps, schema_editor):
    Virement = apps.get_model('virements', 'Virement')
    Banque = apps.get_model('virements', 'Banque')

    fallback, _ = Banque.objects.get_or_create(
        code='inconnue',
        defaults={
            'nom': 'Banque inconnue',
            'couleur_principale': '#0066CC',
            'couleur_secondaire': '#0056B3',
        }
    )

    for virement in Virement.objects.all():
        try:
            banque = Banque.objects.get(code=virement.banque_emettrice_old)
        except Banque.DoesNotExist:
            banque = fallback
        virement.banque_emettrice = banque
        virement.save()


class Migration(migrations.Migration):

    dependencies = [
        ('virements', '0002_alter_virement_banque_emettrice_alter_virement_langue'),
    ]

    operations = [
        # 1. Créer le modèle Banque
        migrations.CreateModel(
            name='Banque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom de la banque')),
                ('code', models.SlugField(max_length=50, unique=True, verbose_name='Code unique')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/', verbose_name='Logo')),
                ('couleur_principale', models.CharField(default='#0066CC', max_length=7, verbose_name='Couleur principale')),
                ('couleur_secondaire', models.CharField(default='#0056B3', max_length=7, verbose_name='Couleur secondaire')),
                ('slogan', models.CharField(blank=True, max_length=200, verbose_name='Slogan')),
                ('numero_enregistrement', models.CharField(blank=True, max_length=100, verbose_name="Numéro d'enregistrement")),
                ('siege_social', models.CharField(blank=True, max_length=200, verbose_name='Siège social')),
                ('actif', models.BooleanField(default=True, verbose_name='Banque active')),
            ],
            options={
                'verbose_name': 'Banque',
                'verbose_name_plural': 'Banques',
                'ordering': ['nom'],
            },
        ),

        # 2. Peupler les banques
        migrations.RunPython(create_banques, reverse_code=migrations.RunPython.noop),

        # 3. Renommer l'ancien champ pour libérer le nom
        migrations.RenameField(
            model_name='virement',
            old_name='banque_emettrice',
            new_name='banque_emettrice_old',
        ),

        # 4. Ajouter le nouveau champ FK (nullable pour la migration)
        migrations.AddField(
            model_name='virement',
            name='banque_emettrice',
            field=models.ForeignKey(
                'virements.Banque',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='virements',
                verbose_name='Banque émettrice',
            ),
        ),

        # 5. Copier les données
        migrations.RunPython(migrate_banque_emettrice, reverse_code=migrations.RunPython.noop),

        # 6. Rendre le FK obligatoire
        migrations.AlterField(
            model_name='virement',
            name='banque_emettrice',
            field=models.ForeignKey(
                'virements.Banque',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='virements',
                verbose_name='Banque émettrice',
            ),
        ),

        # 7. Supprimer l'ancien champ
        migrations.RemoveField(
            model_name='virement',
            name='banque_emettrice_old',
        ),
    ]
