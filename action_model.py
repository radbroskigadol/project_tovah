"""
TOVAH v14 kernel/action_model.py — Typed action, ecology, and proposal objects.

Canonical schemas for planning, tool use, kernel ecology, and self-modification.
Prevents drift into ad-hoc dicts while remaining serializable.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from tovah_v14.core.primitives import BilateralValue


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class _SerializableDataclass:
    """Small mixin for packet/model payload friendliness."""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Goal(_SerializableDataclass):
    """A kernel goal with typed fields."""

    goal: str
    function_spec: str = ""
    domain: str = ""
    reasoning: str = ""
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    bilateral_confidence: BilateralValue = field(
        default_factory=lambda: BilateralValue(0.5, 0.1)
    )


@dataclass
class PlanStep(_SerializableDataclass):
    """One step in a strategic plan."""

    action: str  # "research", "tool_use", "patch", "test", "review"
    target: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, active, completed, failed, skipped
    result: Optional[Dict[str, Any]] = None


@dataclass
class ToolIntent(_SerializableDataclass):
    """A declared intent to use a tool."""

    tool: str
    query: str = ""
    arg: str = ""
    arg2: str = ""
    rationale: str = ""
    expected_outcome: str = ""


@dataclass
class ExecutionResult(_SerializableDataclass):
    """Result of executing a plan step or tool action."""

    ok: bool
    action: str
    summary: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    bilateral_assessment: BilateralValue = field(
        default_factory=lambda: BilateralValue(0.5, 0.5)
    )
    duration_ms: int = 0


@dataclass
class ReflectionNote(_SerializableDataclass):
    """A kernel reflection on its own performance or state."""

    topic: str
    observation: str
    confidence: BilateralValue = field(default_factory=lambda: BilateralValue(0.5, 0.5))
    timestamp: float = field(default_factory=time.time)
    source: str = ""  # "self_assess", "advisor", "test_result", "manual"


@dataclass
class PatchProposal(_SerializableDataclass):
    """A typed patch proposal for the approval-gated lane."""

    patch_name: str
    target: str
    code: str
    rationale: str
    source: str = "autonomous"
    risk_level: str = "low"  # low, medium, high
    risk_notes: str = ""
    expected_state_changes: List[str] = field(default_factory=list)
    approval_required: bool = True
    preflight_passed: bool = False


@dataclass
class ApprovalRequest(_SerializableDataclass):
    """Request for human approval of a kernel action."""

    request_id: str
    action_type: str  # "patch", "account", "service", "install"
    description: str
    risk_level: str = "medium"
    rationale: str = ""
    timestamp: float = field(default_factory=time.time)
    approved: Optional[bool] = None
    approved_at: Optional[float] = None


# ============================================================
# Kernel-ecology foundation
# ============================================================


@dataclass
class KernelIdentityRef(_SerializableDataclass):
    """Typed identity record for sovereign, hub, or subkernel actors."""

    kernel_id: str
    role: str = "main"
    lifecycle: str = "born"
    parent_kernel_id: str = ""
    mission_context: str = ""
    trust_level: str = "provisional"
    authoritative_state: bool = False
    can_promote: bool = False
    notes: str = ""


@dataclass
class GoalLineage(_SerializableDataclass):
    """Parent/child genealogy for delegated or branched goals."""

    goal_id: str
    parent_goal_id: str = ""
    root_goal_id: str = ""
    mission_context: str = ""
    owner_kernel_id: str = ""
    requester_kernel_id: str = ""
    lease_scope: str = "local"
    lease_expires_at: Optional[float] = None
    provenance: List[str] = field(default_factory=list)


@dataclass
class BlockedGrowthRecord(_SerializableDataclass):
    """Typed record for failures that require governance or more resources."""

    record_id: str = field(default_factory=lambda: _id("blocked"))
    kernel_id: str = ""
    blocker: str = ""
    symptom: str = ""
    attempted_action: str = ""
    required_resource: str = ""
    recommended_action: str = ""
    severity: str = "medium"
    timestamp: float = field(default_factory=time.time)


@dataclass
class ResourceRequest(_SerializableDataclass):
    """Request for budget, memory, or other quantitative resources."""

    request_id: str = field(default_factory=lambda: _id("resource"))
    requester_kernel_id: str = ""
    resource_kind: str = ""
    amount: float = 0.0
    rationale: str = ""
    parent_goal_id: str = ""
    duration_hint: str = ""
    budget_name: str = ""
    priority: int = 0
    risk_class: str = "low"


@dataclass
class ToolAccessRequest(_SerializableDataclass):
    """Request for temporary or persistent tool rights."""

    request_id: str = field(default_factory=lambda: _id("tool"))
    requester_kernel_id: str = ""
    tool_name: str = ""
    rationale: str = ""
    parent_goal_id: str = ""
    desired_scope: str = "branch_local"
    desired_duration: str = "session"
    priority: int = 0
    risk_class: str = "medium"


@dataclass
class ModuleProposal(_SerializableDataclass):
    """Proposal to create or promote a module into a governed lane."""

    proposal_id: str = field(default_factory=lambda: _id("module"))
    proposer_kernel_id: str = ""
    module_name: str = ""
    module_kind: str = ""
    target_role: str = "hub"
    rationale: str = ""
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    risk_class: str = "medium"
    promotion_target: str = "hub"
    requires_approval: bool = True


@dataclass
class PromotionRequest(_SerializableDataclass):
    """Request to move an artifact upward in the trust/promotion ladder."""

    request_id: str = field(default_factory=lambda: _id("promote"))
    requester_kernel_id: str = ""
    artifact_kind: str = ""
    artifact_name: str = ""
    current_stage: str = "proposed"
    desired_stage: str = "promotable"
    target_kernel_id: str = "main"
    rationale: str = ""
    evidence: List[str] = field(default_factory=list)
    risk_class: str = "medium"


@dataclass
class SpawnRequest(_SerializableDataclass):
    """Request to instantiate a specialized child kernel."""

    request_id: str = field(default_factory=lambda: _id("spawn"))
    requester_kernel_id: str = ""
    child_kernel_id: str = ""
    requested_role: str = "subkernel"
    specialization: str = ""
    mission_context: str = ""
    parent_goal_id: str = ""
    resource_profile: str = ""
    rationale: str = ""
    risk_class: str = "medium"


@dataclass
class MemorySyncRequest(_SerializableDataclass):
    """Request to discard, summarize, or promote branch memory."""

    request_id: str = field(default_factory=lambda: _id("memory"))
    requester_kernel_id: str = ""
    target_kernel_id: str = "main"
    sync_mode: str = "summarize"  # discard, summarize, promote
    memory_kinds: List[str] = field(default_factory=list)
    rationale: str = ""
    include_provenance: bool = True
    parent_goal_id: str = ""


@dataclass
class TrustReport(_SerializableDataclass):
    """Governance-facing trust assessment for a branch or child kernel."""

    report_id: str = field(default_factory=lambda: _id("trust"))
    subject_kernel_id: str = ""
    reporter_kernel_id: str = ""
    trust_level: str = "provisional"
    stability_score: float = 0.0
    concerns: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    recommended_action: str = "monitor"
    timestamp: float = field(default_factory=time.time)
