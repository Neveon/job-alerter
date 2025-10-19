from pathlib import Path
import yaml
from providers.levels_html import fetch_leaderboards


def load_yaml(p: str):
    return yaml.safe_load(Path(p).read_text())


def main():
    app = load_yaml("config/app.yaml")
    rules = load_yaml("config/rules.yaml")
    bl_lines = (
        Path("config/blacklist.txt").read_text().splitlines()
        if Path("config/blacklist.txt").exists()
        else []
    )
    blacklist = [
        line.strip()
        for line in bl_lines
        if line.strip() and not line.strip().startswith("#")
    ]

    print("job-alerter bootstrap OK")
    print(f"- seed_mode: {app['runtime']['seed_mode']}")
    print(f"- levels urls: {len(app['levels']['urls'])}")
    print(f"- blacklist entries: {len(blacklist)}")
    print(f"- include keywords: {rules['keywords']['include_any']}")

    urls = app["levels"]["urls"]
    user_agent = app["runtime"]["user_agent"]
    timeout = app["runtime"]["request_timeout"]

    rows, companies = fetch_leaderboards(urls, timeout, user_agent)

    print(f"\n[levels] rows parsed: {len(rows)}")
    for r in rows[:8]:
        print(
            f"rank={r['rank']:<3} company={r['company']:<20} "
            f"title={r['title']:<25} total={r['comp_total']} base={r['comp_base']} stock={r['comp_stock']} bonus={r['comp_bonus']}"
        )

    print(f"\n[levels] unique companies: {len(companies)}")
    for c in companies[:10]:
        print(" -", c)

    print("Done.")


if __name__ == "__main__":
    main()
