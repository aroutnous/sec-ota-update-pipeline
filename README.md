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
keys/      public.pem (versionnee) ; la cle privee reste locale, ignoree par git
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

A completer au fur et a mesure (commandes pour generer les cles, lancer le serveur,
lancer le client, rejouer les attaques, lancer les tests).

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
