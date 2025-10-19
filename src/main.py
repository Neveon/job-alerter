from pathlib import Path
import yaml
from providers.levels_html import fetch_leaderboards
from targets import load_blacklist, filter_companies, filter_rows


def load_yaml(p: str):
    return yaml.safe_load(Path(p).read_text())


def main():
    app = load_yaml("config/app.yaml")
    rules = load_yaml("config/rules.yaml")

    print("job-alerter bootstrap OK")
    print(f"- seed_mode: {app['runtime']['seed_mode']}")
    print(f"- levels urls: {len(app['levels']['urls'])}")
    print(f"- include keywords: {rules['keywords']['include_any']}")

    urls = app["levels"]["urls"]
    user_agent = app["runtime"]["user_agent"]
    timeout = app["runtime"]["request_timeout"]

    rows, companies = fetch_leaderboards(urls, timeout, user_agent)
    print(f"[levels] rows parsed: {len(rows)}  | unique companies: {len(companies)}")

    # Load & apply blacklist
    bl = load_blacklist()  # case-insensitive substring match
    print(f"[blacklist] terms: {len(bl)}")

    rows_f = filter_rows(rows, bl)
    companies_f = filter_companies(companies, bl)

    # Preview before/after
    print(f"[filtered] rows: {len(rows_f)}  | companies: {len(companies_f)}")
    print("\nTop 10 (after blacklist):")
    for r in rows_f[:10]:
        print(
            f"rank={r['rank']:<3} company={r['company']:<20} "
            f"title={r['title']:<25} total={r['comp_total']}"
        )

    print("\nCompanies (first 10 after blacklist):")
    for c in companies_f[:10]:
        print(" -", c)


if __name__ == "__main__":
    main()
