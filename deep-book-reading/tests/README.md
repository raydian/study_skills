# Skill tests

The suite has two layers:

1. `test_skill_contract.py` verifies the meta-skill contains required structure, PASS routing, terminology, and no scaffold placeholders.
2. `test_validate_package.py` exercises the deterministic output-package validator with valid and deliberately invalid packages.

`cases/` contains forward-test prompts/rubrics for realistic agent behavior. Score each case as pass only when every stated condition is met; partial compliance is a failure for the targeted invariant.

`baseline/` records the RED phase performed before the Skill was written. The baseline was strong on causal caution and figure use but omitted the systematic contract needed for stable locator IDs, canonical knowledge taxonomy, claim IDs, full provenance, ledgers, and PASS state.

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

For a real forward test, give an agent only the relevant case fixture and the Skill path. Do not reveal the expected diagnosis; inspect its emitted package against the case conditions and validator.
