#!/usr/bin/env python3
"""
0-format_sam_data.py
────────────────────
Locate the newest monthly SAM public extract in   data/entity/<YYYYMM>/  ,
unzip it if necessary, and produce  formatted_entities_<YYYYMMDD>.xlsx  in
that same folder.
"""

from __future__ import annotations

import csv
import re
import sys
import time
import zipfile
from datetime import datetime as dt
from pathlib import Path
from typing import List

import pandas as pd

# ───────── Paths ─────────
ROOT_DIR = Path(__file__).resolve().parents[1]  # …/usdlf
ENTITY_ROOT = ROOT_DIR / "data" / "entity"

if not ENTITY_ROOT.exists():
    sys.exit("data/entity/ directory not found — expected relative to script root.")

# ───────── Find latest .dat (or .zip) ─────────
pattern = re.compile(r"SAM_PUBLIC_UTF-8_MONTHLY_V2_(\d{8})\.(dat|zip)$")
candidates: List[tuple[dt, Path]] = []
for p in ENTITY_ROOT.glob("*/*SAM_PUBLIC_UTF-8_MONTHLY_V2_*.*"):
    m = pattern.match(p.name)
    if m:
        date_obj = dt.strptime(m.group(1), "%Y%m%d")
        candidates.append((date_obj, p))

if not candidates:
    sys.exit("No SAM_PUBLIC_UTF-8_MONTHLY_V2_*.dat or .zip found in data/entity/*/")

# newest by file date in name
latest_date, latest_file = max(candidates, key=lambda t: t[0])
folder = latest_file.parent  # data/entity/YYYYMM/
print("Found latest extract:", latest_file.relative_to(ROOT_DIR))

# Ensure we have a .dat to read
if latest_file.suffix == ".zip":
    dat_name = latest_file.with_suffix(".dat").name
    dat_path = folder / dat_name
    if not dat_path.exists():
        print("Unzipping", latest_file.name, "→", dat_name)
        with zipfile.ZipFile(latest_file, "r") as zf:
            member = [m for m in zf.namelist() if m.endswith(".dat")][0]
            zf.extract(member, path=folder)
            (folder / member).rename(dat_path)
    else:
        print(".dat already present, skip unzip")
else:
    dat_path = latest_file

print("Using .dat:", dat_path.name)
DATE_TAG = pattern.match(dat_path.name).group(1)  # YYYYMMDD
OUTPUT_FILE = folder / f"formatted_entities_{DATE_TAG}.xlsx"
print("Formatted Excel will be:", OUTPUT_FILE.relative_to(ROOT_DIR))

# ───────── Increase CSV field limit ─────────
csv.field_size_limit(sys.maxsize)

# ───────── Helpers (phone/email/validation) — unchanged logic ─────────
US_AREA_CODES = {
    "907",
    "205",
    "251",
    "256",
    "334",
    "479",
    "501",
    "870",
    "480",
    "520",
    "602",
    "623",
    "928",
    "209",
    "213",
    "310",
    "323",
    "408",
    "415",
    "510",
    "530",
    "559",
    "562",
    "619",
    "626",
    "650",
    "661",
    "707",
    "714",
    "760",
    "805",
    "818",
    "831",
    "858",
    "909",
    "916",
    "925",
    "949",
    "951",
    "303",
    "719",
    "970",
    "203",
    "860",
    "202",
    "302",
    "239",
    "305",
    "321",
    "352",
    "386",
    "407",
    "561",
    "727",
    "772",
    "813",
    "850",
    "863",
    "904",
    "941",
    "954",
    "229",
    "404",
    "478",
    "706",
    "770",
    "912",
    "808",
    "319",
    "515",
    "563",
    "641",
    "712",
    "208",
    "217",
    "309",
    "312",
    "618",
    "630",
    "708",
    "773",
    "815",
    "847",
    "219",
    "260",
    "317",
    "574",
    "765",
    "812",
    "316",
    "620",
    "785",
    "913",
    "270",
    "502",
    "606",
    "859",
    "225",
    "318",
    "337",
    "504",
    "985",
    "413",
    "508",
    "617",
    "781",
    "978",
    "301",
    "410",
    "207",
    "231",
    "248",
    "269",
    "313",
    "517",
    "586",
    "616",
    "734",
    "810",
    "906",
    "989",
    "218",
    "320",
    "507",
    "612",
    "651",
    "763",
    "952",
    "314",
    "417",
    "573",
    "636",
    "660",
    "816",
    "228",
    "601",
    "662",
    "406",
    "252",
    "336",
    "704",
    "828",
    "910",
    "919",
    "701",
    "308",
    "402",
    "603",
    "201",
    "551",
    "609",
    "732",
    "848",
    "856",
    "908",
    "973",
    "505",
    "575",
    "702",
    "725",
    "775",
    "212",
    "315",
    "347",
    "516",
    "518",
    "585",
    "607",
    "631",
    "646",
    "680",
    "716",
    "718",
    "845",
    "914",
    "917",
    "929",
    "934",
    "216",
    "234",
    "330",
    "419",
    "440",
    "513",
    "567",
    "614",
    "740",
    "937",
    "405",
    "539",
    "580",
    "918",
    "503",
    "541",
    "971",
    "215",
    "267",
    "272",
    "412",
    "445",
    "570",
    "582",
    "610",
    "717",
    "724",
    "814",
    "835",
    "401",
    "803",
    "839",
    "843",
    "854",
    "864",
    "605",
    "423",
    "615",
    "629",
    "731",
    "865",
    "901",
    "931",
    "210",
    "214",
    "254",
    "281",
    "325",
    "346",
    "361",
    "409",
    "430",
    "432",
    "469",
    "512",
    "682",
    "713",
    "737",
    "806",
    "817",
    "830",
    "832",
    "903",
    "915",
    "936",
    "940",
    "956",
    "972",
    "979",
    "276",
    "434",
    "540",
    "571",
    "703",
    "757",
    "804",
    "802",
    "206",
    "253",
    "360",
    "425",
    "509",
    "262",
    "274",
    "414",
    "534",
    "608",
    "715",
    "920",
    "304",
    "681",
    "307",
}


def is_valid_us_phone(phone_str: str, pattern: str) -> bool:
    digits = re.sub(r"\D", "", phone_str)
    if pattern in [
        r"\b\d{3}-\d{3}-\d{4}\b",
        r"\b\d{10}\b",
        r"\b\d{3}\s+\d{3}\s+\d{4}\b",
    ]:
        if len(digits) != 10:
            return False
        return digits[:3] in US_AREA_CODES
    return False


def extract_phones_from_row(row):
    patterns = [r"\b\d{3}-\d{3}-\d{4}\b", r"\b\d{10}\b", r"\b\d{3}\s+\d{3}\s+\d{4}\b"]
    phones = []
    for cell in row:
        if cell and len(cell) >= 10:
            for pat in patterns:
                for ph in re.findall(pat, cell):
                    if is_valid_us_phone(ph, pat):
                        phones.append(ph)
    return list(dict.fromkeys(phones))


def extract_emails_from_row(row):
    pat = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    emails = []
    for cell in row:
        if cell and "@" in cell:
            for em in re.findall(pat, cell, re.IGNORECASE):
                el = em.lower()
                if not any(inv in el for inv in ["@.", "..", "@-", "-@"]):
                    emails.append(el)
    return list(dict.fromkeys(emails))


# Column map (unchanged)
COLUMN_MAPPINGS = {
    0: "UEI",
    3: "CAGE_CODE",
    5: "SAM_STATUS",
    6: "PURPOSE_OF_REG",
    11: "LEGAL_NAME",
    12: "DBA_NAME",
    15: "STREET_ADDRESS",
    17: "CITY",
    18: "STATE",
    19: "ZIP_CODE",
    21: "COUNTRY",
    22: "CONGRESSIONAL_DISTRICT",
    26: "WEBSITE_OR_EMAIL",
    27: "ENTITY_STRUCTURE",
    30: "BUSINESS_TYPE_COUNTER",
    31: "BUSINESS_TYPE_CODES",
    32: "PRIMARY_NAICS",
    33: "NAICS_CODE_COUNTER",
    34: "NAICS_CODE_STRING",
    37: "CREDIT_CARD_USAGE",
    39: "MAILING_ADDRESS",
    41: "MAILING_CITY",
    42: "MAILING_ZIP",
    45: "MAILING_STATE",
    46: "GOVT_POC_FIRST_NAME",
    47: "GOVT_POC_MIDDLE",
    48: "GOVT_POC_LAST_NAME",
    57: "ALT_POC_FIRST_NAME",
    58: "ALT_POC_MIDDLE",
    59: "ALT_POC_LAST_NAME",
    112: "NAICS_EXCEPTION_COUNTER",
    113: "NAICS_EXCEPTION_STRING",
}

print("\nProcessing entities …")
start_total = time.time()

all_records = []
with open(dat_path, "r", encoding="utf-8") as fh:
    reader = csv.reader(fh, delimiter="|")
    next(reader)  # skip header
    for i, row in enumerate(reader):
        rec = {
            name: (row[idx].strip() if idx < len(row) else "")
            for idx, name in COLUMN_MAPPINGS.items()
        }
        rec["BUSINESS_NAME"] = rec["LEGAL_NAME"]
        rec["BUSINESS_TYPE_CODES"] = (
            rec["BUSINESS_TYPE_CODES"].replace("~", ", ")
            if rec["BUSINESS_TYPE_CODES"]
            else ""
        )
        rec["STATUS"] = {"A": "Active", "E": "Expired"}.get(
            rec["SAM_STATUS"], rec["SAM_STATUS"]
        )
        # POC full names
        rec["GOVT_POC_FULL_NAME"] = " ".join(
            filter(
                None,
                [
                    rec.pop("GOVT_POC_FIRST_NAME"),
                    rec.pop("GOVT_POC_MIDDLE"),
                    rec.pop("GOVT_POC_LAST_NAME"),
                ],
            )
        ).strip()
        rec["ALT_POC_FULL_NAME"] = " ".join(
            filter(
                None,
                [
                    rec.pop("ALT_POC_FIRST_NAME"),
                    rec.pop("ALT_POC_MIDDLE"),
                    rec.pop("ALT_POC_LAST_NAME"),
                ],
            )
        ).strip()
        # emails, phones
        ems = extract_emails_from_row(row)
        phs = extract_phones_from_row(row)
        rec.update(
            {
                "ALL_EMAILS": "; ".join(ems),
                "EMAIL_COUNT": len(ems),
                "HAS_EMAIL": "Yes" if ems else "No",
                "ALL_PHONES": "; ".join(phs),
                "PHONE_COUNT": len(phs),
                "HAS_PHONE": "Yes" if phs else "No",
            }
        )
        all_records.append(rec)
        if i % 10000 == 0:
            print(f"  processed {i:,} rows …", end="\r", flush=True)
print()

# DataFrame & export
print("Creating DataFrame …")
df = pd.DataFrame(all_records)
order = [
    "UEI",
    "CAGE_CODE",
    "BUSINESS_NAME",
    "STATUS",
    "WEBSITE_OR_EMAIL",
    "HAS_EMAIL",
    "EMAIL_COUNT",
    "HAS_PHONE",
    "PHONE_COUNT",
    "ALL_EMAILS",
    "ALL_PHONES",
    "GOVT_POC_FULL_NAME",
    "ALT_POC_FULL_NAME",
    "STREET_ADDRESS",
    "CITY",
    "STATE",
    "ZIP_CODE",
    "PRIMARY_NAICS",
    "BUSINESS_TYPE_CODES",
    "ENTITY_STRUCTURE",
    "SAM_STATUS",
    "PURPOSE_OF_REG",
]
order = [c for c in order if c in df.columns]
rename = {
    "CAGE_CODE": "CAGE",
    "BUSINESS_NAME": "Business Name",
    "STATUS": "Status",
    "WEBSITE_OR_EMAIL": "Website or Email",
    "HAS_EMAIL": "Has Email",
    "HAS_PHONE": "Has Phone",
    "ALL_EMAILS": "Email Addresses",
    "ALL_PHONES": "Phone Numbers",
    "GOVT_POC_FULL_NAME": "Government POC Name",
    "ALT_POC_FULL_NAME": "Alternate POC Name",
    "ZIP_CODE": "ZIP",
}
df = df[order].rename(columns=rename)
if "Has Email" in df.columns:
    df["Has Email"].fillna("No", inplace=True)
    df.sort_values(["Has Email", "Has Phone"], ascending=[False, False], inplace=True)

print("Saving Excel …")
df.to_excel(OUTPUT_FILE, index=False)
print("✓ Saved", OUTPUT_FILE.relative_to(ROOT_DIR))
print(f"Total rows: {len(df):,}  |  Execution time: {time.time() - start_total:.1f} s")
