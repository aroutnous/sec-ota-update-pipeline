# Verifications du client et fichier d'etat (R2)

> Proposition de depart, a valider en reunion d'equipe.

## Ordre des verifications

1. Paquet bien forme (champs presents) -> sinon `MALFORMED_PACKAGE`
2. Signature valide -> sinon `BAD_SIGNATURE`
3. Hash du contenu egal a `content_hash` -> sinon `HASH_MISMATCH`
4. Version strictement superieure a la derniere appliquee -> sinon `VERSION_NOT_NEWER`
5. Tout est bon : appliquer, mettre a jour l'etat, logger `ACCEPTED`

## Fichier d'etat

`client/state.json` : `{"last_applied_version": 1}` (ignore par git).

## Audit log

Une ligne JSON par decision :
`{"ts": "...", "version": 2, "decision": "REJECTED", "reason": "BAD_SIGNATURE"}`






## Precisions (R2)

### 1. Paquet bien forme
On verifie aussi les types : `version` est un entier JSON, `content_hash` fait exactement 64 caracteres hexadecimaux minuscules (SHA-256), et `content` et `signature` sont du base64 valide.
Pourquoi : un paquet mal forme pourrait faire planter le robot ou fausser une comparaison (en texte "10" < "9"). On rejette tout ce qui n'a pas la forme attendue avant meme la cryptographie.

### 2. Version comparee
La version comparee a l'etat local est celle du paquet, couverte par la signature (4 premiers des 36 octets signes), jamais celle annoncee par `/latest_version`.
Pourquoi : `/latest_version` n'est pas signe, un attaquant peut le modifier. Seule la version signee est fiable, c'est elle qui bloque le downgrade.

### 3. NETWORK_ERROR
Si le serveur est injoignable (timeout, connexion refusee) ou si la reponse est illisible, le robot renvoie `NETWORK_ERROR`. Rien n'est installe et l'etat ne change pas.
Pourquoi : un attaquant qui coupe le reseau peut empecher la mise a jour, mais pas en faire installer une fausse. Ce code permet de prouver ce deni de service dans l'attaque 5.

### 4. Fichier d'etat
Format : `{"last_applied_version": N}`. Au depart N vaut 0 (si le fichier n'existe pas, on considere 0). Le fichier est ecrit seulement apres une installation reussie, de facon atomique : on ecrit d'abord `client/state.json.tmp`, puis on le renomme en `client/state.json`.
Pourquoi atomique : si le robot plante ou si le courant coupe pendant l'ecriture, on garde soit l'ancien fichier complet, soit le nouveau, jamais un fichier a moitie ecrit. Un fichier corrompu pourrait remettre la version a 0 et rouvrir la porte au replay et au downgrade.

### 5. Audit log
- `ts` : date et heure en ISO 8601 UTC, par exemple `2026-10-16T09:15:00Z`.
- `decision` : `ACCEPTED`, `REJECTED` ou `ERROR` (`ERROR` pour `NETWORK_ERROR`).
- `version` : `null` si le paquet est illisible.
- `reason` : le code de la verification qui a bloque.
- Ajout seul : on ajoute des lignes a la fin, on n'en modifie ni n'en efface jamais.
Pourquoi : chaque ligne est une preuve autonome de ce que le robot a decide. L'UTC evite les confusions de fuseau horaire, et l'ajout seul empeche d'effacer la trace d'une attaque.