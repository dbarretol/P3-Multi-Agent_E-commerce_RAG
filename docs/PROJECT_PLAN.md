# NovaMart Multi-Agent E-commerce RAG — Execution Plan

**Course:** Udacity nd905 / `cd14764` — Course 3.3, Capstone Project 3.3
**Source of truth:** `C:\Dev_Projects\LEARN\AWS\AWS-AGENT-ENGINEER\3-Multi-Agent Systems and Protocol Integration on AWS\19-Multi-Agent E-commerce RAG\{1..8}.md`
**Working copy:** `C:\WORKSPACES\AWS-UDACITY\P3-Multi-Agent_E-commerce_RAG\project\starter\`
**Region (fixed):** `us-east-1`

---

## 1. Ground rules

| Rule | Detail |
|---|---|
| **Only file you edit** | `project/starter/src/agent_orchestrator.py` (TODOs for Tasks 2, 3, 4, 6) |
| **Never modify** | `config.py`, `tests/test_agent.py`, `src/agent_utils.py`, `src/bedrock_kb_retrieval.py`, `src/demo.py`, `infrastructure/*` |
| **Model IDs** | Always reference `config.ORCHESTRATOR_MODEL_ID` (Haiku) and `config.WORKER_MODEL_ID` (Sonnet). Never hardcode a model string. |
| **Run commands from** | `project/starter/` (so `load_dotenv()` finds `.env`) |
| **Package manager** | `uv`. Create the env with `uv venv`, install with `uv pip install -r requirements.txt`. Run project commands either after activating `.venv`, or by prefixing with `uv run` (e.g. `uv run python tests/test_agent.py all`). Every bare `python …` command in this plan assumes the `.venv` is active. |
| **Credentials** | Udacity STS temp creds in `project/starter/.env` (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN`). Expire in a few hours — re-paste on `ExpiredToken` / `InvalidClientTokenId`. |
| **Test scoring** | `python tests/test_agent.py <taskN|all>` prints `Score: X/Y pts`. Target = 120/120. |

### Test point budget (from `tests/test_agent.py`)

| Task | Checks | Points |
|---|---|---|
| task2 | agent instantiation, tool counts (Inv=3, Policy=1, Orch=5), model split (Haiku/Sonnet) | 40 |
| task3 | guardrail exists + has content/PII/topic policies, runtime ARN set | 20 |
| task4 | AgentCore Memory `SESSION_SUMMARY` enabled | 15 |
| task5 | 3 KB IDs set in env + each KB `ACTIVE` | 25 |
| task6 | CloudWatch logging enabled + X-Ray tracing enabled | 20 |
| **Total** | | **120** |

---

## 2. Required submission deliverables

- [ ] **D1** — Completed `src/agent_orchestrator.py` (all TODOs for Tasks 2, 3, 4, 6)
- [ ] **D2** — Three Bedrock Knowledge Bases created in the AWS Console, data sources **synced**
- [ ] **D3** — Populated `.env`: `RETURNS_KB_ID`, `SHIPPING_KB_ID`, `WARRANTY_KB_ID`, `AGENTCORE_RUNTIME_ARN`, `GUARDRAIL_ID`, `GUARDRAIL_VERSION`
- [ ] **D4** — X-Ray **Service Map screenshot** showing Orchestrator → worker call chain after a live request

---

## 3. Milestone map

| # | Milestone | Gate (objective, verifiable pass condition) | Blocks |
|---|---|---|---|
| **M0** | Environment ready | `python config.py` prints the config table with all CloudFormation-sourced rows populated; `python tests/test_agent.py task2` runs (score may be 0) | everything |
| **M1** | Worker agents build | `task2` checks 2.1–2.4, 2.7 pass (≥ 30/40) | M3 |
| **M2** | Orchestrator builds + routes | `task2` = **40/40**; `python src/demo.py` completes a full refund flow end-to-end locally | M5 |
| **M3** | Knowledge Bases live | `task5` = **25/25**; all 3 KBs `ACTIVE`; `search_all_policies("...")` returns non-empty text from Returns **and** Shipping **and** Warranty | M4 (policy path) |
| **M4** | Guardrail + Runtime deployed | `task3` = **20/20**; deploy command prints Runtime ARN + Guardrail id/version; values in `.env` | M6 |
| **M5** | Memory configured | `task4` = **15/15** | — |
| **M6** | Observability configured | `task6` = **20/20** | M7 |
| **M7** | End-to-end proof | 3 canonical scenarios routed correctly via deployed runtime; X-Ray Service Map screenshot captured; `python tests/test_agent.py all` = **120/120** | submission |

---

## 4. Phase 0 — Environment setup → **M0** ✅ UNBLOCKED (2026-09-09) — moved to a personal AWS account

> **History (kept for record):** Blocked 2026-09-02 on the AWS Academy learner-lab account — Bedrock
> Marketplace subscription hard-denied (L7). **2026-09-03** — AWS resources on that account torn down at
> the user's request (stack `DELETE_COMPLETE`, buckets/tables/role/log group removed). Re-verified blocked
> **twice more** (2026-09-03 workspace test — L10; 2026-09-12 fresh temp creds — L10 addendum):
> Academy/`voclabs` can never complete `aws-marketplace:Subscribe`, no matter how fresh the credentials —
> this is a permanent account-level restriction, not a transient/expiry issue. **Do not retest that
> account.**
>
> **Resolution (2026-09-09, L11):** moved `.env` to a **personal AWS account** (`187021010483`), dedicated
> IAM user `udacity-agentcore-dev` with `AdministratorAccess`. Both Claude models + Titan verified working.
> Full pre-flight resource sweep re-confirmed clean on **2026-09-12** (see L11 addendum) — model access,
> quotas, and every API surface the project touches (CloudFormation, DynamoDB/S3 via the stack,
> AgentCore Control, Guardrails, Knowledge Bases, Service Quotas) are reachable with this identity.
>
> Infra + tooling steps were already proven working before the account switch (uv env, stack deploy, seed,
> `config.py`, Titan embeddings) — none of that changes on the new account, it just needs re-running
> against a fresh stack (steps 0.4/0.6 below are **pending re-run**, since the old account's stack was
> deleted and this is a different account/region-scoped set of resources).

> **Environment facts (current):** Local Windows, **not** the Udacity cloud workspace. AWS account
> `187021010483` (personal), IAM user `udacity-agentcore-dev` (`AdministratorAccess`), **permanent**
> access key — no session token, no expiry to babysit (unlike the old Academy STS creds). CloudFormation
> stack **not yet (re-)deployed** on this account — that's the next action.
>
> **Operational gotchas discovered:**
> - `.env` lives at the **repo root** (`C:\WORKSPACES\AWS-UDACITY\P3-Multi-Agent_E-commerce_RAG\.env`), not `project/starter/`. `config.py`'s `load_dotenv()` still finds it (walks up). The **AWS CLI** does not — prefix CLI commands with `set -a && source ../../.env && set +a` (Git Bash) from `project/starter/`.
> - Windows console is cp1252 → any script printing Unicode (`✓`, box chars) crashes with `UnicodeEncodeError`. Run everything with **`PYTHONUTF8=1`** (e.g. `PYTHONUTF8=1 uv run python …`). Affects `seed_data.py`, `config.py`, and `tests/test_agent.py`.
> - `seed_data.py` has no `load_dotenv()` — it needs real env vars, so source `.env` before running it.
> - A permanent IAM key must have **no** `AWS_SESSION_TOKEN` line in `.env` at all (not even empty/`none`) — a leftover `AWS_SESSION_TOKEN=none` from the old temp-creds setup causes `InvalidClientTokenId` (L11).
> - ⚠️ **Bedrock quota ceiling: 10 requests/min per model** (Haiku 4.5 and Sonnet 4.5), the AWS default — a requested increase to 10,000 was `CASE_CLOSED` (not granted). See the **"Bedrock throttling" risk** in §12 and the Task 2 note under 2.C — this is a live constraint for the rest of development, not just a Phase 0 concern.

### Tasks
- [x] **0.1** Set up the environment with **uv** (from `project/starter/`):
      ```sh
      cd project/starter
      uv venv --python 3.12          # 3.12 matches the AgentCore runtime target
      uv pip install -r requirements.txt
      # activate for the rest of the project:
      #   PowerShell : .venv\Scripts\Activate.ps1
      #   Git Bash   : source .venv/Scripts/activate
      # (or skip activation and prefix each command with `uv run`)
      ```
      Optional: `uv init --bare` here to get a `pyproject.toml` + `uv.lock` for reproducibility (does not conflict with the graded files).
- [x] **0.2** Personal-account permanent creds in root `.env`; identity confirmed → `arn:aws:iam::187021010483:user/udacity-agentcore-dev`
- [x] **0.3** Bedrock model access — ✅ **RESOLVED** on the personal account (L11). Haiku 4.5, Sonnet 4.5, and Titan Embed v2 all invoke OK in `us-east-1`; first `Converse` call auto-subscribed via AWS Marketplace in the background (the `AdministratorAccess` identity has `aws-marketplace:Subscribe`, unlike the Academy `voclabs` role). Re-confirmed with a full pre-flight sweep 2026-09-12.
- [x] **0.4** Foundation infra — ✅ **deployed 2026-09-12** on the personal account (`187021010483`): `aws cloudformation deploy --template-file infrastructure/starter_stack.yaml --stack-name udacity-agentcore --capabilities CAPABILITY_NAMED_IAM --region us-east-1` → `CREATE_COMPLETE`. Then `PYTHONUTF8=1 uv run python infrastructure/seed_data.py` → 4 customers, 15 orders, 6 policy docs.
- [x] **0.5** `.env` keys present (creds + region + project filled; KB/runtime/guardrail keys still blank as expected)
- [x] **0.6** `PYTHONUTF8=1 uv run python config.py` — ✅ run 2026-09-12, all 5 CloudFormation-sourced rows populated against the new stack

### Milestone M0 — verification ✅ PASSED (2026-09-12, personal account)
- Bedrock: `us.anthropic.claude-{haiku,sonnet}-4-5` → **invoke OK** on `187021010483` / `udacity-agentcore-dev`. Titan Embed v2 ✅.
- Stack status → `CREATE_COMPLETE`; exports: OrdersTable (`udacity-agentcore-orders`), CustomersTable (`udacity-agentcore-customers`), WorkflowStateTable (`udacity-agentcore-workflow-state`), PolicyBucket (`udacity-agentcore-policy-docs-187021010483-3153d8d0`), VectorBucket (`udacity-agentcore-vectors-187021010483-3153d8d0`), AgentCoreRoleArn (`arn:aws:iam::187021010483:role/udacity-agentcore-agentcore-role`), AgentLogGroup (`/aws/bedrock/agentcore/udacity-agentcore`).
- `config.py` table: all 5 CloudFormation rows populated.
- DynamoDB scan COUNT: customers = 4, orders = 15. S3: 6 policy-doc objects across `policies/returns|shipping|warranty/`.
- ⚠️ **These are new, billable AWS resources on the personal account.** See **§16 — Active AWS resources / teardown checklist** before considering this project finished.

### Evidence collected → `docs/evidence/00-setup/`
- **E0.1** ✅ `identity-and-stack.txt` — re-collected 2026-09-12 against the new stack/account
- **E0.2** ✅ `config-py-output.txt` — re-collected 2026-09-12
- **E0.3** ✅ `bedrock-model-access.txt` — live invoke results for the 3 models, valid on the current (personal) account
- **E0.4** ✅ `s3-policy-docs.txt` — re-collected 2026-09-12
- **E0.5** ✅ `dynamodb-counts.txt` — re-collected 2026-09-12 (customers=4, orders=15)

---

## 5. Phase 1 / Task 2 — Multi-Agent Graph → **M1, M2**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task2`

> **Status: ✅ IMPLEMENTED & VERIFIED (2026-09-12)** — all 2.A–2.E builders complete in
> `src/agent_orchestrator.py`. `task2` scores **40/40**. Live end-to-end runs (see evidence below) confirm
> the full routing chain, DynamoDB optimistic locking, and the parallel multi-agent RAG path all work
> against real Bedrock + DynamoDB on the personal account.

### 2.A — `build_inventory_agent()` → returns one `Agent`
- [x] `BedrockModel(model_id=config.WORKER_MODEL_ID, region_name=config.AWS_REGION, temperature=0.1)`
- [x] System prompt: pure **data gatherer**, never makes eligibility/refund decisions
- [x] Tool `check_order_status(order_id)` → `Table.scan(FilterExpression=Attr('order_id').eq(...))` (no GSI on `order_id` alone — table PK is `customer_id`+`order_id` composite, so a scan+filter is required), returns status/date/price/return_eligible
- [x] Tool `get_customer_tier(customer_id)` → get item from `config.CUSTOMERS_TABLE`, return tier + profile
- [x] Tool `list_customer_orders(customer_id)` → query `config.ORDERS_TABLE` by `customer_id`, return list
- [x] Each tool has a docstring stating purpose / args / return
- [x] Ends with `return Agent(model=…, system_prompt=…, tools=[check_order_status, get_customer_tier, list_customer_orders])`
- **Rubric:** exactly **3** tools; model = Sonnet; temp 0.1 ✅ verified by `task2` 2.1/2.2

### 2.B — `build_refund_agent()` → returns one `Agent`
- [x] `BedrockModel(config.WORKER_MODEL_ID, temperature=0.1)`
- [x] System prompt: decision process = (1) always call `get_inventory_context` first, (2) apply window by tier — **Standard 30 days, Premium 60 days**, (3) decide eligible / not eligible
- [x] Tool `get_inventory_context(session_id)` → `_read_workflow_state(session_id)` and return its `inventory_agent` field (or `{}`)
- [x] Tool `initiate_refund(customer_id, order_id, reason)` → update the order row in `config.ORDERS_TABLE` (status → `return_requested`, `return_reference`), return `{return_reference, instructions}`
- **Rubric:** exactly **2** tools; 30/60-day windows encoded — ✅ verified live (see M2 evidence: correctly denied a Standard-tier return past 30 days)

### 2.C — `build_policy_agent()` → returns one `Agent` (multi-agent RAG) ⭐
- [x] Build **3 retriever sub-agents** inside the function:
      - `ReturnsPolicyRetrieverAgent` — tool calls `retrieve_from_knowledge_base(config.RETURNS_KB_ID, query)`
      - `ShippingPolicyRetrieverAgent` — `config.SHIPPING_KB_ID`
      - `WarrantyPolicyRetrieverAgent` — `config.WARRANTY_KB_ID`
      - each retriever: `BedrockModel(config.WORKER_MODEL_ID, temperature=0.0)`, exactly 1 tool
- [x] Implement `_run_retriever(domain, agent, query)` → invoke sub-agent, return `(domain, result_text)`
- [x] Implement `search_all_policies(query)`:
      - build `retrievers = {'Returns': …, 'Shipping': …, 'Warranty': …}`
      - `trace.kb_start({...})` is already in starter — kept
      - `with ThreadPoolExecutor(max_workers=3) as ex:` submit all 3, gather with `as_completed()`
      - after join: `trace.kb_done(len(retrievers))` then loop `trace.kb_result(domain, results.get(domain, '[No results]'))` for Returns/Shipping/Warranty
      - return combined text of all 3 domains
- [x] Coordinator: `BedrockModel(config.WORKER_MODEL_ID, temperature=0.2)`, system prompt = "always call `search_all_policies` first, then synthesize a grounded answer", tools = `[search_all_policies]`
- **Rubric:** coordinator has exactly **1** tool (`search_all_policies`); `ThreadPoolExecutor(max_workers=3)` + `as_completed()`; retriever temp 0.0, coordinator temp 0.2 — ✅ verified live: all 3 retrievers fired concurrently, no crash even with all 3 KB IDs still blank (graceful "no results found" per retriever, matching `retrieve_from_knowledge_base`'s documented empty-KB-ID behavior) — real passages need Task 5's KBs.
- **⚠️ Quota note:** these 3 retriever calls fire **concurrently**, and the Bedrock cross-region quota is
  only **10 requests/min per model** on this account (see §4/§12). A single `search_all_policies` call
  already burns 3 of that 10 in one shot. Test this function in isolation with single, spaced-out calls
  first — don't hammer it in a tight loop while debugging, and expect to see `ThrottlingException` if you
  run `test_agent.py all` immediately after several manual smoke tests. (No throttling observed during
  the 2026-09-12 verification runs.)

### 2.D — `build_communication_agent()` → returns one `Agent`
- [x] `BedrockModel(config.WORKER_MODEL_ID, temperature=0.3)`
- [x] System prompt: warm, professional, empathetic; include all relevant findings from prior agents
- [x] Tool `get_full_workflow_context(session_id)` → `_read_workflow_state(session_id)` full record
- **Rubric:** exactly **1** tool; temp 0.3

### 2.E — `build_orchestrator_agent(inventory, refund, policy, communication)` → returns one `Agent`
- [x] `BedrockModel(config.ORCHESTRATOR_MODEL_ID, temperature=0.0)`
- [x] `initialize_session(session_id, customer_id)` → `_create_workflow_state(...)`; return confirmation
- [x] `route_to_inventory_agent(session_id, customer_id, request)` → read state → invoke `inventory_agent(...)` → `_update_workflow_state(session_id, {'inventory_agent': result}, expected_version=state['version'])`
- [x] `route_to_policy_agent(session_id, request)` → same read/invoke/update pattern with `{'policy_agent': result}`
- [x] `route_to_refund_agent(session_id, customer_id, request)` → `{'refund_agent': result}`
- [x] `route_to_communication_agent(session_id, customer_id, original_request)` → `{'communication_agent': result}`
- [x] System prompt enforces **all 6 routing rules verbatim**:
      1. Every request → `initialize_session` **first**
      2. Order status / return / refund → inventory **then** refund
      3. Policy-meaning questions (return windows, shipping rates, warranty terms) → policy agent
      4. Account questions ("my tier?", "am I premium?") → inventory agent, **never** policy agent
      5. Math / calculation → answer directly, no routing
      6. Every request → `route_to_communication_agent` **last**, always
- [x] CRITICAL: orchestrator **never** writes the final customer response itself
- **Rubric:** exactly **5** tools; Haiku; temp 0.0 ✅ verified — live run confirmed rule 5 (math answered directly, no routing) and rule 2/6 (inventory → refund → communication, always ending on communication)

### Milestone M1 — verification ✅ PASSED
`python tests/test_agent.py task2` → checks 2.1, 2.2, 2.3, 2.4, 2.7 pass (agents instantiate, tool counts right, model split right). Score ≥ 30/40. → actual: 40/40 (M1 subsumed by M2).

### Milestone M2 — verification ✅ PASSED (2026-09-12)
- `python tests/test_agent.py task2` → **40/40** ✅
- Full chain verified live against a real seeded order (`ORD-91987`, CUST-002/Standard): trace shows
  `Orchestrator → Inventory → Refund → Communication`, WorkflowState version climbed 0→1→2→3, RefundAgent
  correctly applied the 30-day Standard window and denied the return (order was ~76 days old) — a
  correct decision, not a bug. (`demo.py`'s hardcoded `ORD-27176` doesn't exist in this run's randomly
  seeded data, so that exact order number won't reproduce — the routing/logic is proven either way: the
  no-such-order case was also verified live, correctly skipping straight to Inventory → Communication
  without invoking Refund.)
- `python src/agent_orchestrator.py test` → all 3 canonical scenarios ran clean, no exceptions, no
  throttling: (1) return request → Orchestrator → Inventory → Communication (order not found, gracefully
  handled), (2) policy question → Orchestrator → Policy (3 parallel retrievers, graceful empty-KB
  handling) → Communication, (3) math question → answered directly by the orchestrator, **no sub-agent
  routing** (rule 5 confirmed).
- Policy scenario's *content* is necessarily generic until Task 5's KBs exist — parallel-dispatch
  mechanics are fully proven now.

### Evidence collected → `docs/evidence/02-agents/`
- **E2.1** ✅ `E2.1-task2-score.txt` — `Score: 40/40 pts (100%)`
- **E2.2** ✅ `E2.2-full-refund-chain-trace.txt` — full Orchestrator → Inventory → Refund → Communication trace against real order `ORD-91987`
- **E2.3** ✅ `E2.3-three-scenarios.txt` — `agent_orchestrator.py test`, all 3 canonical scenarios
- **E2.4** ✅ `E2.4-task2-implementation.diff` — `git diff main dev/task-01 -- .../agent_orchestrator.py`
- **E2.5** ✅ `E2.5-workflow-state-record.txt` — `aws dynamodb get-item` on the WorkflowState record for the run in E2.2: `version=3`, all four agent columns populated (text capture in lieu of a console screenshot)

---

## 6. Phase 3 / Task 5 — Bedrock Knowledge Bases → **M3**

> Do this **before** Task 3 deploy so the runtime env vars carry real KB IDs, and before testing the policy path.
**Location:** AWS Console (no code) — done here via **CLI/boto3** instead (`bedrock-agent` + `s3vectors`
APIs), which creates the identical AWS resources the console wizard would. **Test:** `python tests/test_agent.py task5`

> **Status: ✅ DONE (2026-09-12).** Console-vs-CLI note: the CFN-created `VectorStoreBucket` is a plain
> `AWS::S3::Bucket`, which is **not** the same resource type as an S3 Vectors "vector bucket" (a distinct
> `s3vectors:` ARN namespace, its own service). Created a real S3 Vectors vector bucket +
> 3 indexes via `aws s3vectors create-vector-bucket` / `create-index` instead of reusing that CFN bucket
> — functionally equivalent to what the console's "S3 Vectors" KB wizard provisions under the hood.

### Tasks (repeat 3×) — done via CLI, see `lessons_learned.md` L14 for full command sequence
- [x] **5.1** `novamart-returns-policy-kb` → KB ID `HAEAIOJU2M`
      - Data source: S3, bucket = CloudFormation `PolicyBucket`, prefix `policies/returns/`
      - Embeddings: `amazon.titan-embed-text-v2:0`
      - Vector store: **S3 Vectors**, dedicated vector bucket `udacity-agentcore-vectors-187021010483`, index `returns-index` (dimension 1024, float32, cosine)
- [x] **5.2** `novamart-shipping-policy-kb` — prefix `policies/shipping/` → KB ID `HNTEB2KQRZ`, index `shipping-index`
- [x] **5.3** `novamart-warranty-policy-kb` — prefix `policies/warranty/` → KB ID `ATZZEIJG1P`, index `warranty-index`
- [x] **5.4** `start-ingestion-job` on each data source — all 3 reached `COMPLETE` (2 documents indexed each, 0 failed)
- [x] **5.5** KB IDs copied into `.env`: `RETURNS_KB_ID=HAEAIOJU2M`, `SHIPPING_KB_ID=HNTEB2KQRZ`, `WARRANTY_KB_ID=ATZZEIJG1P`

### Milestone M3 — verification ✅ PASSED (2026-09-12)
- `python tests/test_agent.py task5` → **25/25** (all 3 IDs set, all 3 KBs `ACTIVE`)
- Live retrieval smoke test via `build_policy_agent()` with query "What is the return policy for premium
  customers?" → all 3 retrievers returned real, grounded passages (60-day Premium return window, free
  expedited shipping, 3-year electronics warranty, $500/20-order tier thresholds) — parallel dispatch and
  synthesis both confirmed working against live KBs, not just the earlier empty-KB graceful-degradation path.

### Evidence collected → `docs/evidence/05-kb/`
- **E3.1** ✅ `E3.1-kb-list-status.txt` — all 3 KBs `ACTIVE`, correct embedding model + S3_VECTORS storage + index name (CLI capture in lieu of console screenshot)
- **E3.2** ✅ `E3.2-sync-history.txt` — all 3 ingestion jobs `COMPLETE`, 2 docs indexed / 0 failed each
- **E3.3** ✅ `E3.3-task5-score.txt` — `25/25`
- **E3.4** ✅ `E3.4-parallel-retrieval-real-content.txt` — `search_all_policies` smoke test, real grounded passages from Returns + Shipping + Warranty (satisfies rubric `test_5_parallel_retrieval` intent)
- **E3.5** ✅ `E3.5-env-kb-ids.txt` — `.env` KB ID lines

---

## 7. Phase 2 / Task 3 — Guardrail + AgentCore Runtime → **M4**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task3`

> **Status: ✅ DONE (2026-09-12).** `task3` = **20/20**. Guardrail ID `mnsou98agg5p` (version `1`), Runtime
> ARN `arn:aws:bedrock-agentcore:us-east-1:187021010483:runtime/udacity_agentcore_runtime-fh9FZwA4FY`.

### `create_guardrail()` → `(guardrail_id, guardrail_version)`
- [x] `bedrock` client `create_guardrail(name=config.GUARDRAIL_NAME, …)` with:
      - **contentPolicyConfig**: SEXUAL, VIOLENCE, HATE → `HIGH` (input+output); INSULTS, MISCONDUCT → `MEDIUM`
      - **sensitiveInformationPolicyConfig**: `CREDIT_DEBIT_CARD_NUMBER`, `US_SOCIAL_SECURITY_NUMBER` → `BLOCK`; `EMAIL`, `PHONE` → `ANONYMIZE`
      - **topicPolicyConfig**: DENY topics — competitor products, pricing negotiations, legal threats (use `config.GUARDRAIL_BLOCKED_TOPICS`)
      - **wordPolicyConfig**: managed word list `PROFANITY`
      - `blockedInputMessaging` + `blockedOutputsMessaging` (friendly text)
- [x] `create_guardrail_version(guardrailIdentifier=id)` — promote DRAFT → numbered version
- [x] return `(id, version)`
- (starter already handles the "guardrail already exists" short-circuit — verified idempotent on a second `deploy` run)

### `deploy_to_agentcore_runtime(orchestrator_agent, guardrail_id, guardrail_version)` → runtime ARN
- [x] `agentcore_control.create_agent_runtime(...)`:
      - `agentRuntimeName` = `runtime_name` (starter-computed), `description`, `roleArn=config.AGENTCORE_ROLE_ARN`
      - `networkConfiguration` → **PUBLIC**
      - `protocolConfiguration` → **MCP**
      - `agentRuntimeArtifact` → the S3 zip already uploaded by starter (`codeConfiguration.code.s3={bucket, prefix}`), runtime `PYTHON_3_12`, `entryPoint=['main.py']`
      - `environmentVariables`: `AWS_REGION`, `PROJECT_NAME`, `RETURNS_KB_ID`, `SHIPPING_KB_ID`, `WARRANTY_KB_ID`, `AGENT_LOG_GROUP`
      - guardrail is injected by the pre-written `before-call` hook — don't pass it explicitly
- [x] return `response.get('agentRuntimeArn', response.get('arn',''))`

### Deploy + record
- [x] `python src/agent_orchestrator.py deploy` (runs the 6-step pipeline) — ran twice, second run confirmed idempotent (both guardrail and runtime reused, not recreated)
- [x] Printed values copied into `.env`: `AGENTCORE_RUNTIME_ARN`, `GUARDRAIL_ID=mnsou98agg5p`, `GUARDRAIL_VERSION=1`

### Milestone M4 — verification ✅ PASSED (2026-09-12)
- Deploy command completed through all 6 steps without fatal error (Step 6/6 Gateway also deployed — pre-written bonus feature, not part of the graded rubric, but a real resource — see §16 teardown update)
- `python tests/test_agent.py task3` → **20/20** — guardrail exists with content + PII + topic policies; runtime ARN set
- Live-verified via `get-guardrail`: exact policy match to the rubric (SEXUAL/VIOLENCE/HATE=HIGH, INSULTS/MISCONDUCT=MEDIUM, PII BLOCK/ANONYMIZE split, 3 denied topics, PROFANITY word list, version `1` ≠ DRAFT)
- Live-verified via `get-agent-runtime`: `networkMode=PUBLIC`, `serverProtocol=MCP`, all 6 env vars present including the real KB IDs from Task 5

### Evidence collected → `docs/evidence/03-guardrail-runtime/`
- **E4.1** ✅ `E4.1-deploy-output.txt` — full `deploy` output, all 6 steps (second, idempotent run — both guardrail and runtime correctly reused rather than recreated)
- **E4.2** ✅ `E4.2-guardrail-detail.txt` — `aws bedrock get-guardrail` output: content filter strengths, PII entities, denied topics, profanity, version `1` (CLI capture in lieu of console screenshot)
- **E4.3** ✅ `E4.3-runtime-detail.txt` — `aws bedrock-agentcore-control get-agent-runtime` output: `PUBLIC`/`MCP`, all env vars
- **E4.4** ✅ `E4.4-task3-score.txt` — `20/20`
- **E4.5** ✅ `E4.5-env-runtime-guardrail.txt` — `.env` excerpt
- **E4.6 (stretch, rubric "stand out")** adversarial probes vs the guardrail — prompt injection, competitor mention, legal threat — with blocked-response screenshots

---

## 8. Phase 2 / Task 4 — AgentCore Memory → **M5**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task4`

> **Status: ✅ DONE (2026-09-12).** Real memory resource `udacity_agentcore_memory-yX3G4HDqFe`, `ACTIVE`,
> `SUMMARIZATION` strategy `session_summary` active, `eventExpiryDuration=7`.
>
> **Test-harness quirk found:** `python tests/test_agent.py task4` run **alone** fails with
> `'BedrockAgentCore' object has no attribute 'get_agent_runtime'`. Cause: only `TestTask2.setUp` does
> `import agent_orchestrator as ao`, which is what triggers the pre-written compat patch
> (`_register_agentcore_compat_methods()`) that adds `get_agent_runtime` to the raw `bedrock-agentcore`
> boto3 client. `TestTask4.setUp` never imports `agent_orchestrator` at all — it only works when task2's
> tests already ran earlier in the **same process** (i.e. via `python tests/test_agent.py all`, which is
> also the actual grading invocation). Not a bug in the implementation — just don't trust `task4` (or
> likely `task3`/`task6`, same mechanism) run in isolation; always confirm via `all`.

### `configure_memory(runtime_arn)` → `memoryArn`
- [x] `agentcore_control.create_memory(...)`:
      - `name` = `config.MEMORY_NAMESPACE` (hyphens→underscores, starter does this), `description`
      - `eventExpiryDuration=7` (7-day retention)
      - `memoryStrategies=[{ 'summaryMemoryStrategy': { 'name': 'session_summary', 'namespaces': ['/summaries/{sessionId}'] } }]`
      - `memoryExecutionRoleArn=config.AGENTCORE_ROLE_ARN` (optional per the API, included so the summarization strategy has permissions to invoke Bedrock)
      - `clientToken=memory_name` for idempotency
- [x] return `memoryArn`
- (starter short-circuits if a memory with that prefix already exists — verified idempotent on a second `deploy` run)

### Milestone M5 — verification ✅ PASSED (2026-09-12)
- `python tests/test_agent.py all` → Task 4 section **15/15** (see quirk note above for why `task4` alone fails)
- Live-verified via `get-memory`: `status=ACTIVE`, strategy `session_summary` type `SUMMARIZATION` status `ACTIVE`, `eventExpiryDuration=7`
- Took ~90s from `CREATING` to `ACTIVE` after `create_memory()` returned — real backend provisioning delay, not an error

### Evidence collected → `docs/evidence/04-memory/`
- **E5.1** ✅ `E5.1-task4-score-within-all.txt` — Task 4 section = `15/15` (from a full `test_agent.py all` run)
- **E5.2** ✅ `E5.2-deploy-step4-memory.txt` — deploy pipeline "Step 4/6: Configuring Memory…" line + memory ARN (idempotent re-run, correctly reused)
- **E5.3** ✅ `E5.3-memory-resource-detail.txt` — `aws bedrock-agentcore-control get-memory` full detail: `SUMMARIZATION` strategy + 7-day expiry (CLI capture in lieu of console screenshot)

---

## 9. Phase 4 / Task 6 — Observability → **M6, M7**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task6`

> **Status: ⚠️ CODE DONE (2026-09-12), score 0/20 in this environment — genuine SDK/API gap, not a
> bug.** `put_agent_runtime_logging_configuration` / `get_agent_runtime_logging_configuration` do not
> exist on `bedrock-agentcore-control` in **either** the project's boto3 (1.43.87) **or** AWS CLI v2
> (2.36.22)'s bundled botocore — confirmed both independently. This is exactly the "SDK version mismatch"
> scenario the starter's own TODO comments anticipated and instructed a graceful try/except fallback for.
> The implementation is correct and matches the spec; `test_agent.py`'s own task6 checks call the same
> missing method directly (no fallback in the test), so they score 0/20 regardless of what our code does.
> Not something fixable from `agent_orchestrator.py` — would need a newer botocore than currently exists
> publicly, or a different (undocumented) API shape. See `lessons_learned.md` L17.

### `configure_observability(runtime_arn)` → `None`
- [x] `runtime_id = runtime_arn.split('/')[-1]`
- [x] `try:` `agentcore_control.put_agent_runtime_logging_configuration(agentRuntimeId=runtime_id, loggingConfiguration={...})` with:
      - `cloudWatchConfig`: `logGroupName=config.AGENT_LOG_GROUP`, `logLevel='INFO'`, `enabled=True`
      - `xRayConfig`: `enabled=True`, `samplingRate=1.0`
      - on success: print log group + sampling rate
- [x] `except Exception as e:` print `"[Note] Logging config skipped (SDK version mismatch): {e}"` — this is the path that actually executes today

### Milestone M6 — verification
`python tests/test_agent.py task6` → **0/20 in this environment** (see status note above) — code itself is correct/complete per spec

### Evidence collected → `docs/evidence/06-observability/`
- **E6.1** `E6.1-task6-result.txt` — shows the exact `AttributeError` proving the API gap, not a code defect
- **E6.2** `E6.2-deploy-step5-observability.txt` — deploy pipeline's graceful `[Note] Logging config skipped (SDK version mismatch)` message, exactly as the TODO instructed

### Milestone M7 — end-to-end proof
- [ ] `python src/agent_orchestrator.py deploy` (final, clean run with all functions implemented)
- [ ] `python src/agent_orchestrator.py test` — verify routing:

  | Scenario | Expected routing |
  |---|---|
  | "I want to return my order ORD-27176" | Orchestrator → Inventory → Refund → Communication |
  | "What is the return policy for premium customers?" | Orchestrator → Policy (3 parallel KB retrievers) → Communication |
  | "How much are 5 items at $29.99 with 10% off?" | Orchestrator answers directly → Communication |

- [ ] Wait 30–60 s, open **AWS Console → X-Ray → Service map**
- [ ] Capture the service map showing Orchestrator connected to ≥ 1 worker
- [ ] `python tests/test_agent.py all` → **120/120**

### Evidence to collect
- **E6.1** Terminal capture: `python tests/test_agent.py task6` = `20/20`
- **E6.2** Console screenshot: AgentCore runtime logging config (CloudWatch INFO enabled, X-Ray 1.0 enabled) — or CloudWatch log group `/aws/bedrock/agentcore/udacity-agentcore` with log streams
- **E7.1** Terminal capture: final `python src/agent_orchestrator.py deploy` (all 6 steps OK)
- **E7.2** Terminal capture: `python src/agent_orchestrator.py test` — 3 scenarios, routing visible in trace
- **E7.3** ⭐ **REQUIRED DELIVERABLE (D4)** — screenshot of **X-Ray Service Map** with the connected Orchestrator → worker trace graph
- **E7.4** Terminal capture: `python tests/test_agent.py all` = `120/120`
- **E7.5** Final `git diff` / copy of completed `src/agent_orchestrator.py` (D1)
- **E7.6** Final `.env` with all 6 populated values (D3) — redact secret access key / session token

---

## 10. Evidence register (master checklist)

| ID | Artifact | Format | Maps to | Collected |
|---|---|---|---|---|
| E0.1 | caller identity + stack `CREATE_COMPLETE` | terminal | M0 | ☐ |
| E0.2 | `python config.py` table | terminal | M0 | ☐ |
| E0.3 | Bedrock model access (3 models) | screenshot | M0 | ☐ |
| E0.4 | S3 `policies/` tree | screenshot | M0 | ☐ |
| E0.5 | DynamoDB customers items | screenshot | M0 | ☐ |
| E2.1 | `task2` = 40/40 | terminal | M2 / D1 | ☐ |
| E2.2 | `demo.py` full trace | terminal | M2 | ☐ |
| E2.3 | `agent_orchestrator.py test` ×3 | terminal | M2 | ☐ |
| E2.4 | Task 2 `git diff` | diff | D1 | ☐ |
| E2.5 | WorkflowState record version > 0 | screenshot | M2 | ☐ |
| E3.1 | 3 KBs `Available` | screenshot | M3 / D2 | ☐ |
| E3.2 | 3× sync history `Completed` | screenshot | M3 / D2 | ☐ |
| E3.3 | `task5` = 25/25 | terminal | M3 | ☐ |
| E3.4 | parallel retrieval, 3 domains non-empty | terminal | M3 | ☐ |
| E3.5 | `.env` KB IDs | text | D3 | ☐ |
| E4.1 | `deploy` full output | terminal | M4 | ☐ |
| E4.2 | Guardrail detail (versioned) | screenshot | M4 / D1 | ☐ |
| E4.3 | AgentCore runtime (PUBLIC/MCP) | screenshot | M4 | ☐ |
| E4.4 | `task3` = 20/20 | terminal | M4 | ☐ |
| E4.5 | `.env` runtime ARN + guardrail | text | D3 | ☐ |
| E4.6 | adversarial guardrail probes | screenshots | stretch | ☐ |
| E5.1 | `task4` = 15/15 | terminal | M5 | ☐ |
| E5.2 | deploy Step 4/6 + memory ARN | terminal | M5 | ☐ |
| E5.3 | Memory resource `SESSION_SUMMARY` | screenshot | M5 | ☐ |
| E5.4 | `configure_memory()` diff | diff | D1 | ☐ |
| E6.1 | `task6` = 20/20 | terminal | M6 | ☐ |
| E6.2 | logging config / log group | screenshot | M6 | ☐ |
| E7.1 | final `deploy` | terminal | M7 | ☐ |
| E7.2 | final `test` routing ×3 | terminal | M7 | ☐ |
| **E7.3** | **X-Ray Service Map** | **screenshot** | **D4** | ☐ |
| E7.4 | `all` = 120/120 | terminal | M7 | ☐ |
| E7.5 | completed `agent_orchestrator.py` | file | D1 | ☐ |
| E7.6 | final `.env` (redacted) | text | D3 | ☐ |

> Suggested storage: `docs/evidence/` with subfolders `00-setup/ 02-agents/ 05-kb/ 03-guardrail-runtime/ 04-memory/ 06-observability/ 07-e2e/`. Name files `E<id>-<slug>.png|txt`.

---

## 11. Critical execution order

```
M0 ──► M1 ──► M2 ──► M3 ──► M4 ──► M5
                             │        │
                             └──► M6 ─┴──► M7
```

Recommended sitting order: **M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7.**
Rationale: KBs (M3) must exist before deploy (M4) so the runtime env vars carry real IDs; Memory (M5) and Observability (M6) both attach to the runtime from M4; the X-Ray map (M7) needs M6 active plus a live invocation.

---

## 12. Risks & mitigations

| Risk | Signal | Mitigation |
|---|---|---|
| ~~Temp creds expire mid-task~~ — N/A since L11 | ~~`ExpiredToken` / `InvalidClientTokenId`~~ | Using permanent personal-account IAM keys now (no expiry). If `InvalidClientTokenId` reappears, check `.env` doesn't have a stray `AWS_SESSION_TOKEN` line (must be absent for permanent keys — L11). |
| ~~Bedrock model not enabled~~ — ✅ resolved (L11) | ~~`AccessDeniedException` on invoke~~ | Resolved by moving to the personal account (`187021010483`, `udacity-agentcore-dev`, `AdministratorAccess`). Confirmed working 2026-09-09 and re-swept 2026-09-12. |
| **Bedrock request-rate throttling** — live risk, watch for this while building | `ThrottlingException` on `Converse`/`InvokeModel`, especially from the Task 2.C parallel KB retrievers (3 concurrent calls) or rapid `test_agent.py` re-runs | Cross-region quota is only **10 requests/min per model**; a requested increase to 10,000 was denied (`CASE_CLOSED`). Space out manual test invocations; let SDK-level retry/backoff absorb transient hits; if it blocks real progress, resubmit a Service Quotas increase request for both Haiku 4.5 and Sonnet 4.5 (aim for ~50–100 RPM) — see `lessons_learned.md` L11. |
| KB sync returns 0 chunks | `task5` ACTIVE but retrieval empty | confirm prefix has a trailing slash, re-run Sync, check bucket is `PolicyBucket` not `VectorStoreBucket` |
| `ThreadPoolExecutor` stdout garbled | interleaved trace lines | the starter's `_TraceWriter._suppress_parallel` handles it — return results as values, print via `trace.kb_result()` after join (don't print inside `_run_retriever`) |
| AgentCore API shape differs by SDK version | `ParamValidationError` on `create_agent_runtime` / `create_memory` | check installed `boto3` model with `python -c "import boto3;print(boto3.client('bedrock-agentcore-control').meta.service_model.operation_names)"`; adjust key names; keep `configure_observability` in try/except as instructed |
| `WorkflowState` version conflicts | `RuntimeError: … Too many concurrent writes` | each routing tool must `_read_workflow_state` immediately before `_update_workflow_state` and pass that fresh `version` |
| Editing a locked file | test suite behaves oddly | only touch `src/agent_orchestrator.py`; `git diff --stat` should list exactly that one file |

---

## 13. Optional — "stand out" (rubric bonus, not graded points)

- [ ] **S1** Adversarial guardrail validation report (E4.6) — injection, competitor, legal-threat probes with screenshots
- [ ] **S2** DynamoDB `agent-sessions` table + Strands `DynamoDbSessionStorage` in the Orchestrator (local session memory alongside AgentCore Memory)
- [ ] **S3** CloudWatch dashboard: invocations over time, avg latency per agent, guardrail trigger frequency
- [ ] **S4** Cognito auth + minimal web frontend calling the AgentCore Runtime endpoint

---

## 14. Definition of done

- [ ] `python tests/test_agent.py all` → **120/120**
- [ ] D1–D4 collected in `docs/evidence/`
- [ ] `.env` has all 6 task-populated values
- [ ] `git diff` touches only `src/agent_orchestrator.py`
- [ ] X-Ray Service Map screenshot shows Orchestrator → ≥1 worker
- [ ] **Industry Best Practices pass** (rubric category, not covered by `test_agent.py`): every tool function has a docstring (purpose/params/return); every `build_*_agent()` returns exactly one `Agent`; names are `snake_case`/descriptive; no hardcoded model-ID strings anywhere — only `config.ORCHESTRATOR_MODEL_ID` / `config.WORKER_MODEL_ID`
- [ ] Submission package assembled per Udacity classroom instructions

---

## 15. Starter-kit upstream parity

Verified **2026-09-12** against `github.com/udacity/cd14764-aws-agentic-c3-classroom` (`main`, no local git remote configured — checked via `gh api` + direct file diff): every starter file (`src/agent_orchestrator.py` incl. all TODOs, `agent_utils.py`, `bedrock_kb_retrieval.py`, `demo.py`, `config.py`, `tests/test_agent.py`, `infrastructure/*`, `requirements.txt`, `.env.example`, `README.md`) is **byte-identical** to upstream. Latest upstream commit touching `project/starter` is `4eeecb3` (2026-05-29) — already present locally. No newer scaffolding, fixes, or TODO changes exist upstream that this working copy is missing. See `lessons_learned.md` **L12** for the full check.

---

## 16. Active AWS resources — teardown checklist

⚠️ **As of 2026-09-12, real billable AWS resources exist on the personal account (`187021010483`).**
Pay-per-request DynamoDB + S3 are cheap at this scale, but nothing here is free-tier-guaranteed —
tear this down when the project is done or between long gaps in work. Tracked here per explicit request
so nothing is left running by accident.

### Currently created (Task 2 + Task 5 checkpoint)
| Resource | Name / ARN | Created by |
|---|---|---|
| CloudFormation stack | `udacity-agentcore` (us-east-1) | `aws cloudformation deploy`, 2026-09-12 |
| DynamoDB table | `udacity-agentcore-orders` | stack |
| DynamoDB table | `udacity-agentcore-customers` | stack |
| DynamoDB table | `udacity-agentcore-workflow-state` | stack |
| S3 bucket | `udacity-agentcore-policy-docs-187021010483-3153d8d0` (versioning **enabled**; holds 6 seeded policy docs) | stack |
| S3 bucket | `udacity-agentcore-vectors-187021010483-3153d8d0` (versioning **enabled**; unused — see note below) | stack |
| IAM role | `udacity-agentcore-agentcore-role` | stack |
| CloudWatch log group | `/aws/bedrock/agentcore/udacity-agentcore` | stack |
| **S3 Vectors vector bucket** | `udacity-agentcore-vectors-187021010483` (`arn:aws:s3vectors:us-east-1:187021010483:bucket/...`) — a **different resource type** from the plain S3 bucket above, own service (`s3vectors`), not deleted by the CFN stack | `aws s3vectors create-vector-bucket`, 2026-09-12 |
| S3 Vectors index ×3 | `returns-index`, `shipping-index`, `warranty-index` (inside the vector bucket above; 1024-dim, float32, cosine) | `aws s3vectors create-index`, 2026-09-12 |
| Bedrock Knowledge Base | `novamart-returns-policy-kb` (`HAEAIOJU2M`) | `aws bedrock-agent create-knowledge-base`, 2026-09-12 |
| Bedrock Knowledge Base | `novamart-shipping-policy-kb` (`HNTEB2KQRZ`) | same |
| Bedrock Knowledge Base | `novamart-warranty-policy-kb` (`ATZZEIJG1P`) | same |
| KB data source ×3 | `novamart-{returns,shipping,warranty}-s3-source` (one per KB above, pointing at the matching `policies/*/` prefix) | `aws bedrock-agent create-data-source`, 2026-09-12 |
| Bedrock Guardrail | `udacity-agentcore-guardrail` (id `mnsou98agg5p`, version `1`) | `create_guardrail()` via `deploy`, 2026-09-12 |
| AgentCore Runtime | `udacity_agentcore_runtime` (`arn:aws:bedrock-agentcore:us-east-1:187021010483:runtime/udacity_agentcore_runtime-fh9FZwA4FY`) | `deploy_to_agentcore_runtime()` via `deploy`, 2026-09-12 |
| Runtime artifact | `s3://udacity-agentcore-policy-docs-187021010483-3153d8d0/agentcore-artifacts/udacity_agentcore_runtime/deployment.zip` (small placeholder zip; removed when the policy-docs bucket is emptied in teardown step 1) | same |
| **AgentCore Gateway** | `novamart-support-3153d8d0` (id `novamart-support-3153d8d0-aypt2f6im2`) — pre-written Step 6/6 of `deploy_all()`, not part of the graded rubric, but a **real resource** | `deploy_agentcore_gateway()` via `deploy`, 2026-09-12 (its 3 Lambda targets failed to register — no Lambda functions deployed — so the gateway itself exists but has no working targets) |
| AgentCore Memory | `udacity_agentcore_memory-yX3G4HDqFe` (`SUMMARIZATION` strategy `session_summary`, 7-day expiry) | `configure_memory()` via `deploy`, 2026-09-12 |

> Note: the CFN template's `VectorStoreBucket` (plain S3) is **not** used by these KBs — S3 Vectors
> "vector buckets" are a separate resource type/ARN namespace from regular S3 buckets, so a real
> `s3vectors:create-vector-bucket` call was required. `VectorStoreBucket` is currently unused; harmless
> to leave (removed automatically when the CFN stack is deleted) but not part of the KB teardown below.

### Not yet created
- Task 6 (Observability) doesn't create a new resource — it configures logging/tracing on the existing runtime.

### Teardown procedure (run when the project is fully done, or to pause and stop billing)
CloudFormation **will not delete non-empty S3 buckets**, and both buckets have versioning enabled, so
`aws s3 rm --recursive` alone is not enough — old versions must be purged too, or stack deletion fails.

```sh
# 1. Empty both versioned S3 buckets completely (current + all noncurrent versions + delete markers)
for BUCKET in udacity-agentcore-policy-docs-187021010483-3153d8d0 \
              udacity-agentcore-vectors-187021010483-3153d8d0; do
  aws s3api delete-objects --bucket "$BUCKET" --delete "$(
    aws s3api list-object-versions --bucket "$BUCKET" \
      --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json)" 2>/dev/null
  aws s3api delete-objects --bucket "$BUCKET" --delete "$(
    aws s3api list-object-versions --bucket "$BUCKET" \
      --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' --output json)" 2>/dev/null
done

# 2. Delete the 3 Bedrock Knowledge Bases (also deletes their data sources) — NOT part of the CFN stack
for KB in HAEAIOJU2M HNTEB2KQRZ ATZZEIJG1P; do
  aws bedrock-agent delete-knowledge-base --knowledge-base-id "$KB" --region us-east-1
done

# 3. Delete the S3 Vectors indexes, then the vector bucket itself — also NOT part of the CFN stack
#    (this is a separate `s3vectors:` resource type from the plain S3 VectorStoreBucket)
VB=udacity-agentcore-vectors-187021010483
for IDX in returns-index shipping-index warranty-index; do
  aws s3vectors delete-index --vector-bucket-name "$VB" --index-name "$IDX" --region us-east-1
done
aws s3vectors delete-vector-bucket --vector-bucket-name "$VB" --region us-east-1

# 4. Delete the AgentCore Gateway, Runtime, Memory resource (if Task 4 lands), and Guardrail —
#    NONE of these are part of the CFN stack and won't be removed by it.
aws bedrock-agentcore-control delete-gateway --gateway-identifier novamart-support-3153d8d0-aypt2f6im2 --region us-east-1
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id udacity_agentcore_runtime-fh9FZwA4FY --region us-east-1
aws bedrock-agentcore-control delete-memory --memory-id udacity_agentcore_memory-yX3G4HDqFe --region us-east-1
aws bedrock delete-guardrail --guardrail-identifier mnsou98agg5p --region us-east-1

# 5. Delete the CloudFormation stack (removes DynamoDB tables, both plain S3 buckets, IAM role, log group)
aws cloudformation delete-stack --stack-name udacity-agentcore --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name udacity-agentcore --region us-east-1

# 6. Verify nothing is left
aws cloudformation describe-stacks --stack-name udacity-agentcore --region us-east-1   # should error "does not exist"
aws s3 ls | grep udacity-agentcore                                                     # should be empty
aws s3vectors list-vector-buckets --region us-east-1                                   # should not list udacity-agentcore-vectors-187021010483
aws bedrock-agent list-knowledge-bases --region us-east-1                              # should not list the 3 novamart-*-policy-kb entries
```

Keep the `.env` KB IDs / runtime ARN / guardrail ID around even after teardown (for the record of what
was built), but they'll no longer resolve to live resources once steps 2–5 run.

---

## 17. Git workflow note (2026-09-12)

This session's edits landed via **automatic commits** on a branch called `dev/task-01` (auto-created,
switched to automatically — not a manual `git checkout` in this conversation), not on `main`. Two
auto-generated commits appeared during Task 2 work (one for the docs update, one for the
`agent_orchestrator.py` implementation); the second commit's message underdescribes the actual diff
(mentions only a Returns retriever / `answer_policy_question`), but the actual committed content was
verified to match the full Task 2 implementation (all 3 retrievers, `search_all_policies`, all 5
orchestrator tools — confirmed via `git show a62602d:...` and TODO-count diffing). `main` remains the
untouched, pristine starter (34 TODOs). No commits were made via an explicit `git commit` call in this
conversation — whatever is auto-committing (harness checkpoint feature, most likely) did so on its own.
Nothing appears lost, but flagging this so the branch/commit history isn't a surprise later — worth
squashing/rebasing `dev/task-01` before a final submission if a clean, single-branch history is wanted.
