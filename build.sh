#!/usr/bin/env bash
# Script de build pour Render
set -o errexit

echo "🚀 Démarrage du build BOITE-VIRO..."
echo "🐍 Version Python: $(python --version)"

# Mise à jour de pip
echo "⬆️ Mise à jour de pip..."
pip install --upgrade pip

# Installation des dépendances Python
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Collecte des fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

# Migrations de la base de données
echo "🗄️ Application des migrations..."
python manage.py migrate --no-input

# Note: Les données existantes sont préservées dans PostgreSQL
# Les migrations ne suppriment jamais les données existantes

echo "✅ Build terminé avec succès !"