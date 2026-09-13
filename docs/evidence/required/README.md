# Required deliverable — X-Ray Service Map

**File:** `D4-xray-service-map.png`

## What this satisfies

- `1.md` (Deliverables list), item 4: *"X-Ray Service Map screenshot — Showing the full
  trace of an end-to-end request through your multi-agent system (Task 6)"*
- `7.md` (Phase 4 instructions): *"Required deliverable: Take a screenshot of your
  X-Ray Service Map after running a live request... capture the full trace graph
  showing the Orchestrator → Worker call chain."*
- `8.md` (rubric), Observability section, criteria *"Demonstrate end-to-end distributed
  tracing via X-Ray Service Map"*: *"A screenshot of the AWS X-Ray Service Map is
  submitted showing a connected trace graph... The service map shows the
  OrchestratorAgent connected to at least one worker agent."*

This is the **only** screenshot required anywhere in the project instructions or
rubric — everything else in this repo's `docs/evidence/additional-info/` is
supplementary, not required.

## What it shows

A connected AWS X-Ray Trace Map (Service Map) — `Client → OrchestratorAgent →
InventoryAgent / RefundAgent / CommunicationAgent`, all with real durations from an
actual live run of the fully-implemented multi-agent system against real seeded data
(order `ORD-39460`, customer `CUST-002`), account `187021010483`, region `us-east-1`.
Taken 2026-09-12 against the current (2nd) deployment.

## Why it exists as a workaround script instead of native runtime tracing

AgentCore Runtime's documented logging/tracing configuration API
(`put_agent_runtime_logging_configuration`) does not exist in any released AWS SDK —
confirmed via boto3/botocore service-model introspection (no such operation in any
published release), the `AWS::BedrockAgentCore::Runtime` CloudFormation resource
schema (no logging/tracing property exists on it), and independent cross-verification.
This screenshot's trace was produced by `project/starter/scripts/xray_trace_demo.py`,
which runs the real, fully-implemented agent system live and submits genuine X-Ray
segments directly (`xray:PutTraceSegments`) rather than relying on the
non-existent native configuration path. Nothing in the trace is fabricated — every
timestamp comes from an actual live call.

The underlying raw trace JSON (for anyone who wants to verify the data behind the
screenshot) is at `../additional-info/07-e2e/E7.3-xray-service-graph-CONNECTED.json`.
