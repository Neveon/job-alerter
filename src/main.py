from pathlib import Path
import yaml
from providers.levels_html import fetch_leaderboards
from providers.jobspy_search import search_company_roles, search_by_query
from targets import (
    filter_job_companies,
    load_blacklist,
    filter_companies,
    filter_rows,
    filter_jobs,
    deduplicate_jobs,
)
from models import Job


def load_yaml(p: str):
    return yaml.safe_load(Path(p).read_text())


def format_salary(job: Job) -> str:
    """Format salary for display."""
    if job.salary.min is not None and job.salary.max is not None:
        return f"${job.salary.min:,} - ${job.salary.max:,}"
    elif job.salary.min is not None:
        return f"${job.salary.min:,}+"
    elif job.salary.max is not None:
        return f"up to ${job.salary.max:,}"
    else:
        return "N/A"


def main():
    app = load_yaml("config/app.yaml")
    rules = load_yaml("config/rules.yaml")

    print("job-alerter bootstrap OK")
    print(f"- seed_mode: {app['runtime']['seed_mode']}")
    print(f"- levels urls: {len(app['levels']['urls'])}")
    print(
        f"- include keywords: {rules['role_titles']['include_any'] + rules['job_descriptions']['include_any']}"
    )

    # Load & apply blacklist
    bl = load_blacklist()  # case-insensitive substring match
    print(f"[blacklist] terms: {len(bl)}")

    # --- JobSpy configuration ---
    js = app.get("jobspy", {})
    site = js.get("site", "indeed")
    location = js.get("location", "Austin, TX")
    radius_miles = js.get("radius_miles", 50)
    results_wanted = js.get("results_wanted", 100)
    hours_old = js.get("hours_old", 168)

    # Extract role keywords from rules.yaml for JobSpy search terms
    role_keywords = (
        rules["role_titles"]["include_any"] + rules["job_descriptions"]["include_any"]
    )

    urls = app["levels"]["urls"]
    user_agent = app["runtime"]["user_agent"]
    timeout = app["runtime"]["request_timeout"]

    rows, companies = fetch_leaderboards(urls, timeout, user_agent)
    print(f"[levels] rows parsed: {len(rows)}  | unique companies: {len(companies)}")

    rows_f = filter_rows(rows, bl)
    companies_f = filter_companies(companies, bl)

    # Preview before/after
    print(f"[filtered] rows: {len(rows_f)}  | companies: {len(companies_f)}")
    print("\nTop 10 (after blacklist):")
    for r in rows_f[:15]:
        print(
            f"rank={r['rank']:<3} company={r['company']:<20} "
            f"title={r['title']:<25} total={r['comp_total']}"
        )

    print("\nCompanies (first 15 after blacklist):")
    for c in companies_f[:15]:
        print(" -", c)

    print("\n=== JobSpy Primary Query (Top 15 Companies) ===")
    print(
        f"Searching for roles at top (levels.fyi ranked) companies with keywords: {role_keywords}"
    )

    # Primary query: Search top 15 (levels.fyi ranked) companies
    all_jobs = []
    top_companies = companies_f[:15]  # Limit to top 15

    for company in top_companies:
        print(f"\nSearching {company}...")
        try:
            company_jobs = search_company_roles(
                site=site,
                company=company,
                role_terms=role_keywords,
                location=location,
                radius_miles=radius_miles,
                results_wanted=results_wanted,
                hours_old=hours_old,
            )
            all_jobs.extend(company_jobs)
            print(f"  Found {len(company_jobs)} jobs at {company}")
        except Exception as e:
            print(f"  Error searching {company}: {e}")

    # Deduplicate and filter jobs
    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"\nTotal unique jobs found across all companies: {len(unique_jobs)}")

    # Apply blacklist and rules filtering
    final_jobs = filter_jobs(unique_jobs, rules)
    print(f"After rules filtering: {len(final_jobs)}")

    # Print results
    print("\n=== Available Roles at Top Companies (Levels.fyi Ranked) ===")
    for job in final_jobs:
        sal_txt = format_salary(job)
        print(
            f" - {job.company:<22} | {job.title:<30} | {job.location:<20} | {sal_txt} | {job.url}"
        )

    # Secondary query: Broad keyword search
    print("\n\n=== JobSpy Broad Keyword Search ===")
    print("Searching any company for roles matching keywords...")

    # Build broad query from keywords
    try:
        broad_jobs = search_by_query(
            site=site,
            role_terms=role_keywords,
            location=location,
            radius_miles=radius_miles,
            results_wanted=results_wanted,
            hours_old=hours_old,
        )
        print(f"Found {len(broad_jobs)} broad jobs")

        # Apply filtering rules
        broad_unique = deduplicate_jobs(broad_jobs)
        broad_companies_f = filter_job_companies(broad_unique, bl)
        broad_final = filter_jobs(broad_companies_f, rules)

        print(f"Broad search found {len(broad_final)} matching jobs after filtering")

        print("\n=== Example Broad Search Results ===")
        for job in broad_final:
            sal_txt = format_salary(job)
            print(
                f" - {job.company:<22} | {job.title:<30} | {job.location:<20} | {sal_txt} | {job.url}"
            )

    except Exception as e:
        print(f"Error in broad search: {e}")


if __name__ == "__main__":
    main()
