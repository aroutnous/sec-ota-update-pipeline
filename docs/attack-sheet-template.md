## Resultats attendus

Le robot verifie dans cet ordre : forme, signature, hash, version. La premiere verification qui echoue rejette le paquet.

| Cas | Ce qu'on fait | Verification qui bloque | Code attendu | Ligne d'audit log attendue |
| --- | --- | --- | --- | --- |
| Controle : mise a jour valide | On envoie un paquet correctement signe, avec une version plus grande que celle du robot | aucune | ACCEPTED | decision ACCEPTED |
| 1a. Paquet non signe | On enleve le champ signature | forme (champ manquant) | MALFORMED_PACKAGE | decision REJECTED, reason MALFORMED_PACKAGE |
| 1b. Paquet non signe | On met une fausse signature (octets au hasard en base64) | signature | BAD_SIGNATURE | decision REJECTED, reason BAD_SIGNATURE |
| 2a. Paquet modifie | On change le contenu, on garde le hash et la signature d'origine | hash : le hash recalcule ne correspond plus | HASH_MISMATCH | decision REJECTED, reason HASH_MISMATCH |
| 2b. Paquet modifie | On change le contenu ET on recalcule le hash, mais on garde l'ancienne signature | signature : elle ne correspond plus au nouveau hash | BAD_SIGNATURE | decision REJECTED, reason BAD_SIGNATURE |
| 3. Replay | On renvoie un paquet valide deja installe (meme version que celle du robot) | version : pas plus grande que la derniere appliquee | VERSION_NOT_NEWER | decision REJECTED, reason VERSION_NOT_NEWER |
| 4a. Downgrade | On envoie un ancien paquet authentique (version plus petite que celle du robot) | version : pas plus grande que la derniere appliquee | VERSION_NOT_NEWER | decision REJECTED, reason VERSION_NOT_NEWER |
| 4b. Downgrade | On prend un ancien paquet et on change seulement son numero de version pour le faire paraitre recent | signature : la version fait partie des octets signes | BAD_SIGNATURE | decision REJECTED, reason BAD_SIGNATURE |
| 5. Man-in-the-middle (R4) | Un proxy coupe la connexion ou rend le serveur injoignable | aucune : le robot ne recoit pas de paquet | NETWORK_ERROR | decision ERROR, version null |

Remarque sur le cas 5 : si le proxy modifie le paquet au lieu de couper la connexion, on retombe sur les cas 2 (HASH_MISMATCH ou BAD_SIGNATURE).

# Fiche d'attaque n. X - <nom de l'attaque>

**Responsable** : R? - **Date d'execution** :

## Objectif et verification ciblee
Quelle verification (signature, hash, version) doit bloquer cette attaque ?

## Methode
Comment l'attaque a ete realisee (commande ou script, `attacks/...`).

## Ce que le client a recu
Contenu ou extrait du paquet recu.

## Reaction du client
Extrait du log d'erreur.

```
(coller le log)
```

## Preuve qu'aucune mise a jour n'a ete appliquee
Etat avant / apres (`state.json`), contenu installe inchange.

## Resultat
Rejetee comme prevu : oui / non. Si non : cause, correction, nouveau test.

## Lecon apprise
Specifique, pas generique.

## Code de rejet attendu / obtenu
Attendu : ...  - Obtenu : ...

## Ligne d'audit log
Coller la ligne JSON ecrite par le client (ts, version, decision, reason).
