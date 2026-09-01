from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CandidateDomain:
    domain: str
    source: str
    evidence: List[str] = field(default_factory=list)
    score: int = 0
    reason: str = ""


@dataclass
class ResolutionResult:
    brand: str
    domain: Optional[str]
    company_name: Optional[str]
    confidence: int
    status: str
    source: Optional[str]
    reason: str
    evidence_urls: List[str] = field(default_factory=list)
    candidates: List[CandidateDomain] = field(default_factory=list)
