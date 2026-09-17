# Test scores

Captured terminal output of `python tests/test_agent.py <task>`, run
2026-09-16 against the live deployment (4th redeploy, suffix `a29f01a0`,
new KB IDs `NWLWTRHQMK`/`DBXGPHVIN9`/`TQHKJ83VJW`, superseding the 3rd
redeploy's now-torn-down resources). Real, verified result:
**120/120 (100%)** across all tasks.

| File | Command | Score |
|---|---|---|
| `task2.txt` | `python tests/test_agent.py task2` | 40/40 |
| `task3.txt` | `python tests/test_agent.py task3` | 20/20 |
| `task4.txt` | `python tests/test_agent.py task4` | 15/15 |
| `task5.txt` | `python tests/test_agent.py task5` | 25/25 |
| `task6.txt` | `python tests/test_agent.py task6` | 20/20 |
| `all.txt`   | `python tests/test_agent.py all` (final score) | 120/120 |
