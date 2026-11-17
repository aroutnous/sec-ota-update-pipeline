# Rapport technique - Partie R1 (Landry BAMBARA)

> Sections 1, 2, 3.1 et 8.5 du rapport, et réflexion personnelle 8.1.
> Sources : `docs/security-design.md`, `docs/decisions.md`, `docs/package-spec.md`,
> `server/package_builder.py`, `server/app.py`.

## 1. Contexte, problème et modèle d'attaquant

### 1.1 Le problème

Un robot reçoit ses mises à jour logicielles « over-the-air » (OTA), par un réseau
que l'on ne contrôle pas. Si un attaquant parvient à lui faire installer un logiciel
modifié, il prend le contrôle du robot. S'il parvient à le faire revenir à une
ancienne version, il rouvre des failles déjà corrigées.

L'objectif du projet est un prototype dans lequel le robot n'installe une mise à
jour que si elle est :

- **authentique** : produite par l'éditeur légitime (signature RSA-PSS) ;
- **intègre** : non modifiée depuis sa signature (empreinte SHA-256 recalculée) ;
- **récente** : strictement plus récente que la version déjà installée (anti-rollback).

Critères de réussite fixés par l'énoncé : 5 attaques sur 5 rejetées, 0 mise à jour
falsifiée installée, 1 mise à jour légitime acceptée.

### 1.2 Modèle d'attaquant

Nous supposons un attaquant qui contrôle le réseau entre le robot et le serveur, et
qui peut aussi prendre le contrôle du serveur de distribution. Il peut lire,
modifier, supprimer, rejouer ou retarder n'importe quel message, se faire passer
pour le serveur et rejouer d'anciens paquets authentiques.

Il ne peut pas obtenir la clé privée de l'éditeur, qui ne quitte jamais la machine
de signature, ni casser RSA-2048 ou SHA-256. Toute la sécurité du système repose
sur cette hypothèse. Le détail (actifs, menaces non couvertes) est dans le
security design document, livré dans `docs/security-design.md`.

## 2. Conception

### 2.1 Trois vérifications, dans un ordre fixe

Le robot vérifie chaque paquet reçu dans cet ordre (décision 4) :

1. **forme** : 4 champs présents, types corrects, sinon `MALFORMED_PACKAGE` ;
2. **signature** RSA-PSS valide avec la clé publique, sinon `BAD_SIGNATURE` ;
3. **hash** : le SHA-256 recalculé du contenu reçu est égal au hash annoncé, sinon `HASH_MISMATCH` ;
4. **version** signée strictement supérieure à la dernière version appliquée, sinon `VERSION_NOT_NEWER`.

L'ordre n'est pas arbitraire. Tant que la signature n'est pas vérifiée, aucun champ
du paquet n'est digne de confiance : on ne compare donc la version qu'après l'avoir
authentifiée. Le premier contrôle qui échoue donne le code de rejet, ce qui permet
de prouver, pour chaque attaque, quelle protection l'a arrêtée.

### 2.2 Ce qui est signé : 36 octets

L'éditeur ne signe pas le logiciel directement. Il signe 36 octets de longueur
fixe (décision 2) : la version sur 4 octets big-endian, suivie des 32 octets bruts
du hash SHA-256 du logiciel. Le logiciel est protégé par son hash, et le hash est
protégé par la signature.

**Écart volontaire avec l'énoncé : la version est signée.** L'énoncé demandait de
signer le hash. Si la version n'était pas signée, un attaquant pourrait prendre un
vieux paquet authentique, changer son numéro de version et le faire passer pour
une mise à jour récente. En signant la version, ce maquillage casse la signature :
c'est exactement ce que montre l'attaque 4b (rejetée en `BAD_SIGNATURE`).

### 2.3 Choix cryptographiques

| Choix | Justification |
| --- | --- |
| RSA-2048 | Taille de clé standard et sûre aujourd'hui ; signatures de 256 octets. |
| RSA-PSS (MGF1-SHA256, sel de taille maximale) | Schéma de signature RSA moderne ; le sel aléatoire rend chaque signature différente. |
| SHA-256 | Empreinte de 32 octets résistante aux collisions. |
| Version = entier | En texte, « 10 » est inférieur à « 9 » : une comparaison de chaînes permettrait un downgrade. |

## 3. Implémentation

### 3.1 Clés, paquet et serveur (R1)

**Clés.** Chaque membre génère sa propre paire RSA-2048 en local avec OpenSSL.
Aucune clé n'est versionnée (décision 8) : le `.gitignore` exclut `*.pem`,
`private*` et `*.key`. Le robot ne détient que la clé publique : il peut vérifier,
mais pas signer.

**Constructeur de paquet** (`server/package_builder.py`, 77 lignes). La fonction
`build_package` calcule le SHA-256 du logiciel, signe les 36 octets avec la clé
privée, puis encode le contenu et la signature en base64. Le paquet est un fichier
JSON `server/packages/v<N>.json` à quatre champs : `version`, `content_hash`,
`content`, `signature`. L'outil `scripts/verifier_paquet.py` vérifie un paquet avec
la seule clé publique.

**Serveur** (`server/app.py`, Flask, 86 lignes, `127.0.0.1:5001`). Deux routes :
`GET /latest_version` renvoie la plus grande version publiée ;
`GET /download?version=N` sert le paquet tel quel (400 si la version n'est pas un
nombre, 404 si elle n'existe pas). Le serveur ne signe rien et ne demande aucune
authentification : il se contente de distribuer des paquets déjà signés. Le
compromettre ne donne donc pas la clé privée. Le port 5001 a remplacé le port 5000,
occupé par AirPlay sous macOS (décision 9).

**Tests du serveur** : 5 tests dans `tests/test_serveur.py` (version annoncée, téléchargement
sans paramètre, plusieurs versions, version inconnue ou invalide, aucun paquet publié).

## 8.5 Organisation du travail

Le travail a été découpé en quatre rôles (R1 serveur et crypto, R2 client et
journal, R3 attaques 1 à 4, R4 MITM et rapport) et onze livrables (L1 à L11), chacun
suivi par une issue GitHub assignée à son responsable.

Chaque contribution suit le même circuit : une branche par sujet, de petits commits
préfixés (`feat:`, `test:`, `docs:`, `chore:`), une Pull Request vers `main`, puis une
relecture par un autre membre, qui teste chez lui avant d'approuver. La branche
`main` est protégée (une approbation obligatoire) et les PR sont fusionnées en
« merge commit » pour conserver les commits de chacun.

Bilan au tag `v0.2` (17 novembre 2026) : 17 Pull Requests fusionnées, dont 16
relues et fusionnées par un autre membre que leur auteur ; 37 commits répartis entre
les quatre membres ; 22 tests automatiques au vert.

La relecture croisée a eu un effet concret : un bloc de code mal fermé dans le
README (PR #24) a été repéré et corrigé avant la fusion.

## 8.1 Réflexion personnelle - Landry

Sur le plan technique, ce projet m'a fait comprendre qu'une signature prouve **qui**
a produit un paquet, mais pas **quand** : sans contrôle de version, un paquet
authentique peut être rejoué indéfiniment. C'est ce qui m'a conduit à signer la
version avec le hash, en m'écartant de l'énoncé, et à séparer la signature (chez
l'éditeur) de la distribution (sur le serveur), pour qu'un serveur piraté ne donne
jamais la clé privée.

Mes plus grosses difficultés n'ont pas été cryptographiques, mais pratiques : le
Bloc-notes de Windows qui a reformaté `decisions.md` (rattrapé avec `git restore`),
le port 5000 occupé par AirPlay sur le Mac d'Amara, qui nous a obligés à fixer un
port commun (décision 9), et un push refusé par GitHub parce qu'il exposait mon
adresse e-mail privée. J'ai appris à relire systématiquement `git diff` avant de
committer.

Coordonner quatre personnes m'a aussi appris que la relecture croisée n'est pas
une formalité : elle a arrêté un README cassé avant qu'il n'arrive dans `main`.

Si c'était à refaire, je poserais le tag `v0.1` dès que le code tournait (il n'a
jamais été posé), et je signerais aussi la réponse de `/latest_version`, avec une
date d'expiration, pour fermer l'attaque de gel que nous avons laissée ouverte.
