# Fiche d'attaque n°2 - Paquet modifié

**Responsable** : R3 (Killian) - **Date d'exécution** : 15 novembre 2026 (pytest, 22 passed)

## Objectif et verification ciblee
Faire installer un logiciel **modifié** à partir d'un paquet authentique. Vérifications ciblées : le **hash** (2a) puis la **signature** (2b).

## Methode
Tests automatiques `tests/test_attaques_paquet.py` :
- `test_attaque_2a_contenu_modifie_hash_garde` : on change le contenu, on garde le hash et la signature d'origine.
- `test_attaque_2b_contenu_et_hash_modifies` : on change le contenu **et** on recalcule le hash, mais on garde l'ancienne signature.

Relancer : `python -m pytest tests/test_attaques_paquet.py -v`

## Ce que le client a recu
- 2a : un contenu différent de l'original, avec le `content_hash` et la `signature` d'origine.
- 2b : un contenu différent, avec un `content_hash` cohérent avec ce nouveau contenu, mais la `signature` d'origine.

## Reaction du client
- 2a : forme OK, signature **OK** (elle porte sur version + hash d'origine, qui n'ont pas changé). Le robot recalcule le SHA-256 du contenu reçu : il ne correspond plus au hash annoncé → **HASH_MISMATCH**.
- 2b : le hash est cohérent, donc le test du hash passerait, mais la signature porte sur l'**ancien** hash : RSA-PSS échoue → **BAD_SIGNATURE** (la vérification de signature passe avant celle du hash).

## Preuve qu'aucune mise a jour n'a ete appliquee
Les deux rejets ont lieu avant l'installation et avant l'écriture de `state.json` (installation puis `save_state` seulement après acceptation). Firmware installé et version appliquée inchangés ; une ligne REJECTED dans le journal.

## Resultat
Rejetée comme prévu : **oui** (2a et 2b).

## Lecon apprise
L'attaquant est pris dans les deux cas : modifier le logiciel casse l'empreinte (2a) ; recalculer l'empreinte casse la signature (2b), parce que **le hash est signé**. Pour s'en sortir il faudrait forger une nouvelle signature, donc détenir la clé privée.

## Code de rejet attendu / obtenu
| Cas | Attendu | Obtenu |
| --- | --- | --- |
| 2a. Contenu modifié, hash gardé | HASH_MISMATCH | HASH_MISMATCH |
| 2b. Contenu + hash modifiés | BAD_SIGNATURE | BAD_SIGNATURE |

## Ligne d'audit log
```
{"ts": "<heure UTC>", "version": <n>, "decision": "REJECTED", "reason": "HASH_MISMATCH"}
{"ts": "<heure UTC>", "version": <n>, "decision": "REJECTED", "reason": "BAD_SIGNATURE"}
```
