---
name: start
description: Session start protocol — pending work, git status, review gate
---

Session start skill. Run the checklist and produce a status report.

## Steps

### 1. Review gate

Check date of last codebase review in `docs/reviews/`.

A review is **DUE** if:
- > 4 weeks since last codebase review

**When due: flag it prominently.** Bug fixes and content work are exempt.

### 2. Read memory

Read `MEMORY.md` index. Skim any project-type memories for active work.

### 3. Check git status

```bash
git status
git log --oneline -10
```

Note uncommitted changes, unpushed commits, submodule state.

### 4. Check open items

Read `docs/reviews/` for any unchecked items from the last review.
Check if there are any TODO comments in recently changed files.

### 5. Produce the report

```
🔬 **Review Gate**: not due (last YYYY-MM-DD) / DUE — n weeks since last
🌿 **Git State**: clean / uncommitted changes / unpushed commits
📦 **Submodule**: sindrome theme at <commit>

## Open Items
- item 1
- item 2

## Recent Activity
<last 5 commits summarized>

## What's Available
Given the state, here's what we can work on: ...
```

The "What's Available" section is the key output — surface pending
work from reviews, memories, and git state.
