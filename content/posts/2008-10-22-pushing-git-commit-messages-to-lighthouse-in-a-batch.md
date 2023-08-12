---
date: 2008-10-22T15:00:00Z
title: Pushing git commit messages to lighthouse in a batch
tags: [git, github, lighthouse, ruby]
---

If you use github-provided lighthouse integration, from the "Admin" pages of
your git repository, you may have stumbled upon on a glitch: every changeset on
lighthouse appears as done by the lighthouse user that configured the
integration on github.

This happens because lighthouse uses the API token to link changeset authors to
LH users, and that's not good when you're not alone committing :-).

A simple solution is to use a post-commit hook, as described
[here](http://github.com/guides/integrating-git-commit-messages-in-lighthouse),
but that's not satisfactory because it means that every time you issue git
commit on your console, the commit message will go public, and if you `--amend`
or `reset --soft` the index you'll have to browse to lighthouse and delete the
changeset.

A much smarter solution is to push all changed revs when pushing them to
github: I [modified the original post-commit
hook](http://gist.github.com/53917) and installed it alongside the `git`
command in `$(dirname which git)/git-lh`.

This gives me a new `git lh` command that fetches the current HEAD revision
from github using `refs/heads/master` and POSTs every changeset between that
rev and the current tip in the working tree to lighthouse.

So, if you issue `git lh` before issuing `git push`, every change you're
pushing to github will go to lighthouse, too.

**UPDATE**: A simple bash script like:

```bash
#!/bin/bash
git lh && git push
```

saved as `git-lh-push` saves you from typing two commands when you want to push
:).

Have fun!

References:

the [git-lh script on github](http://gist.github.com/53917)
