---
date: 2008-10-22T15:00:00Z
title: Inviare i messaggi di commit git a Lighthouse in batch
tags: [git, ruby, open-source]
---

{{< retrospective year="2026" >}}
Lighthouse (il project tracker di ENTP) ha chiuso nel 2012, e la sua integrazione con GitHub non esiste più. Se cerchi il collegamento automatico tra commit e issue, tutte le piattaforme moderne (GitHub Issues, GitLab, Jira, Linear) lo fanno nativamente.
{{< /retrospective >}}

Se usi l'integrazione con Lighthouse fornita da GitHub, dalle pagine "Admin"
del tuo repository git, potresti esserti imbattuto in un difetto: ogni
changeset su Lighthouse appare come se fosse stato fatto dall'utente Lighthouse
che ha configurato l'integrazione su GitHub.

Questo succede perché Lighthouse usa il token API per collegare gli autori dei
changeset agli utenti LH, e non va bene quando non sei l'unico a fare commit :-).

Una soluzione semplice è usare un hook post-commit, come descritto
[qui](http://github.com/guides/integrating-git-commit-messages-in-lighthouse),
ma non è soddisfacente perché significa che ogni volta che esegui git commit
dalla tua console, il messaggio del commit diventa pubblico, e se fai
`--amend` o `reset --soft` dell'index dovrai andare su Lighthouse a cancellare
il changeset.

Una soluzione molto più furba è pushare tutte le revisioni modificate quando
le si pusha su GitHub: ho [modificato l'hook post-commit
originale](http://gist.github.com/53917) e l'ho installato accanto al comando
`git` in `$(dirname which git)/git-lh`.

Questo mi dà un nuovo comando `git lh` che recupera la revisione HEAD corrente
da GitHub usando `refs/heads/master` e fa POST di ogni changeset tra quella
revisione e il tip corrente nel working tree verso Lighthouse.

Quindi, se esegui `git lh` prima di `git push`, ogni modifica che stai
pushando su GitHub andrà anche su Lighthouse.

**AGGIORNAMENTO**: Un semplice script bash tipo:

```bash
#!/bin/bash
git lh && git push
```

salvato come `git-lh-push` ti risparmia di digitare due comandi quando vuoi fare push :).

Buon divertimento!

Riferimenti:

lo [script git-lh su GitHub](http://gist.github.com/53917)
