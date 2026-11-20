# SkillEvaluator BYOT Harbor Tasks

This directory is user-owned. SkillEvaluator stages copies under eval
results and does not mutate these source files in place.

Keep the result contract stable:

- trajectory path: `/logs/agent/trajectory.json`
- reward JSON: `/logs/verifier/reward.json`
- reward text: `/logs/verifier/reward.txt`
- score range: `0.0` to `1.0`
- case IDs should match `evals/evals.json` when using `default` or `default_plus_custom`
