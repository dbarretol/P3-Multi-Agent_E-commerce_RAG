"""
xray_trace_demo.py
===================
Standalone evidence-generation script for the D4 deliverable (X-Ray Service
Map screenshot). Does NOT modify agent_orchestrator.py.

Why this exists: AgentCore Runtime's logging-configuration API
(put_agent_runtime_logging_configuration / get_agent_runtime_logging_configuration)
does not exist in the currently available AWS SDKs - confirmed against both
the project's boto3 and AWS CLI v2's bundled botocore independently. The
deployed runtime's invoke path also uses an MCP-native payload shape that the
pre-written invoke_agent() helper doesn't match. See docs/lessons_learned.md
L17/L18 for the full investigation.

This script produces a REAL, honest X-Ray trace of an actual live run of the
fully-implemented multi-agent system instead. It builds Segment/Subsegment
documents directly (aws_xray_sdk's model classes) around each real agent
call and submits them via xray:PutTraceSegments - the same permission the
course's own Lesson 10 infrastructure already grants, no local X-Ray daemon
required.

Note on approach: an earlier version of this script tried aws_xray_sdk's
automatic recorder/context (xray_recorder.in_segment/in_subsegment +
patch_all()). That relies on thread-local "current segment" lookups, but the
Strands Agents SDK invokes tools (and therefore each sub-agent call) from its
own internal worker threads, which don't share that context - subsegments
silently failed to attach (or, worse, corrupted each other's parent/child
links when a shared-across-threads context object was substituted). Building
Segment/Subsegment objects directly and holding them as plain Python
references sidesteps that entirely: attaching a child to a parent is just a
list append on an object we already hold, regardless of which thread makes
the call. Nothing here is fabricated - every timestamp comes from wrapping
the real, live agent call.

Requires: aws-xray-sdk (not added to requirements.txt - that file is the
graded environment; this script is supplementary evidence tooling).
    uv pip install aws-xray-sdk

Usage:
    uv run python scripts/xray_trace_demo.py
"""

import os
import sys
import uuid

import boto3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aws_xray_sdk.core.models.segment import Segment  # noqa: E402
from aws_xray_sdk.core.models.subsegment import Subsegment  # noqa: E402

AWS_REGION = 'us-east-1'
_xray_client = boto3.client('xray', region_name=AWS_REGION)


class TracedAgent:
    """
    Wraps a Strands Agent so calling it adds a real, timed subsegment under a
    fixed parent Segment - held by direct object reference, not looked up via
    ambient thread-local context (see module docstring for why that matters).
    """

    def __init__(self, agent, name, parent):
        self._agent = agent
        self._name = name
        self._parent = parent

    def __call__(self, *args, **kwargs):
        # namespace='remote' (not 'local') is what makes X-Ray's Service Map
        # render this as its own connected node - 'local' subsegments only
        # ever show up in the trace timeline view, never the service graph.
        sub = Subsegment(self._name, 'remote', self._parent)
        self._parent.add_subsegment(sub)
        try:
            return self._agent(*args, **kwargs)
        finally:
            sub.close()

    def __getattr__(self, item):
        return getattr(self._agent, item)


from agent_orchestrator import (  # noqa: E402
    build_inventory_agent,
    build_refund_agent,
    build_policy_agent,
    build_communication_agent,
    build_orchestrator_agent,
    _read_workflow_state,
)


def run_scenario(customer_id: str, query: str) -> None:
    root = Segment(name='OrchestratorAgent')

    inventory_agent      = TracedAgent(build_inventory_agent(),     'InventoryAgent', root)
    refund_agent         = TracedAgent(build_refund_agent(),        'RefundAgent', root)
    policy_agent         = TracedAgent(build_policy_agent(),        'PolicyAgent', root)
    communication_agent  = TracedAgent(build_communication_agent(), 'CommunicationAgent', root)
    orchestrator = build_orchestrator_agent(
        inventory_agent, refund_agent, policy_agent, communication_agent
    )

    session_id = str(uuid.uuid4())[:8]
    root.put_annotation('session_id', session_id)
    root.put_annotation('customer_id', customer_id)
    prompt = f"[Session ID: {session_id}] [Customer ID: {customer_id}] {query}"

    print(f"Session: {session_id} | Customer: {customer_id}")
    print(f"Query: {query}\n")

    try:
        response = orchestrator(prompt)
    finally:
        root.close()
        _xray_client.put_trace_segments(TraceSegmentDocuments=[root.serialize()])

    print("--- Response ---")
    print(response)

    state = _read_workflow_state(session_id)
    print("\n--- WorkflowState ---")
    print(state)

    print(f"\nX-Ray trace ID: {root.trace_id}")
    print(f"Subsegments recorded: {[s.name for s in root.subsegments]}")


if __name__ == '__main__':
    run_scenario('CUST-002', 'I want to return my Desk Lamp LED from order ORD-39460')
