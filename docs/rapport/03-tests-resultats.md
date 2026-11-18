# Rapport technique - Partie R3 (Killian OUASSENAN)

> Sections 4.1, 4.2, 5.1 et 5.2 du rapport, et réflexion personnelle 8.3.
> Sources : `tests/` (conftest.py, outils.py, test_attaques_paquet.py,
> test_attaques_rejeu.py), `docs/resultats/attaque-1.md` à `attaque-4.md`,
> `docs/journal-echecs.md` (tests de mutation).

## 4. Méthodologie des tests

### 4.1 Le laboratoire de tests et le test de contrôle

Toutes les attaques sont réalisées sous forme de **tests automatiques** (pytest).
Elles sont donc rejouables par n'importe qui, en une commande :
`python -m pytest -v` (22 tests).

Les tests ne dépendent d'aucune clé personnelle : `tests/conftest.py` génère une
paire RSA-2048 **en mémoire** à chaque session, et fabrique un paquet v2 neuf pour
chaque test. Les tests travaillent à deux niveaux :

- **niveau paquet** (`test_attaques_paquet.py`, 5 tests) : on appelle directement
  `verify_package` sur un paquet modifié, sans réseau. C'est le niveau des attaques
  1 et 2 ;
- **niveau système** (`test_attaques_rejeu.py`, 4 tests) : on lance un vrai serveur
  Flask sur un port libre (`tests/outils.py`), le robot se met à jour normalement en
  v2, puis un **serveur pirate** lui sert un ancien paquet authentique en
  l'annonçant comme une v5. C'est le niveau des attaques 3 et 4.

Chaque test d'attaque système vérifie **quatre preuves** : le code renvoyé, l'état
inchangé (`state.json`), le logiciel installé inchangé (`firmware.bin`) et la ligne
`REJECTED` ajoutée au journal.

**Le test de contrôle.** À chaque niveau, un test vérifie qu'une mise à jour
légitime est bien **acceptée** (`test_controle_mise_a_jour_valide_acceptee`,
`test_controle_une_vraie_v3_passe_encore`). Sans lui, un robot qui refuserait tout
réussirait tous les tests d'attaque, et ces tests ne prouveraient rien.

### 4.2 Tests de mutation : nos tests mesurent-ils vraiment les protections ?

Un test qui passe ne prouve rien s'il passerait aussi sans la protection. Nous
avons donc retiré volontairement une vérification de `client/verify.py`, relancé
les tests, puis restauré le fichier :

| Protection retirée | Tests qui échouent | Ce que cela prouve |
| --- | --- | --- |
| Vérification du hash | 2a (et le test MITM `test_contenu_remplace_est_refuse`) | Ces tests dépendent bien du hash. |
| Vérification de la version | 3 et 4a ; **4b reste vert** | 3 et 4a dépendent de la version ; 4b est arrêté par la signature, indépendamment. |

Après restauration, les 22 tests repassent.

## 5. Résultats

### 5.1 Tableau de synthèse

| Attaque | Scénario | Vérification qui bloque | Code obtenu | Rejetée ? |
| --- | --- | --- | --- | --- |
| 1. Non signé | 1a signature supprimée | forme | `MALFORMED_PACKAGE` | oui |
|  | 1b fausse signature | signature | `BAD_SIGNATURE` | oui |
| 2. Modifié | 2a contenu changé, hash gardé | hash | `HASH_MISMATCH` | oui |
|  | 2b contenu et hash recalculé | signature | `BAD_SIGNATURE` | oui |
| 3. Replay | paquet v2 déjà installé, renvoyé | version | `VERSION_NOT_NEWER` | oui |
| 4. Downgrade | 4a retour vers v1 | version | `VERSION_NOT_NEWER` | oui |
|  | 4b v1 avec version maquillée | signature | `BAD_SIGNATURE` | oui |
| 5. MITM | contenu remplacé par le proxy | hash | `HASH_MISMATCH` | oui |
|  | réponses bloquées par le proxy | aucune (déni de service) | `NETWORK_ERROR` | rien installé |
| Contrôle | vraie mise à jour (v2, puis v3) | toutes passent | `ACCEPTED` | acceptée |

Bilan : **5 attaques sur 5 n'installent rien**, **0 mise à jour falsifiée appliquée**,
**la mise à jour légitime est acceptée**. Les critères de l'énoncé sont atteints.

### 5.2 Attaques 1 à 4

Les fiches détaillées sont dans `docs/resultats/attaque-1.md` à `attaque-4.md`.
L'essentiel :

- **Attaque 1, paquet non signé.** Sans la clé privée, l'attaquant ne peut que
  retirer la signature (1a, arrêté dès la forme) ou en inventer une (1b, arrêtée par
  la signature). Déposer un paquet inconnu sur le serveur ne suffit donc jamais.
- **Attaque 2, paquet modifié.** Changer le contenu en gardant le hash (2a) est
  détecté par le hash recalculé. Recalculer le hash (2b) ne sert à rien : le hash est
  dans les octets signés, la signature ne correspond plus.
- **Attaque 3, replay.** Le paquet rejoué est parfaitement authentique : seule la
  version peut l'arrêter. Une signature prouve **qui** a signé, pas **quand**.
- **Attaque 4, downgrade.** Un vieux paquet authentique est arrêté par la version
  (4a). Si l'attaquant maquille son numéro de version (4b), c'est la signature qui
  casse, car la version fait partie des 36 octets signés.

## 8.3 Réflexion personnelle - Killian

Ce projet m'a surtout appris deux choses. D'abord, que la version doit faire partie des octets signés : l'éditeur signe 36 octets (la version sur 4 octets et le hash sur 32), donc maquiller le numéro d'un vieux paquet casse la signature (attaque 4b). Ensuite, que le test de mutation est ce qui donne un sens aux tests d'attaque : en désactivant le hash puis la version, j'ai vu quels tests cassaient, et que 4b restait vert parce que la signature le bloque indépendamment de la version.

Ma plus grosse difficulté a été pratique plutôt que cryptographique : un dépôt mal nommé, des collages Git Bash qui bloquaient le terminal, et à l'étape 4 un kit absent. J'ai donc rédigé les fiches des attaques 1 à 4 avec l'aide d'un assistant IA, à partir du modèle et de mes tests. En les relisant à l'étape 5, j'ai trouvé une erreur dans la fiche 1 (elle parlait d'un serveur réel alors que le test appelle directement verify_package) et je l'ai corrigée : j'ai appris à relire ma propre documentation contre le code.

Si c'était à refaire, j'écrirais les fiches en même temps que les tests, j'étendrais la mutation à la signature et à la forme, et je testerais les limites que l'on documente seulement (robot remis à 0, attaque de gel).