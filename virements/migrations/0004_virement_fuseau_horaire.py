from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virements', '0003_banque_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='virement',
            name='fuseau_horaire',
            field=models.CharField(
                choices=[
                    ('Europe/Paris',       'Europe/Paris (CET/CEST)'),
                    ('Europe/London',      'Europe/London (GMT/BST)'),
                    ('Europe/Berlin',      'Europe/Berlin (CET/CEST)'),
                    ('Europe/Madrid',      'Europe/Madrid (CET/CEST)'),
                    ('Europe/Rome',        'Europe/Rome (CET/CEST)'),
                    ('Europe/Amsterdam',   'Europe/Amsterdam (CET/CEST)'),
                    ('Europe/Brussels',    'Europe/Brussels (CET/CEST)'),
                    ('Europe/Warsaw',      'Europe/Warsaw (CET/CEST)'),
                    ('Europe/Moscow',      'Europe/Moscow (MSK)'),
                    ('Europe/Zurich',      'Europe/Zurich (CET/CEST)'),
                    ('Africa/Abidjan',     'Africa/Abidjan (GMT)'),
                    ('Africa/Dakar',       'Africa/Dakar (GMT)'),
                    ('Africa/Lagos',       'Africa/Lagos (WAT)'),
                    ('Africa/Nairobi',     'Africa/Nairobi (EAT)'),
                    ('Africa/Casablanca',  'Africa/Casablanca (WET)'),
                    ('Africa/Algiers',     'Africa/Algiers (CET)'),
                    ('Africa/Cairo',       'Africa/Cairo (EET)'),
                    ('Africa/Kinshasa',    'Africa/Kinshasa (WAT)'),
                    ('Africa/Douala',      'Africa/Douala (WAT)'),
                    ('America/New_York',   'America/New_York (EST/EDT)'),
                    ('America/Chicago',    'America/Chicago (CST/CDT)'),
                    ('America/Denver',     'America/Denver (MST/MDT)'),
                    ('America/Los_Angeles','America/Los_Angeles (PST/PDT)'),
                    ('America/Toronto',    'America/Toronto (EST/EDT)'),
                    ('America/Montreal',   'America/Montreal (EST/EDT)'),
                    ('America/Sao_Paulo',  'America/Sao_Paulo (BRT)'),
                    ('America/Buenos_Aires','America/Buenos_Aires (ART)'),
                    ('Asia/Dubai',         'Asia/Dubai (GST)'),
                    ('Asia/Riyadh',        'Asia/Riyadh (AST)'),
                    ('Asia/Shanghai',      'Asia/Shanghai (CST)'),
                    ('Asia/Tokyo',         'Asia/Tokyo (JST)'),
                    ('Asia/Kolkata',       'Asia/Kolkata (IST)'),
                    ('Asia/Singapore',     'Asia/Singapore (SGT)'),
                    ('UTC',                'UTC'),
                ],
                default='UTC',
                max_length=50,
                verbose_name='Fuseau horaire',
            ),
        ),
    ]
