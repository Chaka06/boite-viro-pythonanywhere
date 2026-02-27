# ============================================================
# FICHIER WSGI POUR PYTHONANYWHERE
# ============================================================
# Copiez-collez ce contenu dans le fichier WSGI de PythonAnywhere :
# Web > (votre app) > Code > WSGI configuration file
#
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur PythonAnywhere
# ============================================================

import sys
import os

# Chemin vers votre projet (remplacer VOTRE_USERNAME)
path = '/home/VOTRE_USERNAME/boite-viro'
if path not in sys.path:
    sys.path.insert(0, path)

# Se placer dans le répertoire du projet pour que python-decouple
# trouve le fichier .env automatiquement
os.chdir(path)

# Module de settings Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'boite_viro.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
