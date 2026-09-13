# Required deliverable — X-Ray Service Map

![X-Ray Service Map showing OrchestratorAgent connected to InventoryAgent, RefundAgent, and CommunicationAgent](D4-xray-service-map.png)

This is `D4-xray-service-map.png` — a connected AWS X-Ray Trace Map (what the console calls a Service Map) from a real, live run of the fully-implemented multi-agent system. `Client → OrchestratorAgent → InventoryAgent / RefundAgent / CommunicationAgent`, each edge carrying a real duration from an actual request (order `ORD-39460`, customer `CUST-002`), captured against account `187021010483` in `us-east-1`.

## Why this is the only file in this folder

The project's instructions and rubric ask for exactly one piece of visual evidence, worded the same way in both places:

> *"Required deliverable: Take a screenshot of your X-Ray Service Map after
> running a live request... capture the full trace graph showing the
> Orchestrator → Worker call chain."*

and, in the rubric itself, under Observability:

> *"A screenshot of the AWS X-Ray Service Map is submitted showing a connected
> trace graph... The service map shows the OrchestratorAgent connected to at
> least one worker agent."*

Everything else collected while building this project — score records, deploy logs, extra console screenshots — lives one level up in [`../additional-info/`](../additional-info/) instead, so this folder stays exactly what a reviewer needs and nothing more.

## How the trace behind it was produced

AgentCore Runtime's documented tracing API, `put_agent_runtime_logging_configuration`, doesn't exist in any released AWS SDK — checked directly against the live boto3/botocore service model (no such operation in any published version) and against the `AWS::BedrockAgentCore::Runtime` CloudFormation resource schema (no logging/tracing property on it at all). Rather than leave the tracing requirement unmet, [`project/starter/scripts/xray_trace_demo.py`](../../project/starter/scripts/xray_trace_demo.py) runs the real, fully-implemented agent system live and submits genuine X-Ray segments directly via `xray:PutTraceSegments`. Every timestamp in the trace comes from an actual call — nothing here is staged or fabricated.

If you want to inspect the raw data behind the screenshot rather than just the picture, it's saved as JSON at [`../additional-info/07-e2e/E7.3-xray-service-graph-CONNECTED.json`](../additional-info/07-e2e/E7.3-xray-service-graph-CONNECTED.json).
