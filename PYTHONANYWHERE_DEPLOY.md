# Guide de déploiement — PythonAnywhere (Developer $10/mois)

## Vue d'ensemble

- Base de données : SQLite (persistant sur PythonAnywhere)
- Serveur : géré par PythonAnywhere (pas besoin de gunicorn)
- Fichiers statiques : WhiteNoise + mapping PA dashboard
- Fichiers media (PDFs) : persistants sur le disque PA

---

## ÉTAPE 1 — Ouvrir une console Bash sur PythonAnywhere

Dashboard → Consoles → Bash

---

## ÉTAPE 2 — Cloner le dépôt GitHub

```bash
cd ~
git clone https://github.com/Chaka06/boite-viro-pythonanywhere.git boite-viro
cd boite-viro
```

---

## ÉTAPE 3 — Créer l'environnement virtuel Python

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ÉTAPE 4 — Créer le fichier .env

```bash
nano .env
```

Coller ce contenu (adapter les valeurs) :

```
SECRET_KEY=remplacer-par-une-cle-secrete-longue-et-aleatoire
DEBUG=False
ALLOWED_HOSTS=VOTRE_USERNAME.pythonanywhere.com
SECURE_SSL_REDIRECT=False

EMAIL_HOST=mail.virement.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=support@virement.net
EMAIL_HOST_PASSWORD=votre_mot_de_passe_smtp
DEFAULT_FROM_EMAIL=support@virement.net
SERVER_EMAIL=support@virement.net
ADMIN_EMAIL=support@virement.net
```

Générer une SECRET_KEY :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## ÉTAPE 5 — Initialiser la base de données

```bash
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic --no-input
```

---

## ÉTAPE 6 — Créer le superutilisateur

```bash
python manage.py createsuperuser
```

---

## ÉTAPE 7 — Configurer l'application Web sur PythonAnywhere

Dashboard → Web → Add a new web app → Manual configuration → Python 3.11

### 7.1 — Virtualenv

Dans la section "Virtualenv" :
```
/home/VOTRE_USERNAME/boite-viro/venv
```

### 7.2 — Fichier WSGI

Cliquer sur le lien du fichier WSGI configuration file et remplacer tout le contenu par celui de `pythonanywhere_wsgi.py` (dans le repo), en remplaçant VOTRE_USERNAME.

### 7.3 — Fichiers statiques (Static files)

Ajouter ces deux mappings dans la section "Static files" :

| URL      | Directory                                          |
|----------|----------------------------------------------------|
| /static/ | /home/VOTRE_USERNAME/boite-viro/staticfiles        |
| /media/  | /home/VOTRE_USERNAME/boite-viro/media              |

---

## ÉTAPE 8 — Recharger l'application

Cliquer sur le bouton vert "Reload" dans le dashboard Web.

Votre application est accessible sur :
```
https://VOTRE_USERNAME.pythonanywhere.com
```

---

## Mise à jour du code (après modifications)

```bash
cd ~/boite-viro
source venv/bin/activate
git pull origin main
pip install -r requirements.txt   # si requirements changés
python manage.py migrate           # si nouvelles migrations
python manage.py collectstatic --no-input
```

Puis cliquer "Reload" dans le dashboard Web.

---

## Dépannage

### Voir les logs d'erreur
Dashboard → Web → Log files → Error log

### Tester la config SMTP depuis la console
```bash
cd ~/boite-viro
source venv/bin/activate
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail('Test', 'Message test', 'support@virement.net', ['votre@email.com'])
```

### Vérifier les migrations
```bash
python manage.py showmigrations
```
