# Required deliverable — X-Ray Service Map

> **Pending.** The screenshot goes here once the current redeploy is verified.
> It needs to be taken manually from the AWS Console (X-Ray → Service map /
> Traces → Service map) after running `python src/agent_orchestrator.py test`
> against the live deployment.

What this screenshot needs to show, per the rubric:

> "A screenshot of the AWS X-Ray Service Map is submitted showing a connected
> trace graph... The service map shows the OrchestratorAgent connected to at
> least one worker agent."

This time, since the real observability fix traces every routing tool and
every Knowledge Base retrieval, the graph should show more than the bare
minimum: `NovaMart-Orchestrator` connected to `InventoryAgent`, `RefundAgent`,
`CommunicationAgent`, and `PolicyAgent` — with `PolicyAgent` itself connected to
`KnowledgeBase:returns`, `KnowledgeBase:shipping`, and `KnowledgeBase:warranty`.
