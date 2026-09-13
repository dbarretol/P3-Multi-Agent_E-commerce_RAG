# Evidence directory

This folder is split in two, so a reviewer can find the one thing the rubric actually
asks for without wading through our own internal verification notes.

## `required/`

Contains **only** the one deliverable the project rubric and lesson instructions
explicitly ask for as a screenshot:

> *"Required deliverable: Take a screenshot of your X-Ray Service Map after running a
> live request... capture the full trace graph showing the Orchestrator → Worker call
> chain."* — `7.md` (Phase 4 instructions), matched verbatim in the rubric (`8.md`,
> Observability section) and in the project's deliverables list (`1.md`, item 4).

See `required/README.md` for exactly what it shows and how it was produced.

## `additional-info/`

Everything else: our own internal test-run snapshots, score records, implementation
diffs, and supplementary console screenshots collected while building and verifying
this project. **None of it is required by the rubric** — it exists as our own audit
trail (see `docs/PROJECT_PLAN.md` and `docs/lessons_learned.md` for the full narrative)
and as supporting context for the Task 6 bug report (the automated
`test_agent.py task6` check calls an AWS SDK method that has never existed in any
released boto3/botocore version — see `docs/lessons_learned.md` L17/L19/L21/L22/L23).

**Resource-ID note:** most of the `.txt`/`.diff` snapshots in `additional-info/` were
captured against the **first** deployment (2026-09-12, resource suffix `3153d8d0`).
That deployment was torn down and redeployed the same day (resource suffix
`5b82cc40`) to cover a pause in work — see `docs/lessons_learned.md` L19/L23. The
snapshots still accurately prove each task was implemented and passed at the time
they were taken, but their specific IDs/ARNs won't match the **current** live
resources. For current, live resource IDs, see `.env` or `docs/PROJECT_PLAN.md`'s
"Currently created" table. The one exception is `07-e2e/E7.3-xray-service-graph-
CONNECTED.json` and everything in `additional-info/screenshots/`, which were
regenerated against the current (2nd) deployment during the L23 redeploy session and
do match `.env` as of this writing.
