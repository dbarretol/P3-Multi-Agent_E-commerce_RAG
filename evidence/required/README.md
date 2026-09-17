# Required deliverables — screenshots

Captured against the **4th redeploy** (2026-09-16, resource suffix `a29f01a0`,
KB IDs `NWLWTRHQMK`/`DBXGPHVIN9`/`TQHKJ83VJW`). The 3rd redeploy's screenshots
(suffix `434837e0`) are stale — those resources are torn down — and are kept
for the historical record at
[`../../evidence-old/required-3rd-redeploy/`](../../evidence-old/required-3rd-redeploy/).

This redeploy exists specifically to close the gaps from the reviewer's
feedback on the previous submission (see `docs/lessons_learned.md` L31):

> "run `python src/agent_orchestrator.py test` and include screenshots for
> the executing results" / "in AWS console make sure fully deploy your
> solutions including all knowledge bases, and agent core deployment, then
> include screenshots respectively" / "missing required screenshots about
> your knowledge base deployments" / "Please include screenshots to show
> that each KBs uses S3 Vectors backing store pointing to the correct
> VectorStoreBucket and each KB's data source has been synced" / "missing
> screenshots for `python src/agent_orchestrator.py test` passes results"

## 1. `python src/agent_orchestrator.py test` — ✅ done

> 14 sequential terminal screenshots in
> [`orchestrator-cli-test/`](orchestrator-cli-test/) (`01-of-14.png` ...
> `14-of-14.png`), scrolled top-to-bottom through the full run: all 3
> scenarios (CUST-002 return request, CUST-002 premium policy question,
> CUST-003 discount calculation), each ending with a real
> `X-Ray trace ... published successfully` confirmation line.

## 2. `python tests/test_agent.py all` → 120/120 — ✅ done

> [`test-score-120/01-all-tasks-and-final-score-120.png`](test-score-120/) —
> one screenshot, all of Task 2 through Task 6 plus
> `Score: 120/120 pts (100%)` / "Perfect score!", all showing the current
> KB IDs (`NWLWTRHQMK`/`DBXGPHVIN9`/`TQHKJ83VJW`) matching `.env`.

## 3. AWS Console — Knowledge Base deployments — 🟡 partially done

> [`knowledge-bases/`](knowledge-bases/) has one screenshot per KB
> (`01-returns...`, `02-shipping...`, `03-warranty...`), each showing the KB
> ID, status `Available`, RAG type `Vector store`, and its data source
> (`returns-datasource` / `shipping-datasource` / `warranty-datasource`)
> status `Available` (synced). **This covers "data source synced" fully.**
>
> **Still missing:** none of the 3 screenshots show the actual **S3 Vectors
> bucket name / vector index name** the reviewer explicitly asked for — the
> KB overview page only says "Vector store" as the RAG type, not which
> bucket/index it points to. That detail lives on the KB's **Edit** page
> (Vector database configuration section) — please open each KB → **Edit**
> → screenshot the section showing:
> - Vector store: **Amazon S3 Vectors**
> - Vector bucket: `udacity-agentcore-vectors-187021010483-a29f01a0`
> - Vector index: `returns-policy-index` / `shipping-policy-index` /
>   `warranty-policy-index` (matching the KB)
>
> Add these as `04-returns-kb-vector-config.png`,
> `05-shipping-kb-vector-config.png`, `06-warranty-kb-vector-config.png` (or
> similar) in the same folder.

## 4. AWS Console — AgentCore deployment — 🟡 partially done

> [`agentcore-deployment/01-runtime-ready.png`](agentcore-deployment/) shows
> the Runtime (`udacity_agentcore_runtime-zrlU0uFRgf`) status `Ready`.
>
> **Still missing:** the Guardrail screenshot. Please go to **Bedrock →
> Guardrails** → open `83i9l4zhozjl` (v1) → screenshot showing it exists
> with its content/PII/topic policies, status `Ready`. Add as
> `02-guardrail-ready.png` in the same folder.

## 5. X-Ray Service Map — ✅ done

> [`xray-service-map/`](xray-service-map/) — 4 pan/zoom screenshots against
> this deployment's live traces. Together they show all 9 expected nodes
> connected to `NovaMart-Orchestrator`: `Client`, `InventoryAgent`,
> `RefundAgent`, `CommunicationAgent`, `KnowledgeBase:returns`,
> `KnowledgeBase:warranty`, `KnowledgeBase:shipping` (image 01), plus
> `RefundAgent`/`PolicyAgent`/`KnowledgeBase:returns` (02), the Orchestrator
> reconverged with `KnowledgeBase:warranty`/`shipping`/`InventoryAgent` (03),
> and `KnowledgeBase:shipping`/`InventoryAgent`/`CommunicationAgent` (04).

---

**Remaining gaps: 2 screenshots** — the KB vector-store config (#3) and the
Guardrail page (#4). Once those are in, update this README's status lines
(and `../README.md`) to all-✅.
