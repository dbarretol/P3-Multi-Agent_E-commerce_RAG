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

## Rubric section → where it lives

Everything below follows the rubric's own section order, so each part can be
checked off in the same sequence it's graded in.

| Rubric section | Implementation | Evidence |
|---|---|---|
| **Multi-Agent Graph** — worker agents, parallel RAG, Orchestrator routing | `agent_orchestrator.py`: `build_inventory_agent`, `build_refund_agent`, `build_policy_agent` (+ 3 retriever sub-agents), `build_orchestrator_agent` | [`evidence/additional-info/02-agents/`](evidence/additional-info/02-agents/) |
| **AgentCore Runtime and Guardrails** — Guardrail + deployment | `agent_orchestrator.py`: `create_guardrail`, `deploy_to_agentcore_runtime` | [`evidence/additional-info/03-guardrail-runtime/`](evidence/additional-info/03-guardrail-runtime/) |
| **Memory and Knowledge Bases** — session memory + 3 KBs | `agent_orchestrator.py`: `configure_memory`; 3 Bedrock KBs (returns/shipping/warranty) | [`evidence/additional-info/04-memory/`](evidence/additional-info/04-memory/), [`05-kb/`](evidence/additional-info/05-kb/) |
| **Observability** — CloudWatch/X-Ray + Service Map screenshot | `agent_orchestrator.py`: `configure_observability` | [`evidence/required/`](evidence/required/) (the screenshot itself), [`evidence/additional-info/06-observability/`](evidence/additional-info/06-observability/), and [`evidence/TASK6-OBSERVABILITY-BUG.md`](evidence/TASK6-OBSERVABILITY-BUG.md) (known AWS SDK limitation, explained) |
| **Industry Best Practices** — clean code, correct model selection | Throughout `agent_orchestrator.py` — docstrings, naming, `config.*_MODEL_ID` used consistently | [`evidence/additional-info/07-e2e/`](evidence/additional-info/07-e2e/) (final file version + final test run) |

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
