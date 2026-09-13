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
| [`evidence/`](evidence/) | The required rubric deliverable (X-Ray Service Map) plus supporting evidence collected while building and verifying this project. |

## Status

All tasks are implemented and verified live against a real AWS deployment — see
[`project/starter/README.md`](project/starter/README.md) for the full task
breakdown. One automated check in Task 6 calls a boto3 method that has never
shipped in any released AWS SDK version; `configure_observability()` still
implements the real, currently-shipping equivalent (CloudWatch Logs Delivery API
for X-Ray and log delivery), verified live end to end. See
[`evidence/TASK6-OBSERVABILITY-BUG.md`](evidence/TASK6-OBSERVABILITY-BUG.md) for
the investigation behind that.

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
