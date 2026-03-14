# TOVAH v14 — Kernel Action Model

**Canonical schemas for the sovereign kernel ecology.**

This file defines every typed object the kernel uses for:
- Goals & plans
- Tool intents & execution results
- Patch & module proposals
- Promotion requests
- Goal lineage & trust reports
- Blocked growth & resource requests
- Kernel identity & spawning

All objects are fully serializable, bilateral-value aware, and designed to prevent drift into ad-hoc dictionaries — exactly as required by the [UAP Gödel Obstruction Series](https://zenodo.org/records/19016200).

```python
# Example from action_model.py
@dataclass
class PromotionRequest(_SerializableDataclass):
    request_id: str
    requester_kernel_id: str
    artifact_kind: str          # "patch" | "module"
    artifact_name: str
    desired_stage: str
    target_kernel_id: str = "main"
    evidence: List[str] = field(default_factory=list)
    risk_class: str = "medium"
