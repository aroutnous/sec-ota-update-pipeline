# Rapport technique - Partie R2 (Niagale TRAORE)

> Sections 3.2, 3.3 et 7 du rapport, et réflexion personnelle 8.2.
> Sources : `docs/client-checks.md`, `client/verify.py`, `client/state.py`,
> `client/audit.py`, `client/robot.py`, `scripts/demo.py`, `README.md`,
> section 9 de `docs/security-design.md`.

### 3.2 Client robot, état et journal d'audit (R2)

**Vérification** (`client/verify.py`, 83 lignes). La fonction `verify_package`
applique les quatre contrôles dans l'ordre fixé (forme, signature, hash, version)
et renvoie un code ; le contenu n'est rendu que si le code vaut `ACCEPTED`. Ce
fichier n'importe rien du serveur : il redéfinit lui-même le calcul des 36 octets
signés et ne connaît que la clé publique. Le robot et le serveur ne partagent donc
qu'une spécification, pas du code.

**Cycle de mise à jour** (`client/robot.py`, 89 lignes). À chaque passage, le robot :

1. demande `GET /latest_version`. Ce numéro n'est qu'une indication : il sert à
   savoir s'il y a quelque chose à télécharger, jamais à décider ;
2. télécharge le paquet annoncé avec `GET /download?version=N` (délai maximal de 5 s,
   pour qu'un serveur muet ne bloque pas le robot) ;
3. fait vérifier le paquet. **La version comparée est celle signée dans le paquet**,
   pas celle annoncée par le serveur ;
4. si le paquet est accepté : installe le logiciel (`client/installed/firmware.bin`),
   puis enregistre l'état, puis écrit la ligne de journal, dans cet ordre.

Si la version annoncée n'est pas plus récente, le robot répond `UP_TO_DATE` sans
rien télécharger ni journaliser. Si le serveur est injoignable, il journalise
`NETWORK_ERROR` et n'installe rien.

**État persistant** (`client/state.py`). Le fichier `client/state.json` contient
`{"last_applied_version": N}` (0 au premier démarrage). Il n'est écrit qu'après une
installation réussie, de façon atomique : écriture dans `state.json.tmp`, `fsync`
pour forcer l'écriture sur le disque, puis `os.replace`, qui remplace l'ancien
fichier en une seule opération. Une coupure laisse l'ancien ou le nouveau fichier
complet, jamais un fichier à moitié écrit. Si le fichier est illisible, le robot
s'arrête au lieu de repartir de 0 : repartir de 0 rouvrirait la porte au downgrade.

**Journal d'audit** (`client/audit.py`). Une ligne JSON par décision, ajoutée à la
fin du fichier (mode « ajout » seulement) : heure UTC, version (`null` si
illisible), décision (`ACCEPTED`, `REJECTED` ou `ERROR`) et raison (le code).
Exemple réel, produit pendant la démonstration de l'équipe du 17 octobre (robot neuf,
puis proxy en mode `tamper-content`, puis proxy `transparent` après publication d'une v3,
puis proxy en mode `drop`) :

```
{"ts": "2026-10-17T22:09:22Z", "version": 2, "decision": "ACCEPTED", "reason": "ACCEPTED"}
{"ts": "2026-10-17T22:12:36Z", "version": 3, "decision": "REJECTED", "reason": "HASH_MISMATCH"}
{"ts": "2026-10-17T22:13:14Z", "version": 3, "decision": "ACCEPTED", "reason": "ACCEPTED"}
{"ts": "2026-10-17T22:14:13Z", "version": null, "decision": "ERROR", "reason": "NETWORK_ERROR"}
```

**Tests du robot** : 5 tests dans `tests/test_robot.py` (mise à jour légitime,
déjà à jour, état conservé après redémarrage, serveur injoignable, écriture de l'état).

### 3.3 Reproductibilité et démonstration (R2)

Le README donne les commandes d'installation et d'utilisation, et la suite de
tests se lance en une commande : `python -m pytest -v` (22 tests).

Le script `scripts/demo.py` rejoue le chemin légitime en une seule commande,
`python -m scripts.demo`, sans ouvrir plusieurs terminaux ni utiliser de clé
personnelle : il crée une paire de clés en mémoire, publie v1 et v2 dans un dossier
temporaire, lance le vrai serveur sur un port libre, puis fait tourner le robot.
Sortie attendue : `ACCEPTED` (v2), `UP_TO_DATE`, puis `ACCEPTED` (v3) après la
publication d'une v3, et enfin le logiciel installé et le journal d'audit. Le
script a été vérifié sur la branche `main` au moment du tag `v0.2`.

## 7. Limites et pistes d'amélioration

Le système empêche l'installation d'une fausse mise à jour dans notre modèle
d'attaquant. Il ne couvre pas tout, et nous préférons le dire :

| Limite | Pourquoi | Ce qu'on ferait en production |
| --- | --- | --- |
| Déni de service | Un attaquant au milieu peut bloquer les réponses ; aucune signature ne force la livraison. | Alerter après plusieurs `NETWORK_ERROR` consécutifs, plusieurs serveurs miroirs. |
| Attaque de gel | La réponse de `/latest_version` n'est pas signée : un attaquant peut faire croire qu'il n'y a rien de nouveau. | Métadonnées signées, datées et à expiration (modèles TUF / Uptane). |
| Fuite de la clé privée | Toute la sécurité tombe ; il n'y a ni rotation ni révocation. | Clé dans un HSM, signature hors ligne, hiérarchie de clés révocables. |
| Robot réinitialisé | Si `state.json` est effacé, l'état revient à 0 et un vieux paquet authentique serait accepté. | Compteur anti-rollback en mémoire matérielle (eFuse, TPM). |
| Installation non atomique | Seul l'état est écrit de façon atomique ; `firmware.bin` pourrait rester partiel après une coupure. | Partitions A/B : installer sur la partition inactive, puis basculer. |
| Pas de confidentialité | Le logiciel circule en clair (TLS hors périmètre). | HTTPS en défense en profondeur, en plus de la signature. |

**Limites de nos tests et de notre dépôt :**

- le test `test_etat_ecrit_de_facon_atomique` vérifie que l'état écrit est bien
  relu, mais il ne simule pas réellement une coupure au milieu de l'écriture ;
- le robot est simulé par un programme Python sur la même machine que le serveur ;
- le dossier `attacks/` prévu au départ est resté vide : les attaques ont été
  réalisées sous forme de tests automatiques dans `tests/`, ce qui les rend
  rejouables en une commande.

## 8.2 Réflexion personnelle - Niagale

Ce projet m'a appris qu'un client de mise à jour ne se résume pas à vérifier une signature. J'ai compris pourquoi on ne fait jamais confiance au numéro donné par /latest_version, pourquoi l'état doit être écrit après l'installation et jamais avant, et comment une écriture atomique (.tmp, fsync, os.replace) évite qu'une coupure laisse un fichier à moitié écrit. Ce sont des détails qui paraissent petits, mais qui ouvrent ou ferment la porte au downgrade.

Mes plus grosses difficultés ont été pratiques plutôt que techniques. J'ai dû corriger une adresse e-mail Git mal configurée, recréer une branche partie trop tôt avec git checkout -B, et comprendre qu'il me manquait le bouton de review parce que j'étais connectée avec le compte de Killian. À l'étape 4, je n'avais pas le kit et un collage dans Git Bash avait échoué : j'ai recréé demo.py par une commande, et vérifié chaque résultat avec wc -l et git diff avant de committer. À l'étape 5, un copier-coller dans l'éditeur a remplacé tout mon fichier : je l'ai récupéré depuis le kit et j'ai refait la correction par une commande. J'ai pris l'habitude de toujours lire la sortie d'une commande avant de passer à la suivante.

Si c'était à refaire, j'écrirais un test qui simule vraiment une coupure pendant l'écriture de l'état, car le nôtre vérifie seulement que l'état est bien relu. Je rendrais aussi l'installation du logiciel atomique, comme l'état, avec deux partitions A/B.
