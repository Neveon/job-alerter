from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Dict, Set
from models import Job


def load_blacklist(path: str = "config/blacklist.txt") -> Set[str]:
    """
    Load blacklist (one company per line). Case-insensitive, ignores blanks/# comments.
    """
    p = Path(path)
    if not p.exists():
        print(f"Warning: blacklist file not found: {path}")
        return []
    lines = [ln.strip() for ln in p.read_text().splitlines()]
    return set(ln.lower() for ln in lines if ln and not ln.startswith("#"))


def _is_blocked(name: str, blacklist: Iterable[str]) -> bool:
    """
    Block if any blacklist token is a case-insensitive substring of the company name.
    Ex: "block" blocks "Block", "Block Inc.", etc.
    """
    ln = name.lower()
    return any(token in ln for token in blacklist)


def filter_companies(companies: List[str], blacklist: Set[str]) -> List[str]:
    """Preserve original order; drop blacklisted names."""
    out = []
    for c in companies:
        if not _is_blocked(c, blacklist):
            out.append(c)
    return out


def filter_job_companies(companies: List[Job], blacklist: Set[str]) -> List[Job]:
    """Preserve original order; drop blacklisted names."""
    return [c for c in companies if not _is_blocked(c.company, blacklist)]


def filter_rows(rows: List[Dict], blacklist: List[str]) -> List[Dict]:
    """Drop rows whose company is blacklisted; preserve order."""
    return [r for r in rows if not _is_blocked(r.get("company", ""), blacklist)]


def matches_role_title(
    job: Job, include_titles: List[str], exclude_titles: List[str]
) -> bool:
    """
    Check if job title matches role title rules.
    Must match at least one include title and none of the exclude titles.
    """
    job_title = job.title.lower()

    # Must match at least one include title
    if include_titles:
        if not any(title.lower() in job_title for title in include_titles):
            return False

    # Must not match any exclude titles
    if exclude_titles:
        if any(title.lower() in job_title for title in exclude_titles):
            return False

    return True


def matches_job_description(
    job: Job, include_descriptions: List[str], exclude_descriptions: List[str]
) -> bool:
    """
    Check if job description matches description rules.
    Must match at least one include description and none of the exclude descriptions.
    """
    # Use actual job description if available, otherwise fall back to title + company
    if job.description:
        job_text = job.description.lower()
    else:
        job_text = f"{job.title} {job.company}".lower()

    # Must match at least one include description
    if include_descriptions:
        if not any(desc.lower() in job_text for desc in include_descriptions):
            return False

    # Must not match any exclude descriptions
    if exclude_descriptions:
        if any(desc.lower() in job_text for desc in exclude_descriptions):
            return False

    return True


def matches_location(
    job: Job, include_locations: List[str], exclude_locations: List[str]
) -> bool:
    """
    Check if job matches location rules.
    Must match at least one include location and none of the exclude locations.
    """
    job_location = job.location.lower()

    # Must match at least one include location
    if include_locations:
        if not any(location.lower() in job_location for location in include_locations):
            return False

    # Must not match any exclude locations
    if exclude_locations:
        if any(location.lower() in job_location for location in exclude_locations):
            return False

    return True


def filter_jobs(jobs: List[Job], rules: Dict) -> List[Job]:
    """
    Filter jobs based on rules.yaml configuration.
    Applies role title, job description, and location filters.
    """
    role_titles = rules.get("role_titles", {})
    job_descriptions = rules.get("job_descriptions", {})
    locations = rules.get("locations", {})

    include_titles = role_titles.get("include_any", [])
    exclude_titles = role_titles.get("exclude_any", [])
    include_descriptions = job_descriptions.get("include_any", [])
    exclude_descriptions = job_descriptions.get("exclude_any", [])
    include_locations = locations.get("include_any", [])
    exclude_locations = locations.get("exclude_any", [])

    filtered_jobs = []
    for job in jobs:
        if (
            matches_role_title(job, include_titles, exclude_titles)
            and matches_job_description(job, include_descriptions, exclude_descriptions)
            and matches_location(job, include_locations, exclude_locations)
        ):
            filtered_jobs.append(job)

    return filtered_jobs


def deduplicate_jobs(jobs: List[Job]) -> List[Job]:
    """Remove duplicate jobs based on URL."""
    seen_urls = set()
    unique_jobs = []
    for job in jobs:
        if job.url and job.url not in seen_urls:
            seen_urls.add(job.url)
            unique_jobs.append(job)
    return unique_jobs
