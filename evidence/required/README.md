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

## 1. `python src/agent_orchestrator.py test` — ⚠️ needs your screenshot

> This is a **different command** than `tests/test_agent.py` — it's the
> orchestrator's own built-in test mode (3 real customer-support scenarios,
> run through the real multi-agent graph with live CloudWatch/X-Ray tracing).
> Already confirmed working end-to-end against this deployment (3 scenarios
> completed, 3 X-Ray traces published) — this screenshot just needs to be
> your own terminal capture of a real run.
>
> **To capture:** from `project/starter`, with the venv active and `.env`
> loaded, run:
> ```
> python src/agent_orchestrator.py test
> ```
> Screenshot the terminal showing all 3 scenarios' output (may need 2+ images
> if it doesn't fit one screen, same as the test-score capture below — name
> them `01-....png`, `02-....png` etc.).
>
> Save into [`orchestrator-cli-test/`](orchestrator-cli-test/).

## 2. `python tests/test_agent.py all` → 120/120 — ⚠️ needs your screenshot

> Re-verified 2026-09-16 against this deployment: real, live **120/120
> (100%)** — see `../test-scores/all.txt`. The previous screenshot
> (3rd redeploy) is stale since those KB IDs/runtime no longer exist —
> needs a fresh capture so the on-screen KB IDs match the current `.env`.
>
> **To capture:** from `project/starter`, with the venv active and `.env`
> loaded:
> ```
> python tests/test_agent.py all
> ```
> Screenshot the terminal (likely 2 images, top half + bottom half, same as
> before). Save into [`test-score-120/`](test-score-120/).

## 3. AWS Console — Knowledge Base deployments — ⚠️ needs your screenshots

> Reviewer specifically wants to see, **for each of the 3 KBs**: it uses the
> **S3 Vectors backing store**, pointing to the correct `VectorStoreBucket`
> (`udacity-agentcore-vectors-187021010483-a29f01a0`), with its matching
> vector index name, **and** that its data source shows as synced.
>
> **To capture**, in the AWS Console (region `us-east-1`):
> 1. Go to **Amazon Bedrock → Knowledge Bases**. Screenshot the list showing
>    all 3 KBs (`returns`, `shipping`, `warranty`) with status `Available`.
> 2. Open **each** KB's detail page individually. On each, screenshot the
>    section showing:
>    - Storage configuration: **S3 Vectors**, bucket
>      `udacity-agentcore-vectors-187021010483-a29f01a0`, vector index
>      (`returns-policy-index` / `shipping-policy-index` /
>      `warranty-policy-index` respectively)
>    - The **Data source** tab/section showing sync status = `Available`
>      (i.e. last sync completed, not "Syncing" or "Failed")
>
> That's 1 list screenshot + up to 2 per KB (config + data source) = ~7
> images total, or fewer if a KB's detail page fits both in one screenshot.
> Name them descriptively, e.g. `01-kb-list-all-three-active.png`,
> `02-returns-kb-s3vectors-config.png`, `03-returns-kb-datasource-synced.png`,
> `04-shipping-kb-s3vectors-config.png`, ... etc.
>
> Save into [`knowledge-bases/`](knowledge-bases/).

## 4. AWS Console — AgentCore deployment — ⚠️ needs your screenshots

> Reviewer wants to see the AgentCore side "fully deployed" too — Runtime
> and Guardrails.
>
> **To capture:**
> 1. **Bedrock AgentCore → Agent Runtime** → open
>    `udacity_agentcore_runtime-zrlU0uFRgf` → screenshot showing status
>    `READY`/`Active`.
> 2. **Bedrock → Guardrails** → open `83i9l4zhozjl` (v1) → screenshot showing
>    it exists with its content/PII/topic policies, status `Ready`.
>
> Save into [`agentcore-deployment/`](agentcore-deployment/).

## 5. X-Ray Service Map — ⚠️ needs your screenshot (re-capture)

> The 3rd-redeploy screenshots are stale (those resources are deleted) —
> needs a fresh capture against this deployment's live traces. 3 traces
> already confirmed received (from the `agent_orchestrator.py test` run
> above) — allow the usual 30-60s propagation window before opening the
> console.
>
> **To capture:** CloudWatch → X-Ray traces → Service map (region
> `us-east-1`, 6h window). Same as before, the full graph likely won't fit
> one screen — pan/zoom and capture multiple overlapping views, same
> approach as last time.
>
> Save into [`xray-service-map/`](xray-service-map/).

---

Once all 5 categories above have real screenshots in place, update this
README's status lines (and `../README.md`) to ✅, same pattern as the
3rd-redeploy version.
