# Decisions d'equipe - reunion du 15 octobre 2026

Presents : Landry BAMBARA (R1), Niagale TRAORE (R2), Killian OUASSENAN (R3), Amara SOUNTOURA (R4)

## Roles

| Role | Membre | Livrables |
| --- | --- | --- |
| R1 - Serveur & crypto | Landry BAMBARA | L1, L2, L8 |
| R2 - Client & log | Niagale TRAORE | L3, L4, L9, L11 |
| R3 - Attaques 1 a 4 | Killian OUASSENAN | L5, L7 |
| R4 - MITM & rapport | Amara SOUNTOURA | L6, L7, L10 |

## Decisions techniques

| # | Decision | Choix retenu | Pourquoi |
| --- | --- | --- | --- |
| 2 | Octets signes | version (entier 4 octets, big-endian) suivie des 32 octets bruts du hash SHA-256 : 36 octets fixes | La version ne peut pas etre maquillee (downgrade) ; longueur fixe, aucune ambiguite |
| 3 | Champs du paquet | JSON : version (entier), content_hash (64 hex minuscules), content (base64), signature (base64) | Version entiere car en texte "10" < "9" ; JSON lisible dans les fiches |
| 4 | Ordre des verifications | forme (champs + types) -> signature -> hash recalcule -> version > derniere appliquee | Aucune confiance dans un champ non authentifie ; la version comparee est celle signee, jamais /latest_version |
| 5 | Codes | MALFORMED_PACKAGE, BAD_SIGNATURE, HASH_MISMATCH, VERSION_NOT_NEWER, NETWORK_ERROR ; ACCEPTED si tout passe | Prouver quelle verification bloque chaque attaque ; tracer le deni de service |
| 6 | Audit log | une ligne JSON par decision : ts (ISO 8601 UTC), version (null si illisible), decision (ACCEPTED, REJECTED, ERROR), reason ; ajout seul | Chaque ligne est une preuve autonome |
| 7 | Etat du robot | {"last_applied_version": N}, 0 au depart, ecrit apres installation reussie, de facon atomique | Le robot n'oublie jamais sa version (risque 1 : replay, downgrade) |
| 8 | Cles | aucune cle versionnee ; chaque membre genere sa paire en local avec OpenSSL | Une cle publique commune ne correspondrait pas aux cles privees locales |

## Questions ouvertes pour le prof

- Le robot peut-il etre simule par un client Python ?
- Signer version + hash (ecart avec l'enonce) est-il accepte ?
- Le TLS est-il hors perimetre ?

