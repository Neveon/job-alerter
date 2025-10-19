# src/providers/levels_html.py
from __future__ import annotations
import re
from typing import List, Dict, Tuple
import requests
from bs4 import BeautifulSoup


def _norm_text(node) -> str:
    return (node.get_text(separator=" ", strip=True) if node else "").strip()


_money_re = re.compile(r"[\$,]")


def _parse_money_to_int(s: str | None) -> int | None:
    """
    Convert money-like strings to an int in USD (no cents).
    Examples: "$301,000" -> 301000, "191K" -> 191000, "N/A" -> None.
    """
    if not s:
        return None
    s = s.strip()
    if not s or s.upper() in {"N/A", "NA"}:
        return None
    # Handle "191K" etc.
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*[Kk]", s)
    if m:
        return int(float(m.group(1)) * 1000)
    # Handle "$301,000" etc.
    s = _money_re.sub("", s)
    if s.isdigit():
        return int(s)
    # Last resort: pull digits only
    digits = re.sub(r"\D+", "", s)
    return int(digits) if digits else None


def parse_leaderboard_table(html: str) -> List[Dict]:
    """
    Parse the Levels leaderboard table structure you shared.

    Returns a list of rows:
      {
        "rank": int,
        "company": str,
        "title": str,
        "comp_total": int|None,
        "comp_base": int|None,
        "comp_stock": int|None,
        "comp_bonus": int|None,
      }
    """
    soup = BeautifulSoup(html, "html5lib")

    container = soup.select_one("#tableContainer") or soup
    table = container.select_one("table") or soup.select_one("table")
    if not table:
        return []

    tbody = table.select_one("tbody")
    if not tbody:
        return []

    rows: List[Dict] = []
    for idx, tr in enumerate(tbody.select("tr")):
        tds = tr.find_all("td")
        if not tds:
            continue

        rank = idx + 1

        # Company lives in td.company-data-column -> strong or link text
        company_td = tr.select_one("td.company-data-column")
        if company_td:
            # Prefer <strong> if present
            strong = company_td.find("strong")
            company = _norm_text(strong) if strong else _norm_text(company_td)
        else:
            company = _norm_text(tds[1]) if len(tds) >= 2 else ""

        # Title often in td.d-none.d-sm-table-cell
        title_td = tr.select_one("td.d-none.d-sm-table-cell")
        title = (
            _norm_text(title_td)
            if title_td
            else (_norm_text(tds[2]) if len(tds) >= 3 else "")
        )

        # Compensation: prefer hidden inputs if present
        last_td = tds[-1]
        total_div = last_td.select_one(".total-comp-number")
        comp_total_txt = _norm_text(total_div) if total_div else _norm_text(last_td)

        # Hidden inputs (seen in your screenshot)
        # <input class="d-none total-comp" value="301000">
        # <input class="d-none base-salary" value="191000">
        # <input class="d-none stock-grant" value="110000">
        # <input class="d-none yearly-bonus" value="0">
        inp_total = last_td.select_one("input.total-comp")
        inp_base = last_td.select_one("input.base-salary")
        inp_stock = last_td.select_one("input.stock-grant")
        inp_bonus = last_td.select_one("input.yearly-bonus")

        comp_total = None
        comp_base = None
        comp_stock = None
        comp_bonus = None

        if inp_total and inp_total.has_attr("value"):
            try:
                comp_total = int(inp_total["value"])
            except Exception:
                comp_total = _parse_money_to_int(comp_total_txt)
        else:
            comp_total = _parse_money_to_int(comp_total_txt)

        if inp_base and inp_base.has_attr("value"):
            try:
                comp_base = int(inp_base["value"])
            except Exception:
                comp_base = None
        if inp_stock and inp_stock.has_attr("value"):
            try:
                comp_stock = int(inp_stock["value"])
            except Exception:
                comp_stock = None
        if inp_bonus and inp_bonus.has_attr("value"):
            try:
                comp_bonus = int(inp_bonus["value"])
            except Exception:
                comp_bonus = None

        # If hidden inputs missing, try parsing "Base | Stock | Bonus" text
        if comp_base is None or comp_stock is None or comp_bonus is None:
            base_stock_bonus = last_td.select_one(".base-stock-bonus")
            if base_stock_bonus:
                parts = [p.strip() for p in _norm_text(base_stock_bonus).split("|")]
                if len(parts) >= 3:
                    base, stock, bonus = parts[0], parts[1], parts[2]
                    if comp_base is None:
                        comp_base = _parse_money_to_int(base)
                    if comp_stock is None:
                        comp_stock = _parse_money_to_int(stock)
                    if comp_bonus is None:
                        comp_bonus = _parse_money_to_int(bonus)

        rows.append(
            {
                "rank": rank,
                "company": company,
                "title": title,
                "comp_total": comp_total,
                "comp_base": comp_base,
                "comp_stock": comp_stock,
                "comp_bonus": comp_bonus,
            }
        )

    # Sort by rank (tbody order should already be rank-ordered, but be safe)
    rows.sort(key=lambda r: r.get("rank", 100))
    return rows


def fetch_leaderboards(
    urls: List[str], timeout: int, user_agent: str
) -> Tuple[List[Dict], List[str]]:
    """
    Fetch multiple leaderboard pages and merge rows. Also returns a deduped company list.
    """
    headers = {"User-Agent": user_agent}
    all_rows: List[Dict] = []
    for url in urls:
        req = requests.get(url, headers=headers, timeout=timeout)
        req.raise_for_status()
        all_rows.extend(parse_leaderboard_table(req.text))

    # Deduplicate companies keeping appearance order
    seen = set()
    companies: List[str] = []
    for row in all_rows:
        name = row.get("company", "").strip()
        if name and name not in seen:
            seen.add(name)
            companies.append(name)

    return all_rows, companies
