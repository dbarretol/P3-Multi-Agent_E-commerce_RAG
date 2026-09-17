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

## 3. AWS Console — Knowledge Base deployments — ✅ done

> [`knowledge-bases/`](knowledge-bases/) has 11 screenshots:
> - `01`-`03`: each KB's overview (ID, status `Available`, RAG type
>   `Vector store`) and its data source status `Available`.
> - `04`/`06`/`08`: each data source's own detail page — sync history
>   `Complete`, 2 scanned / 2 added / 0 failed.
> - `05`/`07`/`09`: each data source's Documents list — both seeded policy
>   docs `INDEXED`.
> - `10`: the **S3 Vectors** service's "Vector buckets" list (a separate
>   AWS resource type from regular S3 — see `docs/lessons_learned.md` L14),
>   showing `udacity-agentcore-vectors-187021010483-a29f01a0`
>   (`arn:aws:s3vectors:...`).
> - `11`: that vector bucket's **3 vector indexes** —
>   `returns-policy-index`, `shipping-policy-index`, `warranty-policy-index`
>   — each with its full ARN, matching the 3 KBs exactly.
>
> Together: each KB is `Available` with a synced data source (`01`-`09`),
> and the S3 Vectors backing store + matching index per KB is confirmed
> (`10`-`11`) — both parts of the reviewer's ask are covered. Note: AWS's
> Bedrock KB console (both the overview page and the Edit wizard) doesn't
> surface the vector-store binding directly — it had to be found via the
> S3 Vectors service's own console pages instead.

## 4. AWS Console — AgentCore deployment — ✅ done

> [`agentcore-deployment/`](agentcore-deployment/): `01-runtime-ready.png`
> shows the Runtime (`udacity_agentcore_runtime-zrlU0uFRgf`) status `Ready`;
> `02-guardrail-ready.png` shows Guardrail `udacity-agentcore-guardrail`
> (`83i9l4zhozjl`, v1) status `Ready` with its content/PII/topic policies.

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

**All 5 deliverables complete.** See `../README.md` for overall status.
