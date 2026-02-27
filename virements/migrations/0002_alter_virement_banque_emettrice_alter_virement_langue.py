from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virements', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virement',
            name='banque_emettrice',
            field=models.CharField(
                choices=[
                    ('bnp_paribas', 'BNP Paribas'),
                    ('credit_agricole', 'Crédit Agricole'),
                    ('bnp_paribas_fortis', 'BNP Paribas Fortis'),
                    ('credit_mutuel', 'Crédit Mutuel'),
                    ('credit_suisse', 'Crédit Suisse'),
                    ('credit_lyonnais', 'Crédit Lyonnais'),
                    ('banque_populaire', 'Banque Populaire'),
                    ('societe_generale', 'Société Générale'),
                    ('intesa_sanpaolo', 'Intesa Sanpaolo'),
                    ('deutsche_bank', 'Deutsche Bank'),
                    ('hsbc', 'HSBC'),
                    ('barclays', 'Barclays'),
                    ('citibank', 'Citibank'),
                    ('ubs', 'UBS'),
                    ('ing_bank', 'ING Bank'),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name='virement',
            name='langue',
            field=models.CharField(
                choices=[
                    ('fr', 'Français'),
                    ('en', 'English'),
                    ('es', 'Español'),
                    ('it', 'Italiano'),
                    ('de', 'Deutsch'),
                    ('pl', 'Polski'),
                    ('ru', 'Русский'),
                    ('pt', 'Português'),
                    ('ar', 'العربية'),
                    ('zh', '中文'),
                ],
                default='fr',
                max_length=2,
            ),
        ),
    ]
