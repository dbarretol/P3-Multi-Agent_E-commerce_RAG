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

## 4. Phase 0 — Environment setup → **M0**

> The Udacity cloud workspace has the CloudFormation stack pre-deployed and data pre-seeded. If you work **locally** you must do steps 0.3–0.4 yourself.

### Tasks
- [ ] **0.1** Set up the environment with **uv** (from `project/starter/`):
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
- [ ] **0.2** Paste Udacity temp creds into `project/starter/.env`; confirm identity: `aws sts get-caller-identity`
- [ ] **0.3** Enable Bedrock model access in `us-east-1` console: **Claude Haiku 4.5**, **Claude Sonnet 4.5**, **Titan Embed Text v2** (`amazon.titan-embed-text-v2:0`)
- [ ] **0.4 (local only)** Deploy foundation infra:
      ```sh
      aws cloudformation deploy --template-file infrastructure/starter_stack.yaml \
        --stack-name udacity-agentcore --capabilities CAPABILITY_NAMED_IAM --region us-east-1
      python infrastructure/seed_data.py
      ```
- [ ] **0.5** `cp .env.example .env` was effectively done — verify keys present
- [ ] **0.6** Run `python config.py`

### Milestone M0 — verification
- `aws cloudformation describe-stacks --stack-name udacity-agentcore --query "Stacks[0].StackStatus"` → `CREATE_COMPLETE`
- `python config.py` shows real values for: Orders Table, Customers Table, Workflow State Table, Policy Bucket, AgentCore Role. KB / Runtime / Guardrail rows showing `(not yet …)` is expected.
- DynamoDB `udacity-agentcore-customers` has 4 items; `udacity-agentcore-orders` populated; S3 `…-policy-docs-…` has `policies/returns|shipping|warranty/` prefixes with `.txt` files.

### Evidence to collect
- **E0.1** Terminal capture: `aws sts get-caller-identity` (redact account if desired) + stack status `CREATE_COMPLETE`
- **E0.2** Terminal capture: full `python config.py` output table
- **E0.3** Console screenshot: Bedrock → Model access showing the 3 models "Access granted"
- **E0.4** Console screenshot: S3 bucket `policies/` tree (returns/, shipping/, warranty/ with files)
- **E0.5** Console screenshot: DynamoDB `udacity-agentcore-customers` items (CUST-001..004)

---

## 5. Phase 1 / Task 2 — Multi-Agent Graph → **M1, M2**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task2`

### 2.A — `build_inventory_agent()` → returns one `Agent`
- [ ] `BedrockModel(model_id=config.WORKER_MODEL_ID, region_name=config.AWS_REGION, temperature=0.1)`
- [ ] System prompt: pure **data gatherer**, never makes eligibility/refund decisions
- [ ] Tool `check_order_status(order_id)` → query `config.ORDERS_TABLE`, return status/date/amount/return_eligible
- [ ] Tool `get_customer_tier(customer_id)` → get item from `config.CUSTOMERS_TABLE`, return tier + profile
- [ ] Tool `list_customer_orders(customer_id)` → query `config.ORDERS_TABLE` by `customer_id`, return list
- [ ] Each tool has a docstring stating purpose / args / return
- [ ] Ends with `return Agent(model=…, system_prompt=…, tools=[check_order_status, get_customer_tier, list_customer_orders])`
- **Rubric:** exactly **3** tools; model = Sonnet; temp 0.1

### 2.B — `build_refund_agent()` → returns one `Agent`
- [ ] `BedrockModel(config.WORKER_MODEL_ID, temperature=0.1)`
- [ ] System prompt: decision process = (1) always call `get_inventory_context` first, (2) apply window by tier — **Standard 30 days, Premium 60 days**, (3) decide eligible / not eligible
- [ ] Tool `get_inventory_context(session_id)` → `_read_workflow_state(session_id)` and return its `inventory_agent` field (or `{}`)
- [ ] Tool `initiate_refund(customer_id, order_id, reason)` → update the order row in `config.ORDERS_TABLE` (status → return/refund), return `{return_reference, instructions}`
- **Rubric:** exactly **2** tools; 30/60-day windows encoded

### 2.C — `build_policy_agent()` → returns one `Agent` (multi-agent RAG) ⭐
- [ ] Build **3 retriever sub-agents** inside the function:
      - `ReturnsPolicyRetrieverAgent` — tool calls `retrieve_from_knowledge_base(config.RETURNS_KB_ID, query)`
      - `ShippingPolicyRetrieverAgent` — `config.SHIPPING_KB_ID`
      - `WarrantyPolicyRetrieverAgent` — `config.WARRANTY_KB_ID`
      - each retriever: `BedrockModel(config.WORKER_MODEL_ID, temperature=0.0)`, exactly 1 tool
- [ ] Implement `_run_retriever(domain, agent, query)` → invoke sub-agent, return `(domain, result_text)`
- [ ] Implement `search_all_policies(query)`:
      - build `retrievers = {'Returns': …, 'Shipping': …, 'Warranty': …}`
      - `trace.kb_start({...})` is already in starter — keep it
      - `with ThreadPoolExecutor(max_workers=3) as ex:` submit all 3, gather with `as_completed()`
      - after join: `trace.kb_done(len(retrievers))` then loop `trace.kb_result(domain, results.get(domain, '[No results]'))` for Returns/Shipping/Warranty
      - return combined text of all 3 domains
- [ ] Coordinator: `BedrockModel(config.WORKER_MODEL_ID, temperature=0.2)`, system prompt = "always call `search_all_policies` first, then synthesize a grounded answer", tools = `[search_all_policies]`
- **Rubric:** coordinator has exactly **1** tool (`search_all_policies`); `ThreadPoolExecutor(max_workers=3)` + `as_completed()`; retriever temp 0.0, coordinator temp 0.2

### 2.D — `build_communication_agent()` → returns one `Agent`
- [ ] `BedrockModel(config.WORKER_MODEL_ID, temperature=0.3)`
- [ ] System prompt: warm, professional, empathetic; include all relevant findings from prior agents
- [ ] Tool `get_full_workflow_context(session_id)` → `_read_workflow_state(session_id)` full record
- **Rubric:** exactly **1** tool; temp 0.3

### 2.E — `build_orchestrator_agent(inventory, refund, policy, communication)` → returns one `Agent`
- [ ] `BedrockModel(config.ORCHESTRATOR_MODEL_ID, temperature=0.0)`
- [ ] `initialize_session(session_id, customer_id)` → `_create_workflow_state(...)`; return confirmation
- [ ] `route_to_inventory_agent(session_id, customer_id, request)` → read state → invoke `inventory_agent(...)` → `_update_workflow_state(session_id, {'inventory_agent': result}, expected_version=state['version'])`
- [ ] `route_to_policy_agent(session_id, request)` → same read/invoke/update pattern with `{'policy_agent': result}`
- [ ] `route_to_refund_agent(session_id, customer_id, request)` → `{'refund_agent': result}`
- [ ] `route_to_communication_agent(session_id, customer_id, original_request)` → `{'communication_agent': result}`
- [ ] System prompt enforces **all 6 routing rules verbatim**:
      1. Every request → `initialize_session` **first**
      2. Order status / return / refund → inventory **then** refund
      3. Policy-meaning questions (return windows, shipping rates, warranty terms) → policy agent
      4. Account questions ("my tier?", "am I premium?") → inventory agent, **never** policy agent
      5. Math / calculation → answer directly, no routing
      6. Every request → `route_to_communication_agent` **last**, always
- [ ] CRITICAL: orchestrator **never** writes the final customer response itself
- **Rubric:** exactly **5** tools; Haiku; temp 0.0

### Milestone M1 — verification
`python tests/test_agent.py task2` → checks 2.1, 2.2, 2.3, 2.4, 2.7 pass (agents instantiate, tool counts right, model split right). Score ≥ 30/40.

### Milestone M2 — verification
- `python tests/test_agent.py task2` → **40/40**
- `python src/demo.py` → completes without exception; trace shows `Orchestrator → Inventory → Refund → Communication`; final "AGENT RESPONSE" block references order `ORD-27176` and a return reference
- `python src/agent_orchestrator.py test` → 3 scenarios each produce a response
- (needs M3 for the policy scenario to return real passages; math + refund scenarios work without KBs)

### Evidence to collect
- **E2.1** Terminal capture: `python tests/test_agent.py task2` showing `Score: 40/40 pts (100%)`
- **E2.2** Terminal capture: full `python src/demo.py` trace (Orchestrator → Inventory → Refund → Communication + final response)
- **E2.3** Terminal capture: `python src/agent_orchestrator.py test` — all 3 scenarios
- **E2.4** `git diff` of `src/agent_orchestrator.py` for Task 2 (the implemented builders)
- **E2.5** DynamoDB screenshot: a `udacity-agentcore-workflow-state` record with `version` > 0 and `inventory_agent` / `refund_agent` / `communication_agent` columns populated

---

## 6. Phase 3 / Task 5 — Bedrock Knowledge Bases → **M3**

> Do this **before** Task 3 deploy so the runtime env vars carry real KB IDs, and before testing the policy path.
**Location:** AWS Console (no code). **Test:** `python tests/test_agent.py task5`

### Tasks (repeat 3×)
- [ ] **5.1** Bedrock → Knowledge Bases → Create. Name `novamart-returns-policy-kb`
      - Data source: S3, bucket = CloudFormation `PolicyBucket`, prefix `policies/returns/`
      - Embeddings: `amazon.titan-embed-text-v2:0`
      - Vector store: **S3 Vectors**, bucket = CloudFormation `VectorStoreBucket`
- [ ] **5.2** `novamart-shipping-policy-kb` — prefix `policies/shipping/`
- [ ] **5.3** `novamart-warranty-policy-kb` — prefix `policies/warranty/`
- [ ] **5.4** Click **Sync** on each KB's data source; wait for "Completed"
- [ ] **5.5** Copy each KB ID into `.env`: `RETURNS_KB_ID=`, `SHIPPING_KB_ID=`, `WARRANTY_KB_ID=`

### Milestone M3 — verification
- `python tests/test_agent.py task5` → **25/25** (all 3 IDs set, all 3 KBs `ACTIVE`)
- Quick retrieval smoke test from `project/starter/`:
  ```sh
  python -c "from src.agent_orchestrator import build_policy_agent; a=build_policy_agent(); print(a('What is the return window for premium customers and the expedited shipping cost?'))"
  ```
  → answer cites content from **all three** domains (60-day return, $9.99 expedited, 3-year warranty)

### Evidence to collect
- **E3.1** Console screenshot: KB list showing all 3 KBs, status `Available`
- **E3.2** Console screenshot (×3): each KB's data source **Sync history = Completed**, showing embedding model + S3 Vectors store + prefix
- **E3.3** Terminal capture: `python tests/test_agent.py task5` = `25/25`
- **E3.4** Terminal capture: the `search_all_policies` / policy-agent smoke test showing non-empty passages from Returns + Shipping + Warranty (this satisfies rubric `test_5_parallel_retrieval` intent)
- **E3.5** `.env` excerpt (KB ID lines)

---

## 7. Phase 2 / Task 3 — Guardrail + AgentCore Runtime → **M4**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task3`

### `create_guardrail()` → `(guardrail_id, guardrail_version)`
- [ ] `bedrock` client `create_guardrail(name=config.GUARDRAIL_NAME, …)` with:
      - **contentPolicyConfig**: SEXUAL, VIOLENCE, HATE → `HIGH` (input+output); INSULTS, MISCONDUCT → `MEDIUM`
      - **sensitiveInformationPolicyConfig**: `CREDIT_DEBIT_CARD_NUMBER`, `US_SOCIAL_SECURITY_NUMBER` → `BLOCK`; `EMAIL`, `PHONE` → `ANONYMIZE`
      - **topicPolicyConfig**: DENY topics — competitor products, pricing negotiations, legal threats (use `config.GUARDRAIL_BLOCKED_TOPICS`)
      - **wordPolicyConfig**: managed word list `PROFANITY`
      - `blockedInputMessaging` + `blockedOutputsMessaging` (friendly text)
- [ ] `create_guardrail_version(guardrailIdentifier=id)` — promote DRAFT → numbered version
- [ ] return `(id, version)`
- (starter already handles the "guardrail already exists" short-circuit)

### `deploy_to_agentcore_runtime(orchestrator_agent, guardrail_id, guardrail_version)` → runtime ARN
- [ ] `agentcore_control.create_agent_runtime(...)`:
      - `agentRuntimeName` = `runtime_name` (starter-computed), `description`, `roleArn=config.AGENTCORE_ROLE_ARN`
      - `networkConfiguration` → **PUBLIC**
      - `protocolConfiguration` → **MCP**
      - `agentRuntimeArtifact` → the S3 zip already uploaded by starter (`bucket=config.POLICY_BUCKET`, key `artifact_key`), runtime `PYTHON_3_12`
      - `environmentVariables`: `AWS_REGION`, `PROJECT_NAME`, `RETURNS_KB_ID`, `SHIPPING_KB_ID`, `WARRANTY_KB_ID`, `AGENT_LOG_GROUP`
      - guardrail is injected by the pre-written `before-call` hook — don't pass it explicitly
- [ ] return `response.get('agentRuntimeArn', response.get('arn',''))`

### Deploy + record
- [ ] `python src/agent_orchestrator.py deploy` (runs the 6-step pipeline)
- [ ] Copy printed values into `.env`: `AGENTCORE_RUNTIME_ARN=`, `GUARDRAIL_ID=`, `GUARDRAIL_VERSION=`

### Milestone M4 — verification
- Deploy command completes through Step 3/6 (and 4–6) without fatal error
- `python tests/test_agent.py task3` → **20/20** (guardrail named `udacity-agentcore-guardrail` exists; has content + PII + topic policies; runtime ARN set)

### Evidence to collect
- **E4.1** Terminal capture: full `python src/agent_orchestrator.py deploy` output (all 6 steps, final ARN + guardrail id/version block)
- **E4.2** Console screenshot: Bedrock → Guardrails → `udacity-agentcore-guardrail` detail — content filter strengths, PII entities (BLOCK/ANONYMIZE), denied topics, profanity on, **Version** ≠ DRAFT
- **E4.3** Console screenshot: Bedrock AgentCore → Runtimes → the runtime showing `PUBLIC` network, `MCP` protocol, env vars
- **E4.4** Terminal capture: `python tests/test_agent.py task3` = `20/20`
- **E4.5** `.env` excerpt (`AGENTCORE_RUNTIME_ARN`, `GUARDRAIL_ID`, `GUARDRAIL_VERSION`)
- **E4.6 (stretch, rubric "stand out")** adversarial probes vs the guardrail — prompt injection, competitor mention, legal threat — with blocked-response screenshots

---

## 8. Phase 2 / Task 4 — AgentCore Memory → **M5**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task4`

### `configure_memory(runtime_arn)` → `memoryArn`
- [ ] `agentcore_control.create_memory(...)`:
      - `name` = `config.MEMORY_NAMESPACE` (hyphens→underscores, starter does this), `description`
      - `eventExpiryDuration=7` (7-day retention)
      - `memoryStrategies=[{ 'summaryMemoryStrategy': { 'name': …, 'namespaces': [...] } }]` (SESSION_SUMMARY strategy)
      - `clientToken=` a stable string for idempotency
- [ ] return `memoryArn`
- (starter short-circuits if a memory with that prefix already exists)

### Milestone M5 — verification
`python tests/test_agent.py task4` → **15/15** — `get_agent_runtime(...).memoryConfiguration.enabledMemoryTypes` contains `SESSION_SUMMARY`
(the deploy pipeline Step 4/6 calls this; re-run `deploy` if you implemented it after the first deploy)

### Evidence to collect
- **E5.1** Terminal capture: `python tests/test_agent.py task4` = `15/15`
- **E5.2** Terminal capture: deploy pipeline "Step 4/6: Configuring Memory…" line + returned memory ARN
- **E5.3** Console screenshot: Bedrock AgentCore → Memory resource showing `SESSION_SUMMARY` strategy + 7-day expiry
- **E5.4** `git diff` of `configure_memory()`

---

## 9. Phase 4 / Task 6 — Observability → **M6, M7**

**File:** `src/agent_orchestrator.py` · **Test:** `python tests/test_agent.py task6`

### `configure_observability(runtime_arn)` → `None`
- [ ] `runtime_id = runtime_arn.split('/')[-1]`
- [ ] `try:` `agentcore_control.put_agent_runtime_logging_configuration(agentRuntimeId=runtime_id, loggingConfiguration={...})` with:
      - `cloudWatchConfig`: `logGroupName=config.AGENT_LOG_GROUP`, `logLevel='INFO'`, `enabled=True`
      - `xRayConfig`: `enabled=True`, `samplingRate=1.0`
      - on success: print log group + sampling rate
- [ ] `except Exception as e:` print `"[Note] Logging config skipped (SDK version mismatch): {e}"`

### Milestone M6 — verification
`python tests/test_agent.py task6` → **20/20** (CloudWatch `enabled=True`, X-Ray `enabled=True`)

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
| Temp creds expire mid-task | `ExpiredToken` / `InvalidClientTokenId` | re-paste all 3 values in `.env`; keep the Udacity credentials tab open |
| Bedrock model not enabled | `AccessDeniedException` on invoke | Phase 0.3 — grant access to Haiku 4.5 / Sonnet 4.5 / Titan Embed v2 in us-east-1 |
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
- [ ] Submission package assembled per Udacity classroom instructions
