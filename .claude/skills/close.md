---
name: close
description: End-of-session protocol — push, update docs and memories, report
---

Session closing skill. Invoke with `/close` at end of session.

## Steps

### 1. Push unpushed commits

```bash
git log --oneline origin/master..HEAD
```

If commits exist, push. Check submodule too:
```bash
cd themes/sindrome && git log --oneline origin/master..HEAD
```

Push both if needed (submodule first, then parent).

### 2. Stage and ship if needed

If there are commits that haven't been deployed yet, ask if the user
wants to stage/ship before closing. Don't assume — ask.

### 3. Update memories

Review the session for anything worth remembering:
- **Feedback**: Did the user correct your approach? Save it.
- **Project**: Did you learn about ongoing work, decisions, or context?
- **User**: Did you learn about preferences, role, or knowledge?
- **Reference**: Did you discover external resources or systems?

Check existing memories for any that are now stale or wrong. Update
or remove them.

**Do NOT save**: code patterns (read the code), git history (use git
log), debugging solutions (the fix is in the code), or anything
already in CLAUDE.md.

### 4. Update review docs if needed

If this session addressed items from a review in `docs/reviews/`,
update the checklist (mark items done, add notes).

### 5. Final commit and push

Commit any doc/memory changes:
```
docs: close session — <what was updated>
```

Push to remote.

### 6. Report

Tell the human:
- Commits pushed (count + range)
- What was deployed (staging/prod/nothing)
- Memories updated (list)
- Review items closed (if any)
- Pending work for next session
