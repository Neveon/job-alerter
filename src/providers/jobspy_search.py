from __future__ import annotations
from typing import Iterable, List
import pandas as pd
from jobspy import scrape_jobs
from models import Job, SalaryRange


def _coerce_int(x):
    try:
        return int(x) if x is not None and str(x).strip() != "" else None
    except Exception:
        return None


def _df_to_jobs(df: pd.DataFrame, source_site: str) -> List[Job]:
    jobs: List[Job] = []
    if df is None or df.empty:
        return jobs

    # JobSpy common columns (as of writing):
    # title, company, location, job_url, date_posted, is_remote,
    # salary_min, salary_max, salary_period, salary_currency, description
    for _, row in df.iterrows():
        salary = SalaryRange(
            min=_coerce_int(row.get("salary_min")),
            max=_coerce_int(row.get("salary_max")),
            currency=(row.get("salary_currency") or "USD") or "USD",
            periodicity=(row.get("salary_period") or "year") or "year",
        )
        jobs.append(
            Job(
                title=str(row.get("title") or "").strip(),
                company=str(row.get("company") or "").strip(),
                location=str(row.get("location") or "").strip(),
                url=str(row.get("job_url") or "").strip(),
                source=source_site,
                listed_at=(row.get("date_posted") or None),
                salary=salary,
                description=(row.get("description") or "").strip() or None,
                req_id=str(row.get("job_url") or "").strip() or None,
            )
        )
    return jobs


def search_company_roles(
    site: str,
    company: str,
    role_terms: Iterable[str],
    *,
    location: str,
    radius_miles: int = 50,
    results_wanted: int = 50,
    hours_old: int = 168,
) -> List[Job]:
    """
    Search roles for a specific company using JobSpy.
    Strategy: run one search per role term with a 'company' filter where possible.
    Indeed does not expose a clean company-only param, so we include company in search term.
    """
    jobs: List[Job] = []
    for term in role_terms:
        # Include company name in the search query to bias results
        query = f"{term} {company}"
        df = scrape_jobs(
            site_name=site,
            search_term=query,
            location=location,
            results_wanted=int(results_wanted),
            hours_old=int(hours_old),
            distance=int(radius_miles),
            country_indeed="USA",  # Adjust if outside US
            verbose=False,
        )
        jobs.extend(_df_to_jobs(df, site))
    return jobs


def search_by_query(
    site: str,
    role_terms: str,
    location: str,
    radius_miles: int = 50,
    results_wanted: int = 50,
    hours_old: int = 168,
) -> List[Job]:
    """
    Broad search (secondary list) independent of the Levels companies.
    """
    jobs: List[Job] = []
    for term in role_terms:
        df = scrape_jobs(
            site_name=site,
            search_term=term,
            location=location,
            results_wanted=int(results_wanted),
            hours_old=int(hours_old),
            distance=int(radius_miles),
            country_indeed="USA",  # Adjust if outside US
            verbose=False,
        )
        jobs.extend(_df_to_jobs(df, site))
    return jobs
