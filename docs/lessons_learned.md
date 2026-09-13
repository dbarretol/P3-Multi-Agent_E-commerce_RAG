# Lessons Learned — NovaMart Multi-Agent E-commerce RAG

Running log of problems hit while setting up and building the project, with root cause and fix.
Newest entries at the bottom of each section.

---

## L1 — `git clone` fails on Windows: "Filename too long"

**Symptom**
```
fatal: cannot create directory at 'lesson-01-.../demo-healthcare-triage': Filename too long
warning: Clone succeeded, but checkout failed.
```

**Root cause** — Windows `MAX_PATH` (260 char) limit; the classroom repo has deep nested paths.

**Fix** — clone with long-path support on:
```sh
git clone -c core.longpaths=true https://github.com/udacity/cd14764-aws-agentic-c3-classroom.git .
```
(If it still trips, also enable OS-level long paths: `git config --global core.longpaths true` and the
`HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled=1` registry key.)

---

## L2 — `.env` location vs. how tools find it

**Symptom** — `config.py` loads `.env` fine, but `aws ...` CLI commands fail with `InvalidClientTokenId`
even though the credentials are valid.

**Root cause** — `.env` lives at the **repo root** (`…/P3-Multi-Agent_E-commerce_RAG/.env`), not in
`project/starter/`. `config.py`'s `load_dotenv()` walks parent directories and finds it. The **AWS CLI
does not read `.env` at all** — it only reads real environment variables / `~/.aws`.

**Fix** — for any `aws` CLI command, source the env first (Git Bash), from `project/starter/`:
```sh
set -a && source ../../.env && set +a && aws sts get-caller-identity --region us-east-1
```
For Python scripts that call `load_dotenv()` (like `config.py`), no action needed.
For Python scripts that **don't** (`infrastructure/seed_data.py` — see L4), source the env the same way.

---

## L3 — `UnicodeEncodeError` on Windows console

**Symptom**
```
UnicodeEncodeError: 'charmap' codec can't encode character '✓' in position 2
```
Hit in `seed_data.py` (prints `✓`), and would also hit `config.py` / `tests/test_agent.py` (box-drawing chars).

**Root cause** — Windows console default code page is cp1252; Python encodes stdout with it.

**Fix** — force UTF-8 for every Python invocation:
```sh
PYTHONUTF8=1 uv run python <script>
```
(or set `PYTHONUTF8=1` once for the session / in `.env` is not enough since it must be a process env var
before Python starts — prefix each command, or `export PYTHONUTF8=1` in the shell).

---

## L4 — `seed_data.py` has no `load_dotenv()`

**Root cause** — the script is written for the Udacity workspace where AWS creds are ambient. It uses
`boto3` and `os.environ.get('AWS_REGION', ...)` directly, no dotenv.

**Fix** — source the root `.env` before running it (and add `PYTHONUTF8=1` per L3):
```sh
cd project/starter && set -a && source ../../.env && set +a && PYTHONUTF8=1 uv run python infrastructure/seed_data.py
```
Idempotent — safe to re-run (all `put_item` / `put_object`). `create_test_user()` warn-skips (no Cognito
UserPool in this stack) — expected.

---

## L5 — Environment with `uv` (not pip/venv)

**Working setup** (from `project/starter/`):
```sh
uv venv --python 3.12                 # 3.12 matches the AgentCore runtime target
uv pip install -r requirements.txt    # strands-agents 1.54.0, boto3, python-dotenv, ...
# run: `uv run python <script>`  (auto-uses ./.venv)  — or activate .venv\Scripts\Activate.ps1
```
No `pyproject.toml` needed; `uv run` uses the local `.venv` directly.

---

## L6 — CloudFormation deploy blocked by Claude Code auto-approval

**Symptom** — `aws cloudformation deploy ...` returned
`Permission for this action was denied by the Claude Code auto mode classifier`.

**Root cause** — state-changing infra command; the auto-approver blocks it by design.

**Fix** — user approves the tool call, or runs it themselves with the `!` prefix in the prompt
(must source `.env` in the same line — shell state doesn't persist between `!` commands):
```
! cd project/starter && set -a && source ../../.env && set +a && aws cloudformation deploy --template-file infrastructure/starter_stack.yaml --stack-name udacity-agentcore --capabilities CAPABILITY_NAMED_IAM --region us-east-1
```
Result: stack `CREATE_COMPLETE`, 7 exports. Then `seed_data.py` (L4).

---

## L7 — ⛔ BLOCKER: AWS Academy learner-lab account cannot invoke Anthropic Bedrock models

**Symptom** — `bedrock-runtime` `Converse` / `InvokeModel` for `us.anthropic.claude-haiku-4-5-*` and
`us.anthropic.claude-sonnet-4-5-*` fail — first intermittently (~20–40% success), then consistently:
```
AccessDeniedException: Model access is denied due to IAM user or service role is not authorized to
perform the required AWS Marketplace actions (aws-marketplace:ViewSubscriptions, aws-marketplace:Subscribe)
to enable access to this model. ... Your AWS Marketplace subscription for this model cannot be completed
at this time.
```
`amazon.titan-embed-text-v2:0` (Amazon-owned, no Marketplace) works fine.

**Diagnosis (proven)**
- Account `303688964032`, role `arn:aws:sts::…:assumed-role/voclabs/user4334897=…` → an
  **AWS Academy / Vocareum learner lab**.
- `bedrock.get_foundation_model_availability(...)` returns `authorizationStatus=AUTHORIZED`,
  `entitlement=AVAILABLE`, `region=AVAILABLE` in us-east-1 / us-east-2 / us-west-2 — i.e. "model access"
  *looks* granted, and the Bedrock **console playground works**.
- But `iam.simulate_principal_policy` on the caller:
  | action | decision |
  |---|---|
  | `bedrock:InvokeModel` | **allowed** |
  | `aws-marketplace:ViewSubscriptions` | allowed |
  | `aws-marketplace:Subscribe` | **explicitDeny** |
- Modern Anthropic models on Bedrock are gated behind an **AWS Marketplace subscription/agreement**.
  On a cold entitlement cache, Bedrock re-checks/re-establishes that subscription against the *caller's*
  identity at invoke time; the `voclabs` explicit deny on `aws-marketplace:Subscribe` makes it fail.
  Warm cache → occasional success (explains the early flakiness and the working playground).
- Course docs confirm this is expected for lab accounts:
  - `3-Multi-Agent…/1-Introduction…/3.md`: *"AWS accounts are provided with the IAM permissions and
    Bedrock model access required for every exercise and the capstone — learners do not need their own
    AWS account."*
  - `1-Prompting…/14-Project…/2.Environment Setup.md`: *"do not rely on the harness default model, which
    requires an AWS Marketplace subscription that lab accounts cannot complete."*

**There is no missing setup step.** The instruction set (`19-Multi-Agent E-commerce RAG`) has no
"enable model access" task because it assumes the Udacity-provided AWS account.

**Deep-dive (2026-09-03) — every avenue checked, one irreducible blocker:**

| Check | Result |
|---|---|
| Model IDs in `config.py` | ✅ correct — `us.anthropic.claude-{haiku,sonnet}-4-5-*` inference profiles exist and are `ACTIVE` (also `global.*`). Bare `anthropic.*` IDs are **not invocable** (on-demand not supported). |
| `bedrock.get_use_case_for_model_access()` | ✅ already submitted (`companyName: "Vocareum"`) — the Anthropic use-case form is **not** the gate |
| `bedrock.list_foundation_model_agreement_offers(modelId=…)` | ✅ 1 offer available per model (valid `offerToken`) |
| `bedrock.create_foundation_model_agreement(modelId, offerToken)` | ❌ `AccessDeniedException: … not authorized to perform: aws-marketplace:Subscribe on resource: *` |
| direct `Converse` / `InvokeModel` | ❌ same — Bedrock tries to auto-accept the agreement **as the caller** and hits the same deny |

The **"Model access" console page is retired**. New behaviour (per AWS notice): Amazon-owned models
auto-enable on first invoke; **Marketplace-served models (Anthropic) require a user _with AWS Marketplace
permissions_ to invoke/accept once, which enables the model account-wide for everyone else.** The
`voclabs` role has **no** `aws-marketplace:Subscribe`, and no other principal exists on an AWS Academy
lab account — so the one-time account-wide enablement **can never happen** here. Amazon Titan works
because it isn't Marketplace-gated.

The console **playground** appearing to work = it hit one of the brief intermittent windows, or a
console-side entitlement that doesn't persist for API callers. `create_foundation_model_agreement` is the
operation that must succeed, and it is hard-denied.

**Fix / path forward — all that's needed is one account where the agreement can be accepted once:**
1. **Udacity-provided workspace + AWS account** — intended environment (repo at
   `/workspace/cd14764-aws-agentic-c3-classroom/`, infra + Bedrock pre-provisioned). Best option.
2. **Personal (non-Academy) AWS account** — sign in as root/admin (has `aws-marketplace:Subscribe`),
   open Claude Haiku 4.5 + Sonnet 4.5 once in the Bedrock playground *or* run
   `aws bedrock create-foundation-model-agreement --model-id anthropic.claude-haiku-4-5-20251001-v1:0 --offer-token <token>`.
   After that first accept, every IAM principal in the account (incl. the AgentCore execution role) can invoke.
3. Ask whoever administers the Academy/org account to do that one-time accept.

Not viable: single-region pin or bare model ID (L8); editing `config.py` (do-not-modify); retry wrappers
(AccessDenied isn't retryable and Strands owns the client).

**Confirmed via AWS Marketplace → Manage subscriptions (screenshot, 2026-09-03):**
Account has **4 active org-shared** Anthropic agreements, all dated 2025-09-11:
Claude Opus 4, Claude Sonnet 4, Claude 3.5 Haiku, Claude 3.7 Sonnet — plus a "No permission to view
licenses / ListReceivedLicenses" banner (entitlements are pushed from the AWS Organization, not
self-managed). **Claude Haiku 4.5 and Claude Sonnet 4.5 — the two IDs `config.py` requires — are NOT in
that set**, and `voclabs` cannot add them.

Sustained invoke test (30 calls each, us-east-1, 2026-09-03 ~04:40Z):
`us.anthropic.claude-haiku-4-5-*` → **0/30**, `us.anthropic.claude-sonnet-4-5-*` → **0/30**.
A few unrelated future-dated profiles (`claude-sonnet-4-6`, `claude-opus-4-5/4-6`) invoke *intermittently*
but also flap run-to-run — the whole account's Anthropic entitlement is unstable, not just the 4.5 pair.
The bare older IDs from the subscription list (`claude-3-5-haiku`, `claude-3-7-sonnet`, `claude-sonnet-4`)
return `ResourceNotFoundException` (not offered in us-east-1 anymore).

**Verdict: this AWS account cannot run the project.** No local workaround (nothing is reliably entitled;
`config.py` is do-not-modify). Move to the Udacity workspace/account, or have the org add
Haiku 4.5 + Sonnet 4.5 subscriptions.

**Everything else in Phase 0 is done** — once model calls return green, resume at Task 2 with no rework.

**Re-test command**
```sh
cd project/starter && set -a && source ../../.env && set +a && PYTHONUTF8=1 uv run python - <<'PY'
import boto3
for r in ["us-east-1","us-east-2","us-west-2"]:
    b=boto3.client("bedrock-runtime",region_name=r); ok=0
    for _ in range(8):
        try: b.converse(modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
              messages=[{"role":"user","content":[{"text":"hi"}]}],inferenceConfig={"maxTokens":3}); ok+=1
        except Exception: pass
    print(r,"ok",ok,"/8")
PY
```
Green = `8/8` in every region.

---

## L8 — Claude 4.5 models need an inference profile

**Symptom** — calling `anthropic.claude-haiku-4-5-20251001-v1:0` (bare ID) →
```
ValidationException: Invocation of model ID anthropic.claude-haiku-4-5-20251001-v1:0 with on-demand
throughput isn't supported. Retry your request with the ID or ARN of an inference profile ...
```

**Root cause** — these models are only available via a **system inference profile**. `config.py` already
uses the right IDs: `us.anthropic.claude-haiku-4-5-20251001-v1:0` /
`us.anthropic.claude-sonnet-4-5-20250929-v1:0` (the `us.` prefix = cross-region US profile spanning
us-east-1 / us-east-2 / us-west-2).

**Implication** — model access must be enabled in **all three** backing regions, not just us-east-1,
because the profile load-balances across them. (Moot on this account — see L7.)

---

## L9 — Teardown (2026-09-03)

Account can't run the project (L7), so everything created was destroyed:
- Emptied both versioned S3 buckets (`…-policy-docs-…`, `…-vectors-…`), then
  `cloudformation delete-stack udacity-agentcore` → `DELETE_COMPLETE`.
- Verified gone: DynamoDB tables, S3 buckets, IAM role `udacity-agentcore-agentcore-role`
  (`NoSuchEntity`), log group, all `udacity-agentcore-*` exports. No Guardrail / AgentCore Runtime /
  Memory / Knowledge Base was ever created (deploy pipeline never ran).
- **Kept locally:** repo, `project/starter/.venv`, root `.env` (creds will expire — wipe the values),
  `docs/PROJECT_PLAN.md`, `docs/lessons_learned.md`, evidence.

**To resume** on a working account: `cd project/starter`, source `.env`, then
`aws cloudformation deploy … --stack-name udacity-agentcore --capabilities CAPABILITY_NAMED_IAM`
and `PYTHONUTF8=1 uv run python infrastructure/seed_data.py` (plan step 0.4). On the Udacity workspace
the stack is already deployed — skip straight to `config.py` then Task 2.

---

## L10 — Re-verified 2026-09-03 with fresh creds + inside the Udacity workspace (still blocked)

Retested after the user set **new temporary credentials** and after opening the **Udacity in-browser
workspace**. No change — and two things now nailed down:

1. **The Udacity "workspace" is the same AWS account/role.** `sts.get_caller_identity` from the
   workspace terminal → `arn:aws:sts::303688964032:assumed-role/voclabs/user4334897=…` — identical to
   local. The workspace ships **no** AWS credentials of its own (`~/.aws` absent, no `AWS_*` env vars,
   `boto3.Session().get_credentials()` → `None`); it only works once you paste the same lab creds into
   `project/starter/.env`. So switching to the workspace does **not** change Bedrock access.

2. **The programmatic model-access path is hard-denied, confirmed by direct call:**
   | call | result |
   |---|---|
   | `bedrock.put_use_case_for_model_access(formData=…)` | ✅ **HTTP 201** — Anthropic FTU form now on file for `303688964032` (student details) |
   | `bedrock.list_foundation_model_agreement_offers(modelId="anthropic.claude-{haiku-4-5,sonnet-4-5}…")` | ✅ 1 offer each (`offer-fudwqbphlos64`, `offer-qac56zmvs7neg`) |
   | `bedrock.create_foundation_model_agreement(offerToken, modelId)` | ❌ `AccessDeniedException: … not authorized to perform: aws-marketplace:Subscribe on resource: * because no identity-based policy allows the aws-marketplace:Subscribe action` |
   | `Converse` on `us.anthropic.claude-{haiku,sonnet}-4-5-*` | ❌ `AccessDeniedException: Model access is denied … required AWS Marketplace actions (aws-marketplace:ViewSubscriptions, aws-marketplace:Subscribe)` |

   The FTU form was **not** the gate (submitting it just changed the error text from generic to the
   explicit `aws-marketplace:*` message). `agreementAvailability` stays `NOT_AVAILABLE`.

**Research — how model access works now (AWS docs, Sep 2026):** the old **"Model access" console page is
retired** in commercial regions and `PutFoundationModelEntitlement` "no longer has an effect." Current
flow: on first invoke Bedrock **auto-creates the AWS Marketplace subscription in the background**, which
needs `aws-marketplace:Subscribe` on the *caller*. The only alternative the docs offer: *"someone with
AWS Marketplace permissions must enable the model for the account as a one-time step"* (then everyone
else in the account can invoke without it). There is **no EULA-only / no-Marketplace acceptance path**
for Anthropic models — `CreateFoundationModelAgreement` itself calls `aws-marketplace:Subscribe`.
Sources: <https://aws.amazon.com/blogs/security/simplified-amazon-bedrock-model-access/>,
<https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html>.

**Therefore, on the Academy account there is genuinely no route.** Need a principal that has
`aws-marketplace:Subscribe` (personal AWS root/admin), or the AWS-Org management account (Udacity/AWS
Academy admin) to do the one-time enable, or a Udacity-provided account that already has it.

**Re-test after moving accounts** — save as `project/starter/verify.py`, `python verify.py`:
```python
from dotenv import load_dotenv; load_dotenv()
import json, boto3
print("ID:", boto3.client("sts","us-east-1").get_caller_identity()["Arn"])
br = boto3.client("bedrock-runtime","us-east-1")
for m in ["us.anthropic.claude-haiku-4-5-20251001-v1:0","us.anthropic.claude-sonnet-4-5-20250929-v1:0"]:
    try:
        br.converse(modelId=m, messages=[{"role":"user","content":[{"text":"hi"}]}],
                    inferenceConfig={"maxTokens":5}); print("OK  ", m)
    except Exception as e: print("FAIL", m, "->", type(e).__name__, str(e)[:120])
```

**Re-confirmed again 2026-09-12** with a fresh set of Udacity temp credentials (`arn:aws:sts::303688964032:assumed-role/voclabs/user4334897=…`, new session id). Identical result — same `AccessDeniedException` on both Claude models
(`... required AWS Marketplace actions (aws-marketplace:ViewSubscriptions, aws-marketplace:Subscribe) ...`), Titan still OK. Confirms the block is tied to the **account/role's IAM policy**, not to credential
age/expiry — refreshing the temp creds can never fix it. Do not re-test this account again; move straight
to the personal-account credentials (L11).

---

## L11 — ✅ RESOLVED (2026-09-09): moved to a personal AWS account, model access works

Abandoned the Academy account. Switched `.env` to a **personal AWS account** (`187021010483`).
Two sub-problems on the way:

1. **`AWS_SESSION_TOKEN=none` in `.env` → `InvalidClientTokenId`.** python-dotenv loaded the literal
   string `none` and boto3 sent it as the session token. Permanent IAM keys (`AKIA…`) must have **no**
   session token — comment the line out entirely (`#AWS_SESSION_TOKEN=none`), don't set it empty either.

2. **Wrong IAM principal.** First key belonged to `user/oss-models-terraform` — a scoped Terraform
   service account with **zero** Bedrock permissions. Every call (incl. Titan) → plain
   `AccessDeniedException: not authorized to perform: bedrock:InvokeModel`. This is an IAM-policy gap,
   **not** the Marketplace block — account-level model-access / quota grants do nothing for a principal
   that lacks `bedrock:*`. Fix: created a dedicated IAM user **`udacity-agentcore-dev`** with
   `AdministratorAccess` (personal account, short-lived project; the CFN stack creates a named IAM role
   and AgentCore needs `iam:PassRole`, so a narrow policy just adds friction), new access key → `.env`.
   Better than widening the Terraform user: no shared blast radius, clean teardown (delete one user).

**Verification (`scratchpad/verify2.py`, 2026-09-09):**
```
IDENTITY: arn:aws:iam::187021010483:user/udacity-agentcore-dev
anthropic.claude-haiku-4-5-20251001-v1:0   INVOKE OK -> pong   (entitlement AVAILABLE, authorized)
anthropic.claude-sonnet-4-5-20250929-v1:0  INVOKE OK -> pong   (agreement AVAILABLE)
TITAN EMBED v2: OK
```
- First `Converse` call auto-subscribed via Marketplace in the background (Admin has
  `aws-marketplace:Subscribe`). No console step needed.
- `get_foundation_model_availability` for Haiku still reports `agreementAvailability: NOT_AVAILABLE`
  while `entitlementAvailability: AVAILABLE` and the invoke succeeds — the agreement field is
  **cosmetic/lagging**, trust the actual invoke.

**Applied service quotas (us-east-1, both Haiku 4.5 and Sonnet 4.5 V1):**
| quota | value |
|---|---|
| Cross-region model inference **requests** per minute | **10** (AWS default) |
| Cross-region model inference **tokens** per minute | **5,000,000** (AWS default) |

These are the stock defaults — the requested increase either hasn't landed or wasn't needed. 10 RPM is
low for a 5-agent fan-out (orchestrator + 4 workers per query) — **expect `ThrottlingException` during
multi-agent runs**; the SDK retries with backoff, or request an increase to ~50–100 RPM if it bites.

**Pre-flight re-check (2026-09-12), full resource sweep before starting Task 2:**
- Re-confirmed both models + Titan invoke OK. `agreementAvailability` for Haiku has since caught up to
  `AVAILABLE` (was lagging `NOT_AVAILABLE` on 09-09) — confirms that field is just slow to sync, not a
  real signal.
- **Quota increase history found:** a request to raise Haiku's requests/min quota to 10,000 →
  `CASE_CLOSED` (not granted; still stuck at the default 10). No successful increase has landed for
  either model. Left as an accepted risk — retry with backoff should absorb it during solo dev/testing;
  revisit only if `ThrottlingException` actually shows up.
- `aws-marketplace` is **not a valid boto3 service name** (typo trap: it's not a low-level client) — don't
  try to query subscriptions that way; a successful `Converse` call is the only test that matters.
- CloudFormation stack `udacity-agentcore` confirmed **not deployed** (`ValidationError: Stack ... does
  not exist`) — matches the L9 teardown; Phase 0.4 redeploy is still the next step.
- `bedrock-agentcore-control` (`list_agent_runtimes`), `bedrock` (`list_guardrails`), and `bedrock-agent`
  (`list_knowledge_bases`) all reachable, each returning 0 — expected pre-build state, confirms no
  permission gaps for Tasks 3/4/5/6 ahead of time.
- IAM user `udacity-agentcore-dev` has `AdministratorAccess` attached — no permission surprises expected
  anywhere in the build.

**Resume path** (do NOT start until user confirms): deploy CFN stack `udacity-agentcore`
(`aws cloudformation deploy --template-file infrastructure/starter_stack.yaml --stack-name udacity-agentcore --capabilities CAPABILITY_NAMED_IAM --region us-east-1`)
→ `PYTHONUTF8=1 uv run python infrastructure/seed_data.py` → `python config.py` → Task 2 in
`project/starter/src/agent_orchestrator.py`. Set a **billing alarm (~$50)** first.

---

## L12 — ✅ Verified (2026-09-12): local starter kit is byte-identical to upstream `main`

Ran a full diff of every graded/non-graded starter file against `raw.githubusercontent.com/udacity/cd14764-aws-agentic-c3-classroom/main/project/starter/...` (fetched via `gh api` + `curl`, no local git remote is configured for this working copy):

- **Identical:** `src/agent_orchestrator.py` (1230/1230 lines, 0 diff), `src/agent_utils.py`, `src/bedrock_kb_retrieval.py`, `src/demo.py`, `config.py`, `tests/test_agent.py`, `infrastructure/starter_stack.yaml`, `infrastructure/seed_data.py`, `requirements.txt`, `.env.example` (root-level copy), `README.md`.
- No newer commit exists upstream that we're missing — latest commit touching `project/starter` is `4eeecb3` (2026-05-29, "fix aws validation constraints": `runtime_name` hyphens → underscores for AgentCore naming validation), and our local `agent_orchestrator.py` already has that exact fix at line 676.
- Repo `pushed_at` = 2026-06-14 (last real push); `updated_at` = 2026-09-06 is just GitHub metadata (stars/description/etc.), not a code change.
- **Conclusion:** the TODOs in `agent_orchestrator.py` are exactly as Udacity shipped them — nothing to re-pull, no upstream fix or scaffolding change was missed. All remaining work is implementation (Task 2) and infra/deploy (Tasks 3–6), not a stale starter kit.

---

## L13 — ✅ Task 2 implemented and verified live (2026-09-12); infra redeployed; unexpected git auto-commits discovered

**Infra:** Redeployed `udacity-agentcore` CFN stack on the personal account (187021010483) and re-seeded
data — closes out [[L11]]'s pending 0.4/0.6 steps. `uv run python config.py` now shows all 5 resource
rows populated. Full resource list + teardown steps: `PROJECT_PLAN.md` §16.

**Task 2 (`agent_orchestrator.py`):** Implemented all five `build_*_agent()` functions per the rubric —
InventoryAgent (3 DynamoDB tools), RefundAgent (2 tools, 30/60-day tier logic), PolicyAgent (3 parallel
retriever sub-agents + `ThreadPoolExecutor(max_workers=3)` coordinator), CommunicationAgent (1 tool),
OrchestratorAgent (5 routing tools, all 6 routing rules in the system prompt). `test_agent.py task2` →
**40/40**.

One schema detail worth recording: `OrdersTable`'s key is a `customer_id`(HASH)+`order_id`(RANGE)
composite with no GSI, but `check_order_status(order_id)` only receives `order_id` — so it has to
`Table.scan(FilterExpression=Attr('order_id').eq(...))` rather than a direct `get_item`. Fine at this
data scale (15 seeded orders); would need a GSI on `order_id` at real scale.

**Live verification (real Bedrock + DynamoDB, not just the unit-style `task2` checks):**
- Full chain proven against a real seeded order (`ORD-91987`, CUST-002/Standard, delivered 2026-06-28):
  Orchestrator → Inventory → Refund → Communication, WorkflowState version 0→1→2→3, RefundAgent
  correctly applied the 30-day Standard window and **denied** the return (order was ~76 days old at the
  time of the test) — correct behavior, not a bug.
- `demo.py`'s hardcoded `ORD-27176` doesn't exist in this run's randomly-seeded data (`seed_data.py`
  generates random 5-digit order IDs each run), so that exact scenario prints "order not found" instead
  of a happy-path refund. The system handled it gracefully — Orchestrator routed Inventory →
  Communication and correctly skipped Refund. Not a code defect; just a seed-data/demo-script mismatch
  worth knowing about if `demo.py`'s output looks different from the lesson's expected example.
- `agent_orchestrator.py test` — all 3 canonical scenarios ran clean: return request, policy question
  (parallel retrieval dispatched correctly, gracefully returned "no results" since Task 5's KBs don't
  exist yet), and the math question (correctly answered directly by the Orchestrator with **no**
  sub-agent routing — confirms routing rule 5).
- No `ThrottlingException` observed across ~4 separate live test runs in immediate succession, despite
  the account's 10 req/min quota ceiling noted in [[L11]].

**⚠️ Unexpected discovery: automatic git commits + branch switch, not initiated via an explicit `git
commit`/`git checkout` in this conversation.** Mid-session, `git reflog` showed a `checkout: moving from
main to dev/task-01`, followed by commits with AI-style generated messages — one bundling the previous
turn's docs edits, one for this turn's `agent_orchestrator.py` implementation. Verified carefully before
concluding anything: `main` is untouched (still the pristine 34-TODO starter); `dev/task-01`'s HEAD
matches the actual working-tree implementation exactly (confirmed via TODO-count diffing and `grep` for
specific function/tool names — `search_all_policies`, `ShippingPolicyRetrieverAgent`, etc. are all
present, contradicting the second commit's message which undersells the diff as "Returns retriever only").
**No work was lost.** Most likely explanation: some checkpoint/autosave feature of the harness, not a
second concurrent agent — but flagging clearly since it changed repo state (new branch, new commits)
without an explicit git action being requested. If this recurs, check `git reflog` early rather than
assuming `git status`/`git diff` reflect only this session's intentional actions.

---

## L14 — ✅ Task 5 (Knowledge Bases) created via CLI, not the console; S3 Vectors is a separate resource type

The lesson instructions say to create the 3 KBs in the AWS Console. Did it via `bedrock-agent` +
`s3vectors` CLI calls instead — produces the identical AWS resources, just scriptable/reproducible.

**Key discovery:** the CFN stack's `VectorStoreBucket` (`udacity-agentcore-vectors-*`, an
`AWS::S3::Bucket`) is a **plain S3 bucket**, not an S3 Vectors "vector bucket". S3 Vectors is its own
service/ARN namespace (`arn:aws:s3vectors:...:bucket/...`, distinct from `arn:aws:s3:::...`) with its own
CLI (`aws s3vectors ...`) and its own resources: a vector bucket, and one or more vector indexes inside
it (each index needs `--dimension`, `--data-type`, `--distance-metric` set at creation — used 1024 /
float32 / cosine to match Titan Embed Text v2's default output). `create-knowledge-base`'s
`storageConfiguration.s3VectorsConfiguration` takes `vectorBucketArn` + `indexName`, **not** a plain S3
bucket ARN. The console's "S3 Vectors" KB wizard almost certainly provisions one of these under the hood
when you pick that option — the lesson's "use the VectorStoreBucket from CloudFormation outputs"
instruction is a simplification that doesn't hold up against the actual API shape. The CFN-created
`VectorStoreBucket` ends up unused; harmless to leave (deleted along with the stack), just not what the
KBs actually point at.

**Command sequence that worked** (region us-east-1, role = `config.AGENTCORE_ROLE_ARN`, which already
had the trust policy for `bedrock.amazonaws.com` and the `s3vectors:*` / `bedrock:InvokeModel` IAM
permissions the CFN stack granted it — no template changes needed):
1. `aws s3vectors create-vector-bucket --vector-bucket-name udacity-agentcore-vectors-187021010483`
2. `aws s3vectors create-index --vector-bucket-name ... --index-name {returns,shipping,warranty}-index --data-type float32 --dimension 1024 --distance-metric cosine` (×3)
3. `aws bedrock-agent create-knowledge-base` (×3) — `knowledgeBaseConfiguration.type=VECTOR`,
   `embeddingModelArn` = Titan Embed Text v2 foundation-model ARN; `storageConfiguration.type=S3_VECTORS`
   with the matching `vectorBucketArn`/`indexName`
4. `aws bedrock-agent create-data-source` (×3) — S3 type, `bucketArn` = the CFN `PolicyBucket`,
   `inclusionPrefixes: ["policies/{domain}/"]`
5. `aws bedrock-agent start-ingestion-job` (×3) → all reached `COMPLETE` within seconds (2 docs each, 0 failed)

**Result:** `test_agent.py task5` → 25/25. Live `search_all_policies()` smoke test returned real, grounded
passages from all three domains (60-day Premium return window, free expedited shipping, 3-year
electronics warranty) — full parallel multi-agent RAG path confirmed end-to-end against live KBs.

**Teardown reminder:** these are resources the CFN stack does **not** own — deleting the stack later will
NOT remove the 3 KBs, the S3 Vectors indexes, or the S3 Vectors bucket. See `PROJECT_PLAN.md` §16 for the
explicit delete commands, and delete the KBs before the S3 Vectors bucket/indexes (a KB can hold a
reference that blocks index deletion otherwise).

---

## L15 — ✅ Task 3 (Guardrail + AgentCore Runtime) implemented and deployed (2026-09-12)

Implemented `create_guardrail()` and `deploy_to_agentcore_runtime()` in `agent_orchestrator.py`. `boto3`
API shapes confirmed via `aws ... create-guardrail --generate-cli-skeleton` /
`aws bedrock-agentcore-control create-agent-runtime --generate-cli-skeleton` before writing code, rather
than guessing field names — worth doing for any AgentCore/Bedrock control-plane call, since these are
newer APIs not well covered by training data and the nesting is easy to get wrong (e.g.
`agentRuntimeArtifact.codeConfiguration.code.s3.{bucket,prefix}` + a required `runtime` enum + a required
`entryPoint` list — none of that is guessable from the starter's one-line TODO comment alone).

`python src/agent_orchestrator.py deploy` ran clean end-to-end: Guardrail `mnsou98agg5p` (v1), Runtime
`udacity_agentcore_runtime-fh9FZwA4FY` (PUBLIC/MCP, all 6 env vars incl. the real Task 5 KB IDs). Re-ran
`deploy` a second time to confirm both the guardrail and runtime short-circuits correctly reuse the
existing resources instead of erroring or duplicating. `test_agent.py task3` → 20/20.

**Unplanned resource:** Step 6/6 of the pre-written `deploy_all()` pipeline (`deploy_agentcore_gateway()`,
marked "pre-written — do not modify") also created a **real AgentCore Gateway**
(`novamart-support-3153d8d0`) — this isn't part of the graded rubric for this project, but it's a live
resource all the same (its 3 Lambda targets failed to register since no Lambda functions are deployed,
but the gateway shell itself exists and isn't free). Added to the teardown list in `PROJECT_PLAN.md` §16
— easy to miss since it's not one of the tasks being graded.

---

## L16 — ✅ Task 4 (AgentCore Memory) implemented; test-harness quirk: `task4` alone always fails

Implemented `configure_memory()`: `create_memory(name=memory_name, eventExpiryDuration=7,
memoryExecutionRoleArn=config.AGENTCORE_ROLE_ARN, memoryStrategies=[{'summaryMemoryStrategy': {'name':
'session_summary', 'namespaces': ['/summaries/{sessionId}']}}], clientToken=memory_name)`. Confirmed the
`namespaces` field's allowed placeholder tokens (`{actorId}`, `{sessionId}`, `{memoryStrategyId}`) via
`aws bedrock-agentcore-control create-memory help` before guessing a value.

Real resource created: `udacity_agentcore_memory-yX3G4HDqFe`. Took about 90 seconds to go from
`CREATING` to `ACTIVE` after the API call returned — a real backend provisioning delay, don't assume it's
instantly usable right after `create_memory()` returns if something downstream needs to read it back.

**Test-harness quirk (important, applies beyond just Task 4):** `python tests/test_agent.py task4` run
**in isolation** fails with `'BedrockAgentCore' object has no attribute 'get_agent_runtime'`, even though
the real memory resource is correctly created and `ACTIVE`. Root cause: `agent_orchestrator.py`'s
pre-written `_register_agentcore_compat_methods()` patch (which adds `get_agent_runtime` etc. to the raw
`bedrock-agentcore` boto3 client) only runs when the module is imported — and only `TestTask2.setUp` does
`import agent_orchestrator as ao`. `TestTask4.setUp` never imports it, so the client it builds is
unpatched. Running `task4` **after** `task2` in the same process (i.e. `python tests/test_agent.py all`,
which is also the real scoring command) works fine, because the patch is already registered globally by
then. **Lesson: never trust an individual `test_agent.py taskN` run for N ≥ 3 in isolation as proof of
failure — always re-check via `all` before concluding something is broken.** (Likely affects task3/task6
too, for the same reason, though not separately confirmed.)

---

## L17 — ⚠️ Task 6 (Observability): implemented correctly, but scores 0/20 — genuine API gap, not fixable from the code

Implemented `configure_observability()` exactly per the TODO: `agentcore_control.put_agent_runtime_logging_configuration(agentRuntimeId=..., loggingConfiguration={cloudWatchConfig: {...}, xRayConfig: {...}})`
wrapped in try/except with the exact fallback message the TODO specifies.

**The method genuinely does not exist**, confirmed two independent ways before concluding this wasn't
fixable by upgrading a package:
1. `boto3.client('bedrock-agentcore-control').meta.service_model.operation_names` — no operation with
   "Logging" or "Observ" in the name, on boto3 1.43.87 (the project's installed version, itself already
   fairly recent since `requirements.txt` only pins `boto3>=1.34.0` with no ceiling).
2. `aws bedrock-agentcore-control put-agent-runtime-logging-configuration help` on **AWS CLI v2 2.36.22**
   (a separately-bundled, independent botocore) → `Found invalid choice`. Same for the `get-*` variant.

Both SDKs — not just the project's pinned one — lack this operation entirely. This is exactly the
scenario the starter's own TODO comments warned about ("may not be available in all SDK versions") and
built a graceful-degradation path for. `test_agent.py`'s own `task6` tests call the identical missing
method directly with no fallback, so they score 0/20 regardless of what `configure_observability()` does
— this is a course-content/SDK-availability gap, not something to keep chasing from inside
`agent_orchestrator.py`. Real score ceiling in this environment: **100/120**, not 120/120, through no
fault of the implementation.

**Open question for M7:** the lesson's Task 6 page also asks for a live X-Ray Service Map screenshot
after running `python src/agent_orchestrator.py test`. That `test` mode calls the **local** Python
`Agent` objects directly (`orchestrator(prompt)`) — it never goes through `invoke_agent()` /
`invoke_agent_runtime()`, so it never actually executes inside the deployed AgentCore Runtime container.
Separately, the deployed runtime's `agentRuntimeArtifact` is a placeholder zip (`main.py` containing only
a comment — pre-written, not our real agent code) uploaded just to satisfy `create_agent_runtime`'s
required-artifact parameter, not a working MCP server. Whether Bedrock/Strands auto-emit X-Ray segments
for direct `Converse`/`Retrieve` calls made from a local script (independent of whether the runtime-level
logging config above ever got applied) is unverified — needs to actually try `test` mode and check the
X-Ray console before assuming either way.

---

## Environment facts (current)

| | |
|---|---|
| Mode | Local Windows 11, Git Bash + PowerShell, `uv` |
| AWS account | `187021010483` (personal), IAM user `udacity-agentcore-dev`, `AdministratorAccess`, permanent key (no session token) — see [[L11]] |
| Region | us-east-1 |
| Repo | working copy at `C:\WORKSPACES\AWS-UDACITY\P3-Multi-Agent_E-commerce_RAG`, currently on branch `dev/task-01` (see [[L13]] re: unexpected auto-commit/branch-switch); no git remote configured (starter files verified against upstream via `gh api`/`curl`, see L12) |
| `.env` | repo root, gitignored |
| Stack | `udacity-agentcore` — ✅ deployed 2026-09-12 on this account, `CREATE_COMPLETE`. **Real billable resources exist — see `PROJECT_PLAN.md` §16 for the full list + teardown steps.** |
| Data | seeded 2026-09-12: 4 customers, 15 orders, 6 policy docs |
| **Status** | Tasks 2/3/4/5 done (100/120). Task 6 ([[L17]]) code complete but scores 0/20 — real API gap in both boto3 and AWS CLI v2, not fixable from `agent_orchestrator.py`. **All TODOs in the file are now resolved** — remaining work is M7 (live 3-scenario proof + required X-Ray screenshot), whose feasibility is an open question per L17. |

> Superseded a stale copy of this table that still listed account `303688964032` (Academy lab) and
> "Blocked at Phase 0 / M0 step 0.3" — that was accurate mid-L7 but never updated after the L9 teardown
> and L11 account switch. Kept the correction here rather than silently rewriting history.
