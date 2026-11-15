# Fiche d'attaque n°3 - Replay (rejeu)

**Responsable** : R3 (Killian) - **Date d'exécution** : 15 novembre 2026 (pytest, 22 passed)

## Objectif et verification ciblee
Rejouer un paquet **authentique** que le robot a déjà installé. Ce paquet a une vraie signature et un vrai hash : seule la **version** peut l'arrêter.

## Methode
Test automatique `tests/test_attaques_rejeu.py::test_attaque_3_replay_du_paquet_deja_installe`.
Le laboratoire : vrai serveur avec v1 et v2, robot déjà à jour en v2. Le « pirate » republie sur un serveur à lui le paquet v2 déjà installé, présenté comme une version plus récente (v5.json), pour tromper la décision du robot.

Relancer : `python -m pytest tests/test_attaques_rejeu.py -v`

## Ce que le client a recu
Un paquet v2 parfaitement valide (forme, signature, hash corrects), identique à celui déjà installé.

## Reaction du client
Forme, signature et hash passent. À l'étape version, le robot compare la version **signée à l'intérieur du paquet** (2) à `last_applied_version` (2), et non le numéro annoncé par le serveur. 2 n'est pas strictement supérieur → **VERSION_NOT_NEWER**.

## Preuve qu'aucune mise a jour n'a ete appliquee
Le test `rien_n_a_change` vérifie trois choses : `state.json` reste à 2, `firmware.bin` contient toujours `firmware v2`, et la dernière ligne du journal est REJECTED avec le bon code.

## Resultat
Rejetée comme prévu : **oui**.
Test de mutation : on a mis en commentaire la vérification « version plus récente » dans `client/verify.py` : le test 3 (et le 4a) **échouent**. Le test est donc bien sensible à cette vérification. Fichier restauré ensuite (`git checkout client/verify.py`), 19 passed à ce moment-là.

## Lecon apprise
Une signature valide prouve **qui** a signé, pas **quand**. Sans comparaison de version, un paquet authentique mais déjà installé est rejouable à volonté. Le robot doit se fier à la version signée, jamais à celle annoncée par `/latest_version`.

## Code de rejet attendu / obtenu
Attendu : VERSION_NOT_NEWER - Obtenu : VERSION_NOT_NEWER

## Ligne d'audit log
```
{"ts": "<heure UTC>", "version": 2, "decision": "REJECTED", "reason": "VERSION_NOT_NEWER"}
```
