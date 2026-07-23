# Codex Repository Workflow

These instructions define how Codex must work in this repository. The goal is
safe, traceable, and reviewable work across Issues, branches, commits, Pull
Requests, reviews, validation, and documentation.

This file is the authoritative contribution, security, and reproducibility
policy for Codex. A README may summarize or link to it, but must not maintain a
separate conflicting copy of these rules.

---

## 0. Core rules

- Follow all applicable `AGENTS.md` files. Deeper files override broader ones
  within their directory scope.
- If a higher-priority runtime instruction conflicts with this file, follow it
  and report the conflict.
- Inspect before changing anything.
- Ask a human when ambiguity materially affects behavior, compatibility,
  security, data, architecture, destructive operations, scope, or acceptance
  criteria. For minor details, choose the safest reasonable option and document
  it.
- Never discard, overwrite, reset, clean, or stash human work without explicit
  authorization.
- Keep each PR focused on one Issue. If scope grows substantially, stop
  expanding it and create or propose linked follow-up Issues.
- Never claim that a command, test, review, CI check, or merge succeeded unless
  it was actually run and observed.
- Never bypass branch protection, required checks, or required reviews.

---

## 1. New repository bootstrap

Treat a repository as new only when it has no meaningful history and is
essentially empty.

Before scaffolding, confirm unresolved choices that are difficult to reverse:
stack and package manager, visibility, license, default branch, minimum runtime,
and whether CI is included now.

Create only the confirmed essentials: `README.md`, `.gitignore`, optional
`LICENSE`, base folders, dependency manifest, and baseline validation config.

The initial scaffold is the only work that may go directly to the default
branch:

```bash
git init -b main
git add -A
git commit -m "chore: initial project scaffold"
git push -u origin main
```

After that first scaffold, use the normal Issue → branch → PR workflow.

---

## 2. Preflight inspection

Before modifying an existing repository, run or equivalent:

```bash
git status --short
git branch --show-current
git remote -v
gh auth status
```

Determine the actual default branch, applicable instructions, working-tree
safety, GitHub access, project type, package manager, CI workflows, and all
supported test/lint/format/type-check/build/notebook commands.

### Existing local changes

If uncommitted changes were not created for the current task:

- do not discard, overwrite, reset, clean, or stash them;
- avoid switching branches when it may endanger them;
- stop and report the conflict if safe isolation is impossible.

### GitHub unavailable

If GitHub or the remote is unavailable:

- do not fabricate an Issue, PR, review, check, or merge;
- report the exact blocker and do not push or merge;
- continue locally only when the user explicitly authorizes local-only work;
- then use a local branch, validate the change, and report pending GitHub steps.

---

## 3. Detect validation commands

Use only commands supported by repository configuration; never invent scripts.

- **Node.js/TypeScript:** inspect `package.json`, lockfiles, workspaces, and
  framework config. Use the package manager matching the lockfile.
- **Python:** inspect `pyproject.toml`, pytest/tox/nox/setup config, lockfiles,
  `tests/`, and configured tools such as Ruff, mypy, or Pyright.
- **Other tooling:** inspect Make, Just, Task, pre-commit, and project scripts.
- **Notebooks/data-intensive projects:** if no automated suite exists, define
  specific manual checks: clean-kernel execution, top-to-bottom reproducibility,
  expected rows/metrics/plots/exports, portable paths, and no private or
  oversized data in Git.

Examples, only when configured:

```bash
npm test
npm run lint
pytest
ruff check .
pre-commit run --all-files
```

Record exact commands and results in the Issue or PR. Never write only “tests
passed” or “manually tested.”

---

## 4. Require an Issue

Every task that changes repository files needs a linked Issue. Pure read-only
explanation, investigation, triage, or review does not require a new Issue
unless requested.

Search open and closed Issues first:

```bash
gh issue list --state all --search "<keywords>" --limit 50
```

Use an existing Issue when it represents the task. Otherwise create one with
context, problem, scope, acceptance criteria, and verification plan:

```bash
gh issue create \
  --title "<clear task title>" \
  --body "<context, scope, acceptance criteria, and verification plan>"
```

---

## 5. Create a safe branch

Never commit or push task work directly to the default branch, except for the
one-time bootstrap exception.

```bash
git fetch origin
git switch <default-branch>
git pull --ff-only origin <default-branch>
git switch -c feat/12-short-description
```

Use lowercase, hyphen-separated names:

- `feat/<issue>-<description>`
- `fix/<issue>-<description>`
- `docs/<issue>-<description>`
- `test/<issue>-<description>`
- `refactor/<issue>-<description>`
- `chore/<issue>-<description>`
- `revert/<issue>-<description>`

Do not reuse a stale branch without checking its history.

---

## 6. Implement the agreed scope

Inspect relevant code, tests, documentation, configuration, and nearby
conventions before editing.

- Follow existing architecture and style.
- Avoid unrelated refactors and mass formatting.
- Preserve compatibility unless the Issue explicitly changes it.
- Add or update tests when behavior changes.
- Change fixtures, snapshots, generated files, or lockfiles only when required
  and understood.
- Do not suppress warnings or checks merely to make CI green.
- For notebooks, preserve reproducibility, avoid hidden state, minimize
  unnecessary output, and document required data and expected outputs.

---

## 7. Security, data, access, and destructive operations

Never commit credentials, tokens, passwords, keys, service-account files,
secret-bearing `.env` files, private datasets, or unapproved personal data.

Before every commit:

```bash
git status --short
git diff --cached --name-only
git diff --cached
```

Ignore sensitive patterns where appropriate while preserving safe examples such
as `.env.example`:

```text
.env
.env.*
*.pem
*.key
credentials*.json
service-account*.json
```

If a suspected secret was staged, remove it and replace hardcoding with secure
configuration. If it may already have been committed or pushed, stop and notify
a human. Do not rewrite history or rotate credentials without authorization.

Never perform these actions without explicit authorization:

- `git reset --hard`, `git clean -fd`, `git clean -fdx`, or equivalent cleanup;
- force-push or published-history rewriting;
- recursive deletion outside known generated/temp directories;
- deleting databases, datasets, storage, user files, or production resources;
- destructive migrations, deployments, or irreversible infrastructure actions.

### Access and contribution ethics

- Use only the authenticated identity and repository access granted for the task.
- Do not change repository visibility, collaborators, teams, permissions,
  branch protection, rulesets, environments, secrets, webhooks, or billing unless
  explicitly authorized and in scope.
- Never use an alternate account, administrator bypass, or weaker workflow to
  evade review or security controls.
- Do not expose secrets, private data, vulnerability details, or personal data in
  Issues, PRs, comments, commit messages, screenshots, logs, or generated output.
- Respect repository licenses, dataset licenses, attribution requirements, and
  third-party terms.
- Do not manipulate contribution activity with duplicate Issues, empty commits,
  artificial PRs, or meaningless review comments.

### Commit signing and DCO

Inspect repository rules and contribution documentation before committing.

- If signed commits are required, use the repository-supported signing method,
  such as `git commit -S`.
- If Developer Certificate of Origin sign-off is required, use
  `git commit -s` so the commit contains the contributor's own
  `Signed-off-by` trailer.
- If both are required, use both signing and sign-off.
- Never fabricate a signature, sign-off, identity, or trailer for another person.
- If the required signing key or identity is unavailable, stop before committing
  and report the blocker.

### Data-intensive applications and untrusted input

For dashboards, APIs, notebooks, data pipelines, analytics applications, and
machine-learning systems:

- Never commit runtime secret files. Use documented placeholder files containing
  only safe example values. Framework configuration may be committed only when
  it contains no credentials or private endpoints.
- Ignore sensitive or local artifacts where appropriate, for example:

  ```text
  .streamlit/secrets.toml
  data/raw/
  data/private/
  artifacts/private/
  *.db
  ```

  Adapt these patterns when the repository intentionally tracks a listed path.
- Do not commit private, licensed, personal, or oversized datasets. Prefer
  approved samples, schemas, source links, checksums, and reproducible download
  or preparation scripts.
- Track generated datasets, plots, reports, notebooks, caches, and model artifacts
  only when intentional, reproducible, appropriately licensed, and reasonably
  sized.
- Document data and model provenance, source/version, preprocessing, features,
  expected input schema, evaluation metrics, and compatibility requirements.
- Never deserialize untrusted executable artifacts such as `.pkl`, `.pickle`,
  or `.joblib` files.
- Treat uploaded, downloaded, and externally supplied files as untrusted. Validate
  size, declared and actual format, schema, required fields, data types, missing
  values, ranges, malformed content, and resource consumption before processing.
- Do not log, persist, or cache secrets, personal data, complete prediction inputs,
  uploaded content, or cross-user session data unless explicitly required and
  approved.
- Keep reusable validation, preprocessing, business logic, inference, and
  visualization code separate from the presentation or web-framework layer when
  practical so it can be tested directly.
- For dashboard or web-application changes, use configured automated tests and
  framework-specific test utilities when practical. Also run a bounded startup
  smoke test and verify key navigation, controls, filters, uploads, empty states,
  errors, authorization boundaries, and data/model outputs.
- Document supported runtime versions, deployment dependencies, required secrets,
  data/model locations, resource assumptions, and the command used to start the
  application.

---

## 8. Commit in meaningful units

Use small, coherent Conventional Commit-style commits:

```text
feat: add transaction risk filter
fix: handle missing values in parser
test: cover expired session behavior
docs: document required environment variables
refactor: extract notebook preprocessing helpers
```

Use `Refs #12` in the commit body when useful. Close the Issue through the PR,
not every commit.

Do not create empty commits for contribution counts, combine unrelated work, or
amend human-authored commits without authorization.

---

## 9. Open a draft PR early

After the first meaningful commit:

```bash
git push -u origin <branch-name>
gh pr create --draft --title "<clear PR title>" --body-file <pr-body-file>
```

Even a small completed task should enter GitHub as a draft first, be validated,
and then be marked ready.

The PR body must include:

```markdown
## What changed
- ...

## Why
- ...

## Verification
- `exact command` — passed
- Manual verification: ...

## Documentation
- Updated ...
- Not required because ...

## Risks and edge cases
- ...

Closes #12
```

Push subsequent commits to the same draft PR.

---

## 10. Validate dependencies, execution, and documentation

Run targeted checks during implementation and the full relevant suite after
completion. This may include tests, lint, formatting, types, build, packaging,
notebook execution, bounded dashboard/application smoke tests, and manual
functional checks.

### Dependency changes and security checks

When adding or upgrading a dependency:

- confirm it is necessary and prefer an existing dependency when suitable;
- use the repository's package manager and update the lockfile consistently;
- avoid unbounded version ranges unless repository policy intentionally uses them;
- run the configured ecosystem security audit when available, such as
  `npm audit`, `pnpm audit`, `yarn npm audit`, or `pip-audit`;
- record the command, findings, and any accepted residual risk in the PR;
- do not claim an audit passed when no audit tool is configured or available;
- do not run forceful automatic remediation that introduces major upgrades or
  broad changes, such as `npm audit fix --force`, without explicit authorization;
- update setup/dependency documentation when installation or deployment changes.

### Execution reliability and retry limits

- Use bounded timeouts or explicit stop criteria for servers, watchers, notebook
  execution, data downloads, model training, and commands that may wait forever.
- Do not leave dashboard servers, development servers, notebook kernels,
  training processes, or watch processes running indefinitely after verification.
- Never repeat an identical failing or hanging command indefinitely. After the
  initial attempt, allow at most two retries, and only when the diagnosis, input,
  environment, or command has materially changed.
- For likely transient network or CI failures, retry at most twice with a
  reasonable delay; do not continuously poll.
- After the retry limit, stop and report the exact command, observed failure,
  attempts made, and the next recommended action.

When a required check fails, fix failures caused by the change and rerun them.
Record unrelated or environmental failures exactly. Do not hide failures or
merge unless repository policy and a human explicitly permit proceeding.

Update documentation in the same PR when setup, dependencies, environment
variables, configuration, API/CLI behavior, data formats, notebook execution,
expected inputs/outputs, or user-visible behavior changes. Otherwise explain
why existing documentation remains accurate.

---

## 11. Synchronize and self-review

Before marking the PR ready, merge the latest default branch into the task
branch; do not rebase or force-push:

```bash
git fetch origin
git merge origin/<default-branch>
```

Resolve conflicts carefully, inspect the result, rerun affected validation,
and push. If repository rules require linear history, stop and report the
policy conflict.

Review both diffs:

```bash
git diff origin/<default-branch>...HEAD
gh pr diff <pr-number>
```

Check correctness, acceptance criteria, regressions, security, data leakage,
error handling, edge cases, tests, docs, generated files, secrets, and scope.

When working solo, leave substantive self-review notes:

```bash
gh pr review <pr-number> --comment --body-file <review-notes-file>
```

Self-review is not independent approval and must not bypass protection rules.

---

## 12. Mark ready and handle review

When implementation, validation, documentation, synchronization, and
self-review are complete:

```bash
gh pr ready <pr-number>
```

If a human reviewer is available or required:

```bash
gh pr edit <pr-number> --add-reviewer <username>
```

Then stop and report that merge is pending human approval. Do not poll
indefinitely or self-merge while approval is pending. Recheck approval after new
commits.

When reviewing another PR, inspect the full diff and linked Issue, run relevant
checks when feasible, and use `--comment`, `--request-changes`, or `--approve`
according to actual findings.

---

## 13. Confirm CI and merge eligibility

```bash
gh pr checks <pr-number>
gh pr view <pr-number> \
  --json isDraft,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
```

Use `gh pr checks <pr-number> --watch --fail-fast` only when waiting is
appropriate.

Do not merge while the PR is draft, checks are pending/failing, validation or
approval is missing, requested changes remain, conflicts exist, docs are
incomplete, secrets are present, scope is exceeded, or repository rules reject
the merge method.

If no CI exists, state that explicitly instead of claiming CI is green.

---

## 14. Merge only with explicit authorization

“Fix this issue” or “open a PR” does not authorize merging. Authorization must
be explicit, for example:

- “Merge when all checks pass.”
- “Complete the task through merge.”
- “You may merge this PR after approval.”

Without explicit authorization, stop after the PR is ready and report status.

Use squash merge unless repository policy says otherwise, and protect against
the PR head changing after review:

```bash
HEAD_SHA="$(git rev-parse HEAD)"
gh pr merge <pr-number> \
  --squash \
  --delete-branch \
  --match-head-commit "$HEAD_SHA"
```

Merge only when GitHub reports it mergeable and all checks, reviews, rules, and
authorization requirements are satisfied. Never bypass protections with admin
privileges.

---

## 15. Close the loop

Use `Closes #<issue>` in the PR body. After merge:

1. verify the PR merged and the Issue closed;
2. close the Issue manually only if it should have closed but did not;
3. update the local default branch with `git pull --ff-only`;
4. confirm the worktree is clean.

The final report must state the Issue, branch, commits, PR, exact validation
results, documentation changes, review/CI status, merge status, and remaining
risks or follow-up Issues.

---

## 16. Handle regressions through a PR

Never push a regression fix or revert directly to the default branch.

Prefer:

```bash
gh pr revert <original-pr-number> \
  --title "revert: <original PR title>" \
  --body "Reverts #<original-pr-number> because <reason>."
```

Then follow normal validation, review, CI, authorization, and merge rules.

If automated reversion is unavailable, create a regression Issue and revert
branch. For a squash-merged PR:

```bash
git revert <squash-commit-sha>
```

Use `-m` only for an actual merge commit after verifying the mainline parent.
Urgency may reduce validation to the minimum reliable set, but never permits a
direct push to the default branch.

---

## 17. Compact checklist

- [ ] Instructions, repository state, project type, CI, and validation commands inspected.
- [ ] Existing human work is safe.
- [ ] Existing Issue linked or non-duplicate Issue created.
- [ ] Work performed on a correctly named branch from the updated default branch.
- [ ] Scope stayed focused; follow-up work separated.
- [ ] Commits are coherent, correctly signed/signed-off when required, and free of secrets/private data.
- [ ] Dependency audits and bounded execution/retry rules were applied when relevant.
- [ ] Data, upload, model, secret, untrusted-input, and deployment safeguards were checked.
- [ ] Draft PR links the Issue and records exact validation and docs status.
- [ ] Latest default branch merged without force-push; affected checks rerun.
- [ ] Substantive self-review completed.
- [ ] Required human review and CI checks completed.
- [ ] Merge used explicit authorization and matching head SHA.
- [ ] PR/Issue closure, local sync, clean worktree, and final report verified.
- [ ] Regressions use a revert PR, never a direct push.
