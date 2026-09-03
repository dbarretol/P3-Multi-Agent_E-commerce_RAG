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

---

## Environment facts (this run)

| | |
|---|---|
| Mode | Local Windows 11, Git Bash + PowerShell, `uv` |
| AWS account | `303688964032` — AWS Academy learner lab (`voclabs` role) |
| Region | us-east-1 |
| Repo | full clone of `udacity/cd14764-aws-agentic-c3-classroom` at repo root; work in `project/starter/` |
| `.env` | repo root, gitignored |
| Stack | `udacity-agentcore` deployed by us (not pre-provisioned) → `CREATE_COMPLETE` |
| Data | 4 customers, 15 orders, 6 S3 policy docs seeded |
| **Status** | **Blocked at Phase 0 / M0 step 0.3** — Bedrock Claude access (L7). Everything else green. |
