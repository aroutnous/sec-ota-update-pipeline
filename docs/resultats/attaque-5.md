# Fiche d'attaque n.5 - Man-in-the-middle

**Responsable** : R4 Amara SOUNTOURA - **Date d'execution** : 17 octobre 2026

## Objectif et verification ciblee
Un attaquant place entre le robot et le serveur (proxy) modifie ou bloque le
telechargement. Verification ciblee : le HASH (contenu modifie) ; en cas de
blocage, c'est un deni de service, non empechable.

## Methode
Proxy `proxy/mitm_proxy.py`, tests `tests/test_proxy.py`. Le robot pointe vers le
proxy (port 8080) qui relaie vers le vrai serveur (5001). Trois modes :
transparent, tamper-content, drop.

## Ce que le client a recu
- transparent : le vrai paquet, inchange.
- tamper-content : le contenu remplace par "firmware pirate", hash et signature
  d'origine conserves.
- drop : aucune reponse (le proxy renvoie 503).

## Reaction du client
```
transparent    -> ACCEPTED       (controle : une vraie MAJ passe meme via le proxy)
tamper-content -> HASH_MISMATCH   (le hash recalcule ne correspond plus)
drop           -> NETWORK_ERROR   (rien recu : deni de service)
```

## Preuve qu'aucune mise a jour n'a ete appliquee
tamper-content et drop : etat inchange, aucun logiciel pirate installe. Le proxy
garde une copie des paquets dans proxy/captures/ ; les rejouer echoue grace a la
verification de version (voir attaque 3).

## Resultat
Rejetee comme prevu : **oui** pour tamper-content et drop. Le mode transparent
(controle) donne bien ACCEPTED.

## Lecon apprise
Modifier le telechargement est detecte (HASH_MISMATCH ou BAD_SIGNATURE). Bloquer
le telechargement reussit, mais ne fait installer aucune fausse mise a jour :
c'est un deni de service, la seule chose qu'un attaquant au milieu peut obtenir.
C'est une limite assumee : on peut la detecter (plusieurs NETWORK_ERROR de
suite), pas l'empecher par la signature. En reel, l'attaquant se placerait par
ARP ou DNS spoofing ; en labo, on pointe le robot vers le proxy, ce qui revient
au meme pour le robot.

## Code de rejet attendu / obtenu
tamper-content : attendu HASH_MISMATCH - obtenu HASH_MISMATCH.
drop : attendu NETWORK_ERROR - obtenu NETWORK_ERROR.

## Ligne d'audit log
```
{"ts": "2026-...Z", "version": 3, "decision": "REJECTED", "reason": "HASH_MISMATCH"}
{"ts": "2026-...Z", "version": null, "decision": "ERROR", "reason": "NETWORK_ERROR"}
```
