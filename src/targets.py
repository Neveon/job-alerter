from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Dict


def load_blacklist(path: str = "config/blacklist.txt") -> list[str]:
    """
    Load blacklist (one company per line). Case-insensitive, ignores blanks/# comments.
    """
    p = Path(path)
    if not p.exists():
        return []
    lines = [ln.strip() for ln in p.read_text().splitlines()]
    return [ln.lower() for ln in lines if ln and not ln.startswith("#")]


def _is_blocked(name: str, blacklist: Iterable[str]) -> bool:
    """
    Block if any blacklist token is a case-insensitive substring of the company name.
    Ex: "block" blocks "Block", "Block Inc.", etc.
    """
    ln = name.lower()
    return any(token in ln for token in blacklist)


def filter_companies(companies: List[str], blacklist: List[str]) -> List[str]:
    """Preserve original order; drop blacklisted names."""
    out = []
    for c in companies:
        if not _is_blocked(c, blacklist):
            out.append(c)
    return out


def filter_rows(rows: List[Dict], blacklist: List[str]) -> List[Dict]:
    """Drop rows whose company is blacklisted; preserve order."""
    return [r for r in rows if not _is_blocked(r.get("company", ""), blacklist)]
