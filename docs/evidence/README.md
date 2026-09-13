# Evidence directory

This folder is split in two, so a reviewer can find the one thing the rubric actually
asks for without wading through our own internal verification notes.

## `required/`

Contains **only** the one deliverable the project rubric and lesson instructions
explicitly ask for as a screenshot:

> *"Required deliverable: Take a screenshot of your X-Ray Service Map after running a
> live request... capture the full trace graph showing the Orchestrator → Worker call
> chain."* — Phase 4 instructions, matched verbatim in the rubric's Observability
> section and in the project's deliverables list.

See `required/README.md` for exactly what it shows and how it was produced.

## `additional-info/`

Everything else: our own internal test-run snapshots, score records, implementation
diffs, and supplementary console screenshots collected while building and verifying
this project. **None of it is required by the rubric** — it's our own audit trail, plus
supporting context for a course-bug report we filed: the automated
`test_agent.py task6` check calls an AWS SDK method
(`put_agent_runtime_logging_configuration`) that has never existed in any released
boto3/botocore version, confirmed via service-model introspection, the
`AWS::BedrockAgentCore::Runtime` CloudFormation schema, and independent
cross-verification.

**Resource-ID note:** most of the `.txt`/`.diff` snapshots in `additional-info/` were
captured against the project's **first** deployment (resource suffix `3153d8d0`).
That deployment was torn down and redeployed the same day (resource suffix `5b82cc40`)
to pause work without incurring ongoing AWS charges. The snapshots still accurately
prove each task was implemented and passed at the time they were taken, but their
specific IDs/ARNs won't match the **current** live resources — check `.env` for those.
The one exception is `07-e2e/E7.3-xray-service-graph-CONNECTED.json` and everything in
`additional-info/screenshots/`, which were regenerated against the current (2nd)
deployment and do match `.env` as of this writing.
