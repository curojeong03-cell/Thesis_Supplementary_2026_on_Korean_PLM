# Table S5. Trigger Retention under the 128-Token Input Limit

| Condition | Scope | Evaluation inputs | Inputs truncated | Triggers lost | Fully retained (%) |
| --- | --- | --- | --- | --- | --- |
| A | AI-Hub, common candidates, evaluation seed 42 | 28,000 | 14 | 10 | 99.9643 |
| B | AI-Hub, common candidates, evaluation seed 42 | 28,000 | 14 | 10 | 99.9643 |
| C | AI-Hub, per-trigger candidates, evaluation seed 42 | 28,000 | 3 | 1 | 99.9964 |
| D | NSMC, positive target, seed 42, stored 0.10% run input pairs | 11,564 | 0 | 0 | 100.0000 |

Inputs are aggregated across triggers. The audit covers saved evaluation inputs. NSMC coverage is restricted to the audited positive-target, seed 42 files. KoELECTRA used the published vocabulary and tokenizer configuration for the recorded model.
