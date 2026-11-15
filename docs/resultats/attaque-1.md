# Fiche d'attaque n°1 - Paquet non signé

**Responsable** : R3 (Killian) - **Date d'exécution** : 15 novembre 2026 (pytest, 22 passed)

## Objectif et verification ciblee
Faire installer un logiciel qui ne vient pas de l'éditeur. Sans la clé privée, l'attaquant ne peut faire que deux choses : **retirer** la signature (1a) ou **en inventer** une (1b). Les vérifications ciblées sont la **forme** du paquet (1a) puis la **signature** (1b).

## Methode
Tests automatiques `tests/test_attaques_paquet.py` (fixtures : clés RSA en mémoire, serveur Flask réel sur un port libre, robot réel) :
- `test_attaque_1a_signature_supprimee` : on supprime le champ `signature` du paquet JSON.
- `test_attaque_1b_fausse_signature` : on met une signature faite d'octets au hasard encodés en base64.
- `test_controle_mise_a_jour_valide_acceptee` : paquet correct, pour prouver que le robot n'est pas simplement « tout-rejetant ».

Relancer : `python -m pytest tests/test_attaques_paquet.py -v`

## Ce que le client a recu
- 1a : un paquet JSON avec `version`, `content_hash`, `content`, mais **sans** champ `signature`.
- 1b : un paquet complet, mais dont `signature` est du base64 aléatoire (256 octets sans lien avec le contenu).

## Reaction du client
Le robot vérifie dans l'ordre forme → signature → hash → version et s'arrête au premier échec.
- 1a : rejeté dès la **forme** (champ manquant), la signature n'est même pas vérifiée.
- 1b : la forme est correcte, rejeté à la **signature** (RSA-PSS ne valide pas).

## Preuve qu'aucune mise a jour n'a ete appliquee
Dans le robot (`client/robot.py`), l'installation puis l'écriture de `state.json` n'arrivent **qu'après** une vérification réussie. Un rejet à la forme ou à la signature sort avant ces deux étapes : le firmware installé et `last_applied_version` ne changent pas. Seule une ligne REJECTED est ajoutée au journal d'audit.

## Resultat
Rejetée comme prévu : **oui** (les 2 tests passent, le test de contrôle passe aussi).

## Lecon apprise
Sans la clé privée, un paquet « non signé » n'a que deux formes possibles : signature absente ou signature inventée. Les deux sont arrêtées, et à deux endroits différents de la chaîne (forme, puis signature). Mettre un paquet inconnu sur le serveur ne suffit donc jamais.

## Code de rejet attendu / obtenu
| Cas | Attendu | Obtenu |
| --- | --- | --- |
| 1a. Signature supprimée | MALFORMED_PACKAGE | MALFORMED_PACKAGE |
| 1b. Fausse signature | BAD_SIGNATURE | BAD_SIGNATURE |

## Ligne d'audit log
Format écrit par le client (le champ `ts` est l'heure UTC de l'exécution) :

```
{"ts": "<heure UTC>", "version": <n>, "decision": "REJECTED", "reason": "MALFORMED_PACKAGE"}
{"ts": "<heure UTC>", "version": <n>, "decision": "REJECTED", "reason": "BAD_SIGNATURE"}
```
