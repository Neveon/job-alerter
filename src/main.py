from pathlib import Path
import yaml


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
    print("Done.")


if __name__ == "__main__":
    main()
