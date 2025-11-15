from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SalaryRange:
    # Future-proof: leave currency & periodicity here though we won't compute now.
    min: Optional[int] = None  # annualized USD if available; else None
    max: Optional[int] = None
    currency: str = "USD"
    periodicity: str = "year"  # "year" | "hour" | etc. (future: normalize)


@dataclass(frozen=True)
class Job:
    title: str
    company: str
    location: str
    url: str
    source: str  # "indeed", etc.
    listed_at: Optional[str] = None  # ISO or site string as given
    salary: SalaryRange = SalaryRange()
    description: Optional[str] = None  # Full job description from JobSpy
    # For dedupe later; keep a stable id candidate (url is fine for now)
    req_id: Optional[str] = None
