# NovaMart Multi-Agent E-commerce RAG

Udacity AWS Agentic AI Nanodegree — Capstone Project (cd14764).

A production-grade multi-agent customer support system built with the
[Strands Agents SDK](https://github.com/strands-agents/sdk-python) and Amazon
Bedrock AgentCore. Five agents (Orchestrator, Inventory, Policy, Refund,
Communication) collaborate to handle order lookups, refund decisions, and
policy questions — routing between specialists, retrieving grounded answers via
parallel multi-agent RAG across three Bedrock Knowledge Bases, enforcing
Bedrock Guardrails, and maintaining shared state across a full request.

## Where things are

| Path | What's there |
|---|---|
| [`project/starter/`](project/starter/) | The actual implementation — `src/agent_orchestrator.py`, tests, infrastructure template. See its own `README.md` for architecture, setup, and a full task-by-task breakdown. |
| [`evidence/`](evidence/) | The required rubric deliverable and supporting evidence. **Start with [`evidence/TASK6-OBSERVABILITY-BUG.md`](evidence/TASK6-OBSERVABILITY-BUG.md)** if you're reviewing this submission — it explains the one score gap up front. |

## Current status

`python tests/test_agent.py all` (run from `project/starter/`) scores **100/120**.
The 20-point gap is Task 6's automated observability check, which calls a boto3
method that has never existed in any released AWS SDK — confirmed multiple
independent ways and explained in full in
[`evidence/TASK6-OBSERVABILITY-BUG.md`](evidence/TASK6-OBSERVABILITY-BUG.md).
Every other task, and the actual required X-Ray Service Map deliverable, is
complete and verified live against a real AWS account.

## Quick start

```bash
cd project/starter
uv venv --python 3.12
uv pip install -r requirements.txt
cp .env.example .env   # then fill in AWS credentials + resource IDs, see below
python config.py       # sanity-check configuration
python tests/test_agent.py all
```

Full setup, deployment, and per-task instructions are in
[`project/starter/README.md`](project/starter/README.md).
