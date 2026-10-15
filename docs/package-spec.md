# Specification du paquet de mise a jour (R1)

> Fige en reunion d'equipe le 15 octobre 2026 (voir docs/decisions.md).

## Format

```json
{
  "version": 2,
  "content_hash": "<sha256 hex du contenu>",
  "content": "<contenu, base64>",
  "signature": "<signature RSA-PSS, base64>"
}
```

- `version` est un entier JSON, pas du texte. En texte, "10" est plus petit que "9",
  et un downgrade pourrait passer.
- `content_hash` fait 64 caracteres hexadecimaux en minuscules.

## Octets signes

On signe exactement 36 octets : la version sur 4 octets (big-endian), suivie des
32 octets bruts du hash SHA-256. On signe les octets du hash, pas son texte en
hexadecimal.

Pourquoi la version est dans la signature : si on ne signait que le hash, un
attaquant pourrait prendre un vieux paquet authentique, changer son numero de
version, et le robot l'accepterait comme une nouvelle version. Avec une longueur
fixe de 36 octets, il n'y a aucune ambiguite sur ce qui est signe.

## Cles

- Paire RSA-2048 generee en local par chaque membre :
  - `openssl genrsa -out keys/private.pem 2048`
  - `openssl rsa -in keys/private.pem -pubout -out keys/public.pem`
- Le robot ne detient que `keys/public.pem`.

### Pourquoi la cle privee ne quitte jamais le serveur

La cle privee sert a signer. Celui qui la possede peut fabriquer une mise a jour
que tous les robots accepteront sans discuter. C'est donc le secret le plus
important de tout le systeme.

Le robot, lui, n'a besoin que de verifier une signature, et la cle publique suffit
pour ca. Elle permet de verifier mais pas de signer. Si quelqu'un vole un robot ou
le pirate, il ne recupere que la cle publique : il ne peut rien signer avec.

Nos mesures :
- chaque membre genere sa paire en local avec OpenSSL, aucune cle n'est partagee ;
- aucune cle n'est versionnee : le `.gitignore` bloque `*.pem`, et la regle
  `private*` bloque aussi la cle privee, ce qui fait deux protections au lieu d'une ;
- sur le serveur, le fichier de la cle privee ne doit etre lisible que par son
  proprietaire.

Limite qu'on assume pour le labo : la cle privee n'est pas chiffree par un mot de
passe et n'est pas stockee dans un module materiel (HSM). En production, il faudrait
au minimum un mot de passe, et idealement un HSM.