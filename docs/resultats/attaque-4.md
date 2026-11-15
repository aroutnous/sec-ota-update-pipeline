# Fiche d'attaque n°4 - Downgrade (retour en arrière)

**Responsable** : R3 (Killian) - **Date d'exécution** : 15 novembre 2026 (pytest, 22 passed)

## Objectif et verification ciblee
Faire revenir le robot à une **ancienne** version (par exemple une version vulnérable). Vérifications ciblées : la **version** (4a) puis la **signature** (4b).

## Methode
Tests automatiques `tests/test_attaques_rejeu.py` (laboratoire : serveur réel avec v1 et v2, robot déjà en v2, serveur « pirate » vide) :
- `test_attaque_4a_downgrade_vers_v1` : le pirate sert le vrai paquet v1 (authentique).
- `test_attaque_4b_v1_avec_version_maquillee` : le pirate prend le paquet v1 et change seulement son numéro de version pour le faire paraître récent.
- `test_controle_une_vraie_v3_passe_encore` : après toutes ces attaques, une vraie v3 signée est ACCEPTED et `state.json` passe à 3. Cela prouve que le robot ne rejette pas tout.

Relancer : `python -m pytest tests/test_attaques_rejeu.py -v`

## Ce que le client a recu
- 4a : un paquet v1 authentique (forme, signature, hash corrects).
- 4b : un paquet v1 dont le champ `version` a été remplacé par un nombre plus grand.

## Reaction du client
- 4a : tout passe jusqu'à la version : 1 n'est pas supérieur à 2 → **VERSION_NOT_NEWER**.
- 4b : la signature couvre les 36 octets (version sur 4 octets + hash sur 32). Changer la version change ces octets, donc la signature ne correspond plus → **BAD_SIGNATURE**. Le robot n'arrive jamais à la vérification de version : la signature bloque avant.

## Preuve qu'aucune mise a jour n'a ete appliquee
Pour 4a et 4b, `rien_n_a_change` vérifie : `state.json` = 2, `firmware.bin` = `firmware v2`, dernière ligne du journal REJECTED avec le bon code.

## Resultat
Rejetée comme prévu : **oui** (4a, 4b), et le contrôle v3 est accepté.
Test de mutation : vérification « version plus récente » mise en commentaire → 3 et 4a **échouent**, mais **4b reste vert** : c'est la signature qui le bloque. Les deux protections sont donc indépendantes, et le test montre laquelle bloque quoi.

## Lecon apprise
Si la version n'était pas **dans les octets signés**, un attaquant pourrait maquiller un vieux paquet en paquet récent et contourner le contrôle de version. Signer la version ferme cette porte : c'est pourquoi on signe 36 octets et pas seulement le hash.

## Code de rejet attendu / obtenu
| Cas | Attendu | Obtenu |
| --- | --- | --- |
| 4a. Vieux paquet authentique | VERSION_NOT_NEWER | VERSION_NOT_NEWER |
| 4b. Version maquillée | BAD_SIGNATURE | BAD_SIGNATURE |

## Ligne d'audit log
```
{"ts": "<heure UTC>", "version": 1, "decision": "REJECTED", "reason": "VERSION_NOT_NEWER"}
{"ts": "<heure UTC>", "version": <n>, "decision": "REJECTED", "reason": "BAD_SIGNATURE"}
```
