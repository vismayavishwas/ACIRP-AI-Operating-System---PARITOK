from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from datetime import datetime


class PrunedChunk(BaseModel):
    content: str
    # e.g., "Duplicate timeline event", "Low relevance (<0.30)", "Outdated ticket log", "Repeated system prompt metadata"
    reason: str
    tokens_saved: int


class ParitokMetrics(BaseModel):
    original_tokens: int
    optimized_tokens: int
    tokens_saved: int
    savings_percentage: float
    cost_saved_usd: float
    efficiency_score: int = Field(description="Dynamic efficiency score between 0 and 100")
    documents_retrieved: int = 1
    documents_discarded: int = 0
    context_retained_pct: float = 100.0
    compression_ratio: float = 1.0
    optimizer_source: Literal["PARITOK_HOSTED_API", "LOCAL_FALLBACK_OPTIMIZER"] = "LOCAL_FALLBACK_OPTIMIZER"
    pruned_chunks: List[PrunedChunk] = []
    original_prompt: Optional[str] = None
    optimized_prompt: Optional[str] = None


class TimelineEvent(BaseModel):
    timestamp: str
    stage: Literal["PERCEPTION", "PLANNER", "TOOL", "MONITOR", "VERIFY", "ESCALATION", "SYSTEM", "PETITION"]

    decision: str
    confidence: str
    reason: str
    next_action: str
    paritok_metrics: Optional[ParitokMetrics] = None


class Strategy(BaseModel):
    name: str
    department: str
    sla_hours: int
    escalation_path: List[str]


class PlannerDecision(BaseModel):
    goal: str
    current_state: str
    chosen_strategy: Strategy
    reason: str
    next_action: str
    requires_human: bool
    confidence: float
    paritok_metrics: Optional[ParitokMetrics] = None


class Incident(BaseModel):
    id: str
    status: Literal[
        "DETECTED", "AWAITING_REUPLOAD", "PLANNED", "SUBMITTED",
        "MONITORING", "VERIFYING", "ESCALATED", "CLOSED"
    ]
    goal: str = ""
    complainant_name: str = "Anonymous Citizen"
    issue_type: Optional[Literal["pothole", "fallen_tree", "garbage"]] = None
    severity: Optional[Literal["low", "medium", "high"]] = None
    confidence: Optional[float] = None
    latitude: float
    longitude: float
    image_before_url: str
    image_after_url: Optional[str] = None
    official_token: Optional[str] = None
    current_strategy: Optional[Strategy] = None
    sla_deadline: Optional[str] = None
    escalation_level: int = 0
    timeline: List[TimelineEvent] = []
    paritok_metrics: Optional[ParitokMetrics] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
