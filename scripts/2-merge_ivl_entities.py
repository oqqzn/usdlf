#!/usr/bin/env python3
"""
Find the newest IVL harvest run under   data/harvests/*/*_harvest/   (or a
specific one supplied via --harvest) and merge it with the newest formatted
SAM entity sheet found under   data/entity/*/formatted_entities_*.xlsx   to
produce a curated contact workbook.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import pandas as pd

# ───────── Paths ─────────
ROOT_DIR = Path(__file__).resolve().parents[1]  # …/usdlf
DATA_DIR = ROOT_DIR / "data"
ENTITY_ROOT = DATA_DIR / "entity"
HARVEST_ROOT = DATA_DIR / "harvests"

# ───────── CLI ─────────
parser = argparse.ArgumentParser(description="Merge IVL roster with SAM entity data.")
parser.add_argument(
    "--harvest", type=Path, help="Path to a specific *_harvest dir (optional)"
)
args = parser.parse_args()

# ───────── Locate harvest run ─────────
if args.harvest:
    HARV_DIR = args.harvest.expanduser().resolve()
    if not (HARV_DIR.is_dir() and HARV_DIR.name.endswith("_harvest")):
        sys.exit("Provided --harvest path is not a *_harvest directory.")
else:
    pat = re.compile(r"(\d{8}_\d{6})_[a-z]+_harvest$")
    runs = [p for p in HARVEST_ROOT.glob("*/**/*_harvest") if pat.search(p.name)]
    if not runs:
        sys.exit("No *_harvest runs found under data/harvests/")
    HARV_DIR = max(
        runs, key=lambda p: pat.search(p.name).group(1)
    )  # max by timestamp string

IVL_FILE = HARV_DIR / "ivl_hits.csv"
if not IVL_FILE.exists():
    sys.exit(f"ivl_hits.csv not found in {HARV_DIR}")

run_tag = HARV_DIR.name.replace("_harvest", "")  # 20250801_093215_p
OUT_XLSX = HARV_DIR / f"{run_tag}_curated_ivl_contacts.xlsx"

# ───────── Load IVL ─────────
ivl = pd.read_csv(IVL_FILE, dtype=str)
print("Using harvest folder :", HARV_DIR.relative_to(ROOT_DIR))
print("IVL rows loaded      :", len(ivl))

# normalise headers
if "ueiSAM" not in ivl.columns and "uei" in ivl.columns:
    ivl.rename(columns={"uei": "ueiSAM"}, inplace=True)
if "cage" not in ivl.columns and "cageNumber" in ivl.columns:
    ivl.rename(columns={"cageNumber": "cage"}, inplace=True)

required_cols = {"ueiSAM", "cage"}
if not required_cols.issubset(ivl.columns):
    sys.exit("IVL file missing UEI/CAGE columns after normalisation.")
if ivl.empty:
    print("No IVL rows, nothing to merge. Exiting.")
    sys.exit(0)

ivl["ueiSAM"] = ivl["ueiSAM"].str.strip()
ivl["cage"] = ivl["cage"].str.upper().str.strip()

# ───────── Locate newest entity sheet ─────────
entity_pat = re.compile(r"formatted_entities_(\d{8})\.xlsx$")
entity_files = [
    p
    for p in ENTITY_ROOT.glob("*/formatted_entities_*.xlsx")
    if entity_pat.search(p.name)
]
if not entity_files:
    sys.exit("No formatted_entities_*.xlsx found under data/entity/*/")
ENTITY_XLS = max(entity_files, key=lambda p: entity_pat.search(p.name).group(1))
print("Entity extract file  :", ENTITY_XLS.relative_to(ROOT_DIR))
print("Output Excel        :", OUT_XLSX.relative_to(ROOT_DIR))

ent = pd.read_excel(ENTITY_XLS, dtype=str)
ent["UEI"] = ent["UEI"].str.strip()
ent["CAGE"] = ent["CAGE"].str.upper().str.strip()
print("Entity records loaded:", len(ent))

# ───────── Merge ─────────
merged = ivl.merge(ent, left_on="ueiSAM", right_on="UEI", how="left", indicator=True)
needs_cage = merged["_merge"] == "left_only"
if needs_cage.any():
    merged.loc[needs_cage, :] = ivl[needs_cage].merge(
        ent, left_on="cage", right_on="CAGE", how="left"
    )
merged.drop(columns="_merge", inplace=True)
print("Rows with entity data:", merged["UEI"].notna().sum(), "/", len(merged))

# ───────── Curate ─────────
colmap = {
    "noticeId": "Notice ID",
    "title": "Notice Title",
    "solicitationNumber": "Solicitation #",
    "postedDate": "Notice Posted",
    "vendorName": "Vendor Name",
    "ueiSAM": "UEI",
    "cage": "CAGE",
    "Business Name": "Legal Business Name",
    "Status": "Entity Status",
    "Has Email": "Has Email",
    "Email Addresses": "Email Addresses",
    "Has Phone": "Has Phone",
    "Phone Numbers": "Phone Numbers",
    "Government POC Name": "Gov POC Name",
    "Alternate POC Name": "Alt POC Name",
    "Street Address": "Street",
    "City": "City",
    "State": "State",
    "ZIP": "ZIP",
    "Primary NAICS": "Primary NAICS",
    "Business Type Codes": "Business Type Codes",
    "Entity Structure": "Entity Structure",
}
final = merged[[c for c in colmap if c in merged.columns]].rename(columns=colmap)
if "Has Email" in final.columns:
    final["Has Email"] = final["Has Email"].fillna("No")
    final.sort_values(
        ["Has Email", "Vendor Name"], ascending=[False, True], inplace=True
    )

# ───────── Save ─────────
final.to_excel(OUT_XLSX, index=False)
print("Curated list saved →", OUT_XLSX.relative_to(ROOT_DIR))
if "Has Email" in final.columns:
    print(
        "Total rows:", len(final), "| With e-mail:", (final["Has Email"] == "Yes").sum()
    )
else:
    print("Total rows:", len(final))
