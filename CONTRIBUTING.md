# Workflow Git

1. Une issue par livrable (L1 a L11), assignee a son responsable.
2. Une branche par sujet : `feat/<role>-<sujet>`, par exemple `feat/r1-package-builder`.
3. Petits commits frequents, au moins 2 pushes par semaine et par membre.
4. Messages : `feat:`, `fix:`, `test:`, `docs:`, `chore:` suivis d'une phrase claire.
5. Pull Request vers `main`, relue et approuvee par le relecteur du livrable.
6. `main` ne recoit que des PR. On ne reecrit pas l'historique et on n'antidate rien.
7. Chacun configure `git config user.name` et `git config user.email` avec son compte GitHub.
8. La cle privee n'est JAMAIS commitee.

Tags : `v0.1` (Session 2, code qui tourne), `v0.2` (Session 3, attaques), `v1.0` (soutenance).
