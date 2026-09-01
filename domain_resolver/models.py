from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BrandContext:
    brand: str
    category: str = ""
    subcategory: str = ""
    monthly_revenue: str = ""
    total_ad_spend: str = ""
    placement_gap: str = ""
    heavy_advertiser: str = ""
    video_intent: str = ""
    multi_format: str = ""
    high_ad_spend_ratio: str = ""
    primary_campaign: str = ""


@dataclass
class CandidateDomain:
    domain: str
    source: str
    evidence: List[str] = field(default_factory=list)
    score: int = 0
    reason: str = ""
    signals: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    final_domain: str = ""


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
