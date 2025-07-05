#!/usr/bin/env python3
"""
1-dod_ivl_harvester.py
──────────────────────
Harvest DoD presolicitation (PTYPE="p") or sources‑sought (PTYPE="r") notices
from SAM.gov and dump IVL rosters to    data/harvests/<YYYYMM>/<run-tag>_harvest/

Run‑tag:  <YYYYMMDD_HHMMSS>_<ptype>_harvest  (e.g. 20250801_093215_p_harvest)
The script creates any missing month folders automatically.
"""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

import requests

# ───────── Config ─────────
ROOT_DIR = Path(__file__).resolve().parents[1]  # …/usdlf
DATA_DIR = ROOT_DIR / "data"
HARVEST_ROOT = DATA_DIR / "harvests"

API_KEY = os.getenv("SAM_API_KEY")
LOOKBACK_DAYS = 90
ORG_CODE = "097"  # DoD
PTYPE = "p"  # "p"=Presolicitation, "r"=Sources Sought
PAGE_SIZE = 1_000
SLEEP_BETWEEN_IVL = 0.2
# ─────────────────────────

if not API_KEY:
    sys.exit("Set SAM_API_KEY env var (preferred) or hard-code it in this script.")

# ───────── Prepare output dirs ─────────
now = dt.datetime.now()
month_tag = now.strftime("%Y%m")  # 202508
run_tag = now.strftime("%Y%m%d_%H%M%S") + f"_{PTYPE}"  # 20250801_093215_p
RUN_DIR = HARVEST_ROOT / month_tag / f"{run_tag}_harvest"
RUN_DIR.mkdir(parents=True, exist_ok=True)

FN_NOTICES = RUN_DIR / "all_notices.csv"
FN_IVL = RUN_DIR / "ivl_hits.csv"
FN_JSON = RUN_DIR / "harvest_summary.json"

print("Output folder:", RUN_DIR.relative_to(ROOT_DIR))

# ───────── CSV helpers ─────────
import csv


def csv_writer(path: Path, header: List[str]):
    exists = path.exists()
    f = path.open("a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if not exists:
        w.writerow(header)
    return w, f


not_wr, nf = csv_writer(
    FN_NOTICES, ["noticeId", "title", "postedDate", "ptype", "ivl_len"]
)
ivl_wr, vf = csv_writer(FN_IVL, ["noticeId", "ueiSAM", "cage", "vendorName"])

# ───────── Date range ─────────
today = now.date()
posted_from = (today - dt.timedelta(days=LOOKBACK_DAYS)).strftime("%m/%d/%Y")
posted_to = today.strftime("%m/%d/%Y")

# ───────── HTTP session ─────────
session = requests.Session()
session.params = {"api_key": API_KEY}

offset = 0
page = 0
api_calls = 0
ivl_rows = 0
rate_limit_hit = False

print("Begin harvest…")

while True:
    # search endpoint
    page += 1
    params = {
        "limit": PAGE_SIZE,
        "offset": offset,
        "postedFrom": posted_from,
        "postedTo": posted_to,
        "ptype": PTYPE,
        "sortBy": "-postedDate",
        "organizationCode": ORG_CODE,
    }
    resp = session.get(
        "https://api.sam.gov/opportunities/v2/search", params=params, timeout=40
    )
    api_calls += 1

    if resp.status_code == 429:
        print("  ⏹  Daily quota hit (search). Stopping.")
        rate_limit_hit = True
        break
    if not resp.ok:
        print("  ❌  Search failed (status", resp.status_code, ") — aborting.")
        break

    notices = resp.json().get("opportunitiesData", [])
    if not notices:
        break
    for n in notices:
        nid = n["noticeId"]
        title = n["title"].strip()
        posted = n["postedDate"]

        # IVL call
        ivl_url = f"https://api.sam.gov/opportunities/v2/opportunities/{nid}/ivl"
        ivl_resp = session.get(ivl_url, timeout=40)
        api_calls += 1

        if ivl_resp.status_code == 429:
            print("  ⏹  Daily quota hit (IVL). Stopping.")
            rate_limit_hit = True
            break

        roster: List[Dict] = []
        ivl_count = 0
        if ivl_resp.ok and ivl_resp.status_code not in (403, 404):
            roster = ivl_resp.json().get("ivl", [])
            ivl_count = len(roster)
        if roster:
            for v in roster:
                ivl_wr.writerow(
                    [nid, v.get("ueiSAM"), v.get("cageNumber"), v.get("name")]
                )
                ivl_rows += 1
        not_wr.writerow([nid, title, posted, PTYPE, ivl_count])
        time.sleep(SLEEP_BETWEEN_IVL)
    if rate_limit_hit:
        break
    offset += PAGE_SIZE

# ───────── Wrap‑up ─────────
nf.close()
vf.close()
meta = {
    "run_utc": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "run_dir": str(RUN_DIR.relative_to(ROOT_DIR)),
    "lookback_days": LOOKBACK_DAYS,
    "ptype": PTYPE,
    "org_code": ORG_CODE,
    "api_calls": api_calls,
    "ivl_rows": ivl_rows,
    "quota_hit": rate_limit_hit,
}
FN_JSON.write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("✓ Harvest complete —", meta)
