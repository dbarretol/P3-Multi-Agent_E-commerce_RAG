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
| [`evidence/`](evidence/) | The two required screenshots (120/120 test score, X-Ray Service Map) plus per-task automated test output. The prior, broader evidence collection is kept at [`evidence-old/`](evidence-old/) for historical record. |

## Rubric section → where it lives

Everything below follows the rubric's own section order, so each part can be
checked off in the same sequence it's graded in.

| Rubric section | Implementation | Evidence |
|---|---|---|
| **Multi-Agent Graph** — worker agents, parallel RAG, Orchestrator routing | `agent_orchestrator.py`: `build_inventory_agent`, `build_refund_agent`, `build_policy_agent` (+ 3 retriever sub-agents), `build_orchestrator_agent` | [`evidence/test-scores/task2.txt`](evidence/test-scores/task2.txt) |
| **AgentCore Runtime and Guardrails** — Guardrail + deployment | `agent_orchestrator.py`: `create_guardrail`, `deploy_to_agentcore_runtime` | [`evidence/test-scores/task3.txt`](evidence/test-scores/task3.txt) |
| **Memory and Knowledge Bases** — session memory + 3 KBs | `agent_orchestrator.py`: `configure_memory`; 3 Bedrock KBs (returns/shipping/warranty) | [`evidence/test-scores/task4.txt`](evidence/test-scores/task4.txt), [`task5.txt`](evidence/test-scores/task5.txt) |
| **Observability** — CloudWatch/X-Ray + Service Map screenshot | `agent_orchestrator.py`: `configure_observability` (real CloudWatch/X-Ray integration, `src/agent_observability.py`) | [`evidence/test-scores/task6.txt`](evidence/test-scores/task6.txt), [`evidence/required/xray-service-map/`](evidence/required/xray-service-map/) |
| **Industry Best Practices** — clean code, correct model selection | Throughout `agent_orchestrator.py` — docstrings, naming, `config.*_MODEL_ID` used consistently | source file itself |

## Status

**Complete — real, verified 120/120 (100%).** All tasks are implemented and
verified live against a real AWS deployment — see
[`project/starter/README.md`](project/starter/README.md) for the full task
breakdown. Task 6 (Observability) uses a genuine CloudWatch/X-Ray integration
(`src/agent_observability.py`, ported from Udacity's own upstream starter-kit
update) rather than a workaround — see
[`evidence/test-scores/all.txt`](evidence/test-scores/all.txt) and
[`evidence/required/`](evidence/required/) for the two required screenshots.

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
