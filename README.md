# Secure OTA Update Pipeline

Capstone S9 - HESTIM Engineering School - 5A-IIA-Cybersecurite - Projet 3 (A2)
Encadrant : Dr. Sridath TULA

Prototype d'un pipeline de mise a jour OTA (over-the-air) securisé pour un robot simulé.
Le robot n'installe une mise a jour que si elle est **authentique** (signature RSA-PSS),
**integre** (hash SHA-256) et **recente** (version superieure a la derniere appliquee).

## Equipe

1. Landry BAMBARA
2. Niagale TRAORE
3. Amara SOUNTOURA
4. Killian OUASSENAN

## Structure du depot

```
server/    serveur Flask (/latest_version, /download) et constructeur de paquet
client/    client robot : verification signature, hash, version ; audit log
attacks/   scripts des 5 attaques
proxy/     proxy man-in-the-middle (attaque 5)
tests/     tests automatises et test de controle
keys/      vide dans Git : chacun genere sa paire en local (decision 8)
docs/      specifications, security design document, fiches d'attaque, rapport
scripts/   utilitaires (creation des issues GitHub)
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

Toutes les commandes se lancent depuis la racine du depot, environnement active
(sous macOS, `python3` si `python` n'existe pas). Ports : serveur 5001, proxy 8080 (decision 9).

````bash
# 1. Cles, une seule fois, en local (jamais dans Git)
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

# 2. Publier des mises a jour signees (server/packages/)
python -m server.package_builder --version 1 --text "firmware v1"
python -m server.package_builder --version 2 --text "firmware v2"

# 3. Terminal 1 : le serveur (http://127.0.0.1:5001)
python -m server.app

# 4. Terminal 2 : le robot (etat, journal et logiciel installe dans client/)
python -m client.robot
cat client/state.json client/audit.log

# 5. Terminal 3 : le proxy MITM, puis le robot passe par lui
python -m proxy.mitm_proxy --mode tamper-content     # ou transparent, drop
python -m client.robot --server http://127.0.0.1:8080

# 6. Tests automatiques (controle + attaques)
python -m pytest -v
```

## Les 5 attaques testees

1. Paquet non signe
2. Paquet modifie
3. Replay (ancien paquet valide)
4. Downgrade (version plus ancienne)
5. Man-in-the-middle (telechargement intercepte)

Criteres de succes : 5/5 attaques rejetees, 0 mise a jour falsifiee appliquee,
1 mise a jour valide acceptee.

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).
