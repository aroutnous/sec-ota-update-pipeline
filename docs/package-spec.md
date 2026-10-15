# Specification du paquet de mise a jour (R1)

> Proposition de depart, a valider et figer en reunion d'equipe (S2).

## Format

```json
{
  "version": 2,
  "content_hash": "<sha256 hex du contenu>",
  "content": "<contenu, base64>",
  "signature": "<signature RSA-PSS, base64>"
}
```

## Octets signes

A decider ensemble. Proposition : `version` (entier 4 octets, big-endian) suivi du
`content_hash` (32 octets). Signer version + hash, et non le hash seul, empeche de
changer le numero de version sans casser la signature.

## Cles

- RSA-2048 generee par `openssl genrsa` ; la cle privee reste sur le serveur.
- Le robot ne detient que `keys/public.pem`.
- Pourquoi la cle privee ne doit jamais quitter le serveur : a documenter ici.
