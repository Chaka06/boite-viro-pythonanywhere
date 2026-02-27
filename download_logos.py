"""
Script de téléchargement des logos de banques pour les emails.
Usage : python download_logos.py
"""
import os
import urllib.request

LOGOS_DIR = os.path.join(os.path.dirname(__file__), 'media', 'logos')
os.makedirs(LOGOS_DIR, exist_ok=True)

LOGOS = {
    'bnp_paribas.png':       'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/BNP_Paribas_logo.svg/320px-BNP_Paribas_logo.svg.png',
    'credit_agricole.png':   'https://upload.wikimedia.org/wikipedia/fr/thumb/0/0e/Cr%C3%A9dit_Agricole_logo.svg/320px-Cr%C3%A9dit_Agricole_logo.svg.png',
    'bnp_paribas_fortis.png':'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/BNP_Paribas_logo.svg/320px-BNP_Paribas_logo.svg.png',
    'credit_mutuel.png':     'https://upload.wikimedia.org/wikipedia/fr/thumb/4/4a/Cr%C3%A9dit_Mutuel_logo.svg/320px-Cr%C3%A9dit_Mutuel_logo.svg.png',
    'credit_suisse.png':     'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Credit_Suisse_Logo.svg/320px-Credit_Suisse_Logo.svg.png',
    'credit_lyonnais.png':   'https://upload.wikimedia.org/wikipedia/fr/thumb/5/5a/Cr%C3%A9dit_Lyonnais_logo.svg/320px-Cr%C3%A9dit_Lyonnais_logo.svg.png',
    'banque_populaire.png':  'https://upload.wikimedia.org/wikipedia/fr/thumb/8/8e/Banque_Populaire_logo.svg/320px-Banque_Populaire_logo.svg.png',
    'societe_generale.png':  'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Soci%C3%A9t%C3%A9_G%C3%A9n%C3%A9rale_logo.svg/320px-Soci%C3%A9t%C3%A9_G%C3%A9n%C3%A9rale_logo.svg.png',
    'intesa_sanpaolo.png':   'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Intesa_Sanpaolo_logo.svg/320px-Intesa_Sanpaolo_logo.svg.png',
    'deutsche_bank.png':     'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Deutsche_Bank_logo.svg/320px-Deutsche_Bank_logo.svg.png',
    'hsbc.png':              'https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/HSBC_logo_%282018%29.svg/320px-HSBC_logo_%282018%29.svg.png',
    'barclays.png':          'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Barclays_Bank_logo.svg/320px-Barclays_Bank_logo.svg.png',
    'citibank.png':          'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Citibank.svg/320px-Citibank.svg.png',
    'ubs.png':               'https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/UBS_logo.svg/320px-UBS_logo.svg.png',
    'ing_bank.png':          'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/ING_Group_logo.svg/320px-ING_Group_logo.svg.png',
}

headers = {'User-Agent': 'Mozilla/5.0'}

print(f"Dossier cible : {LOGOS_DIR}\n")
ok, fail = [], []

for filename, url in LOGOS.items():
    dest = os.path.join(LOGOS_DIR, filename)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        size = len(data)
        if size < 2000:
            fail.append((filename, f'Fichier trop petit ({size} octets) — URL invalide'))
            continue
        with open(dest, 'wb') as f:
            f.write(data)
        ok.append((filename, size))
        print(f"  OK  {filename:35s}  {size//1024} KB")
    except Exception as e:
        fail.append((filename, str(e)))
        print(f"  ERR {filename:35s}  {e}")

print(f"\n--- Résumé ---")
print(f"Succès : {len(ok)}/{len(LOGOS)}")
if fail:
    print("Échecs :")
    for name, reason in fail:
        print(f"  - {name}: {reason}")
