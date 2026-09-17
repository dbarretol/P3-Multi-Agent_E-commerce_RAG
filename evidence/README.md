# Evidence directory

This folder holds exactly what the rubric asks for, in the rubric's own section
order — `Multi-Agent Graph → AgentCore Runtime and Guardrails → Memory and
Knowledge Bases → Observability → Industry Best Practices` — plus the automated
test output that backs up each section's scored criteria. Nothing else: no
setup screenshots, no non-graded extras. The previous, broader evidence
collection (built before Task 6's real fix was ported in) is kept at
[`../evidence-old/`](../evidence-old/) for the historical record, not as part
of this submission.

> **Status: in progress — 4th redeploy (2026-09-16, suffix `a29f01a0`).**
> A reviewer pass on the previous submission asked for more: a screenshot of
> `python src/agent_orchestrator.py test`, and AWS Console screenshots proving
> the Knowledge Bases and AgentCore Runtime/Guardrails are fully deployed
> (S3 Vectors backing store per KB, data source sync status). Everything was
> torn down after that submission, so this is a fresh live deployment. Real,
> verified **120/120 (100%)** — see `test-scores/all.txt`. Screenshots are
> pending — see `required/README.md` for exactly what's needed and where.

## The required deliverables

Per the project instructions plus reviewer feedback, submission requires:
(1) completed `agent_orchestrator.py`, (2) populated `.env`, (3) a screenshot
of `python src/agent_orchestrator.py test` passing, (4) a screenshot of the
120/120 `tests/test_agent.py all` score, (5) AWS Console screenshots of the
3 Knowledge Bases (S3 Vectors backing store + synced data sources) and the
AgentCore Runtime/Guardrails, and (6) the X-Ray Service Map screenshot.
(1) and (2) are the source/config already in this repo; (3)-(6) are in
[`required/`](required/) — see [`required/README.md`](required/README.md).

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
