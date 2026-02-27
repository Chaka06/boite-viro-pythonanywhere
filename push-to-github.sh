#!/bin/bash
# Script pour pousser le code vers GitHub
# Usage: ./push-to-github.sh

set -e

echo "Préparation du push vers GitHub..."
echo ""

# Vérifier si Git est initialisé
if [ ! -d .git ]; then
    echo "Initialisation de Git..."
    git init
fi

# Ajouter le remote (ou le mettre à jour)
echo "Configuration du remote GitHub..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/Chaka06/boite-viro-pythonanywhere.git

# Vérifier les fichiers à committer
echo ""
echo "Fichiers modifiés:"
git status --short

# Demander confirmation
echo ""
read -p "Voulez-vous continuer le commit et push? (o/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
    echo "Opération annulée"
    exit 1
fi

# Ajouter tous les fichiers
echo "Ajout des fichiers..."
git add .

# Faire le commit
echo "Création du commit..."
git commit -m "Mise à jour" || {
    echo "Aucun changement à committer"
    exit 0
}

# Pousser vers GitHub
echo "Push vers GitHub..."
git push -u origin main

echo ""
echo "Push terminé avec succès!"
echo "Code sur: https://github.com/Chaka06/boite-viro-pythonanywhere"
