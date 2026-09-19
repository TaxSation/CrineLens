"""
CrimeLens Pydantic Models & Typed Schemas
Defines core domain models, evidence classes, and API contracts.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceClass(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    REPORTED = "REPORTED"


class FindingType(str, Enum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"


class PriorityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EntityType(str, Enum):
    PERSON = "person"
    PHONE = "phone"
    VEHICLE = "vehicle"
    LOCATION = "location"
    ACCOUNT = "account"
    ORGANIZATION = "organization"
    CASE = "case"
    FIR = "fir"
    EVENT = "event"
    DOCUMENT = "document"
    SOCIAL_POST = "social_post"


class EdgeProvenance(BaseModel):
    source_record_id: str
    source_type: str
    timestamp: Optional[str] = None
    evidence_class: EvidenceClass = EvidenceClass.OBSERVED
    confidence: float = 1.0
    reliability: float = 1.0
    context: Optional[str] = None


class EntityNode(BaseModel):
    id: str
    name: str
    type: EntityType
    community_id: Optional[int] = None
    is_bridge: bool = False
    priority: PriorityLevel = PriorityLevel.LOW
    priority_score: float = 0.0
    priority_reason: str = ""
    alias_of: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    centrality: Dict[str, float] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    timestamp: Optional[str] = None
    provenance: EdgeProvenance


class CaseSummary(BaseModel):
    case_id: str
    case_type: str
    incident_date: str
    primary_location: str
    status: str
    title: str
    description: str
    entity_count: int
    relationship_count: int
    evidence_count: int
    anomalies_count: int
    contradictions_count: int


class AnomalyItem(BaseModel):
    id: str
    type: str
    title: str
    entity_ids: List[str]
    timestamp: str
    severity: str
    description: str
    evidence_records: List[str]
    finding_type: FindingType = FindingType.INFERENCE


class ContradictionItem(BaseModel):
    id: str
    title: str
    entity_id: str
    entity_name: str
    claim_a: Dict[str, Any]
    claim_b: Dict[str, Any]
    status: str = "UNRESOLVED CONFLICT"
    finding_type: FindingType = FindingType.INFERENCE


class HiddenLinkItem(BaseModel):
    id: str
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    score: float
    reasons: List[str]
    supporting_signals: Dict[str, Any]
    finding_type: FindingType = FindingType.INFERENCE


class PriorityLead(BaseModel):
    entity_id: str
    name: str
    role_or_occupation: str
    priority: PriorityLevel
    priority_score: float
    reason: str
    network_role: str
    signals: List[str]
    suggested_action: str
    finding_type: FindingType = FindingType.RECOMMENDATION
