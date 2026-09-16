# Evidence directory

This folder holds exactly what the rubric asks for, in the rubric's own section
order — `Multi-Agent Graph → AgentCore Runtime and Guardrails → Memory and
Knowledge Bases → Observability → Industry Best Practices` — plus the automated
test output that backs up each section's scored criteria. Nothing else: no
setup screenshots, no non-graded extras. The previous, broader evidence
collection (built before Task 6's real fix was ported in) is kept at
[`../evidence-old/`](../evidence-old/) for the historical record, not as part
of this submission.

> **Status: complete.** Regenerated against a fresh deployment now that
> Task 6 has a real, working implementation (see `docs/PROJECT_PLAN.md` §18)
> instead of the AWS-SDK-gap workaround the old evidence documented. Real,
> verified **120/120 (100%)** — see `test-scores/all.txt` — and the X-Ray
> Service Map screenshot is captured — see `required/README.md`.

## The one required deliverable

[`required/`](required/) — the X-Ray Service Map screenshot the project
instructions and rubric ask for. See [`required/README.md`](required/README.md).

## Test scores, by rubric section

[`test-scores/`](test-scores/) — the `python tests/test_agent.py <task>`
output for each task, plus the final `all` run. Each file is the direct
evidence for that section's "`python tests/test_agent.py taskN` passes"
requirement.

| Rubric section | Test | File |
|---|---|---|
| Multi-Agent Graph | `task2` | `test-scores/task2.txt` |
| AgentCore Runtime and Guardrails | `task3` | `test-scores/task3.txt` |
| Memory and Knowledge Bases | `task4`, `task5` | `test-scores/task4.txt`, `test-scores/task5.txt` |
| Observability | `task6` | `test-scores/task6.txt` |
| — | `all` (final score) | `test-scores/all.txt` |

Industry Best Practices isn't a separate test — it's a property of
`project/starter/src/agent_orchestrator.py` itself (docstrings, naming,
`config.*_MODEL_ID` used throughout), so there's nothing to capture beyond the
source file already submitted.
