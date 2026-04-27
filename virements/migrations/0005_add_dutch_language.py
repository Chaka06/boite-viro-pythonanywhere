from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virements', '0004_virement_fuseau_horaire'),
    ]

    operations = [
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
                    ('nl', 'Nederlands'),
                ],
                default='fr',
                max_length=2,
            ),
        ),
    ]
