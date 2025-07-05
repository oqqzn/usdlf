# SAM Entity and IVL Contact Harvesting Workflow

## Directory Layout
```
usdlf/
├── data/
│   ├── entity/                      # monthly SAM extracts (raw + formatted)
│   │   └── YYYYMM/
│   │       ├── SAM_PUBLIC_UTF-8_MONTHLY_V2_YYYYMMDD.zip   (raw, optional)
│   │       ├── SAM_PUBLIC_UTF-8_MONTHLY_V2_YYYYMMDD.dat   (unzipped, used)
│   │       └── formatted_entities_YYYYMMDD.xlsx           (created by step 0)
│   └── harvests/
│       └── YYYYMM/                  # month of the run
│           └── YYYYMMDD_HHMMSS_<ptype>_harvest/           # one folder per run
│               ├── all_notices.csv
│               ├── ivl_hits.csv
│               └── harvest_summary.json
└── scripts/
    ├── 0-format_sam_data.py
    ├── 1-dod_ivl_harvester.py
    └── 2-merge_ivl_entities.py
```
---
## Tool‑chain Overview
```
(Step 0)  SAM monthly .dat/.zip
         data/entity/YYYYMM/                ──►  formatted_entities_YYYYMMDD.xlsx
(Step 1)  DoD IVL harvest
         data/harvests/YYYYMM/              ──►  YYYYMMDD_HHMMSS_<ptype>_harvest/
(Step 2)  Merge & curate
         *_harvest/ + formatted_entities     ──►  <run‑tag>_curated_ivl_contacts.xlsx
```
---
## Step 0  –  Format the monthly SAM extract
*Script  `scripts/0-format_sam_data.py`*

| Input (auto‑detected)                                                                  | Output (same folder)                                  |
|---------------------------------------------------------------------------------------|--------------------------------------------------------|
| Latest `.dat` **or** `.zip` under `data/entity/*/SAM_PUBLIC_UTF-8_MONTHLY_V2_*.dat`    | `formatted_entities_YYYYMMDD.xlsx`                    |

What happens:
1. Finds the newest file by the date in its name.
2. If only a `.zip` exists, unzips the `.dat` once.
3. Parses & maps real columns, extracts emails/phones (US‑validated), builds POC names.
4. Saves a tidy Excel ordered with email/phone‑rich rows first.

Important columns: UEI, CAGE, Status, Has Email, Email Addresses, Has Phone, Phone Numbers, NAICS, Business Type Codes, Entity Structure …

---
## Step 1  –  Harvest IVL rosters from DoD notices
*Script  `scripts/1-dod_ivl_harvester.py`*

| Config item  | Value / Notes                                   |
|--------------|-------------------------------------------------|
| **PTYPE**    | `p` (Presolicitation) – switch to `r` as needed |
| **Look‑back**| 90 days                                         |
| **Org code** | `097` (DoD)                                     |
| **API key**  | .env `SAM_API_KEY`               |

Each run writes to:
```
data/harvests/YYYYMM/YYYYMMDD_HHMMSS_<ptype>_harvest/
```
Example: `data/harvests/202508/20250801_093215_p_harvest/`

Files inside:
* **all_notices.csv** – every DoD notice returned
* **ivl_hits.csv** – one row per vendor in the IVL (noticeId, ueiSAM, cage, vendorName)
* **harvest_summary.json** – metadata (API calls, IVL rows, quota‑hit flag)

On the first **HTTP 429** the harvester cleanly stops, finalises files, and exits.

---
## Step 2  –  Merge IVL vendors with entity details
*Script  `scripts/2-merge_ivl_entities.py`*

* **Default:** picks the newest `*_harvest` folder under `data/harvests/*/` **and** the newest `formatted_entities_*.xlsx` under `data/entity/*/`.
* **Override:** `--harvest <path>` merges a specific run.

Process:
1. Load `ivl_hits.csv`. If it’s empty, exit quickly.
2. Load the latest formatted entity workbook.
3. Merge on **UEI**, fall back on **CAGE**.
4. Curate/rename columns, sort rows so email‑ready vendors rise to the top.
5. Save **`<run‑tag>_curated_ivl_contacts.xlsx`** inside the same run folder.

### Output columns (abridged)
Notice ID · Notice Title · Posted Date · Vendor Name · UEI · CAGE · Legal Business Name · Entity Status · Has Email · Email Addresses · Has Phone · Phone Numbers · Gov POC · Alt POC · Address · Primary NAICS · Business Type Codes · Entity Structure

---
## Practical Tips
* **Monthly refresh** – drop the new `.zip` or `.dat` into `data/entity/<new‑YYYYMM>/`; run *Step 0*.
* **Multiple harvests per day** – each run has its own timestamped folder; merge script always finds the latest.
* **Quota** – daily SAM API limit is 1 000 calls; the harvester exits on 429 and you can resume next day.
* **Email first** – curated workbook is sorted with `Has Email == "Yes"` at the top for quick outreach.
* **Curated excels** - take roughly 5 minutes for creation

---
© 2025  Internal tooling documentation
