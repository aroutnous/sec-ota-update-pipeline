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
