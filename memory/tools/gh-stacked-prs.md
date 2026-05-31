---
name: gh stacked PRs — auto-close on parent merge
description: Squash-merging a parent PR with --delete-branch closes any child PRs targeting that branch; reopen is blocked. Use cherry-pick onto master to recover.
type: reference
---

When you stack PR B on top of PR A (`gh pr create --base feature/A`), and PR A is squash-merged with `gh pr merge --delete-branch`, GitHub will:

1. **Auto-close PR B** because its base branch no longer exists.
2. **Block `gh pr reopen`** with `Could not open the pull request` — the missing base branch can't be referenced.
3. **Block `gh pr edit --base master`** with `Cannot change the base branch of a closed pull request`.

PR B is effectively dead. The remote head branch still exists.

**Recovery (no force-push):**

```bash
git fetch origin --prune
git checkout -b feature/B-v2 origin/master
git cherry-pick <SHA_of_B's_unique_commit>
git push -u origin feature/B-v2
gh pr create --base master --head feature/B-v2 --title "..."
```

The cherry-pick reapplies B's net diff onto current master (which contains A's squashed content). Auto-merge usually handles any CLAUDE.md-style overlap cleanly because A's content is identical to A's pre-squash state. The original orphan branch and closed PR #B can be left in place; no destructive cleanup required.

**To avoid the dance entirely:** for stacked work, hold off on `--delete-branch` when merging the parent until the child is merged too — or merge parent without `--delete-branch` so the child can be retargeted before the base disappears.
