#!/usr/bin/env python3
"""
Automated QA & Verification Gate for `site/` (`session-85899999`).
Fails with non-zero exit code if ANY requirement is violated:
  1. All 8 HTML pages + assets exist.
  2. Zero broken internal links (`href` / `src`).
  3. Every `<tr>` with `<td>` contains an official `.gov` / `.ca.gov` / county / utility link.
  4. Zero commercial / non-official external domains.
  5. Every `$` dollar figure is `$0` or divisible by `$10`.
  6. Unverified 2026 historical cells are strictly blank (`<td class="blank-cell"...></td>`).
  7. Zero PII / APN patterns.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

APPROVED_EXTERNAL_HOSTS = {
    "boe.ca.gov",
    "www.boe.ca.gov",
    "controller.santaclaracounty.gov",
    "www.sccassessor.org",
    "sftreasurer.org",
    "www.sfassessor.org",
    "www.sf.gov",
    "www.irs.gov",
    "www.ftb.ca.gov",
    "leginfo.legislature.ca.gov",
    "docs.cpuc.ca.gov",
    "www.cpuc.ca.gov",
    "www.sfpuc.gov",
    "www.insurance.ca.gov",
    "interactive.web.insurance.ca.gov",
    "www.huduser.gov",
    "www.fhfa.gov",
    "www.cbo.gov",
    "www.federalreserve.gov",
}

BANNED_SUBSTRINGS = [
    "policygenius", "nerdwallet", "zillow", "redfin", "rentometer",
    "ballotpedia", "wikipedia", "cornell.edu", "car.org", "hjta",
    "smartasset", "investopedia", "bankrate",
]

REQUIRED_PAGES = [
    "index.html", "properties.html", "projections.html", "scenarios.html",
    "estate-tax.html", "inheritance-guide.html", "flagged-review.html", "sources.html",
]


def main() -> int:
    errors = []

    # 1. File existence
    for p in REQUIRED_PAGES + ["assets/styles.css", "assets/app.js", "assets/data.js", ".nojekyll"]:
        fp = SITE / p
        if not fp.exists():
            errors.append(f"Missing required file: site/{p}")
        elif p != ".nojekyll" and fp.stat().st_size == 0:
            errors.append(f"Empty file: site/{p}")

    total_data_rows = 0
    total_ext_links = 0

    for fname in REQUIRED_PAGES:
        fp = SITE / fname
        if not fp.exists():
            continue
        html = fp.read_text(encoding="utf-8")

        # 2. Banned commercial substrings
        low = html.lower()
        for bad in BANNED_SUBSTRINGS:
            if bad in low:
                errors.append(f"[{fname}] Contains banned non-official reference: {bad}")

        # 3. Internal & external links
        for attr, target in re.findall(r'\b(href|src)="([^"]+)"', html):
            if target.startswith("http://"):
                errors.append(f"[{fname}] Insecure http:// link: {target}")
            elif target.startswith("https://"):
                total_ext_links += 1
                host = target.split("/")[2]
                if host not in APPROVED_EXTERNAL_HOSTS:
                    errors.append(f"[{fname}] Unapproved external domain '{host}' in {target}")
            elif not target.startswith("#") and not target.startswith("mailto:"):
                clean_target = target.split("#")[0].split("?")[0]
                if clean_target and not (SITE / clean_target).exists():
                    errors.append(f"[{fname}] Broken internal {attr}='{target}'")

        # 4. Every <tr> containing <td> must have an official https:// link
        for idx, tr in enumerate(re.findall(r"<tr\b[^>]*>.*?</tr>", html, flags=re.S), start=1):
            if "<td" not in tr:
                continue
            total_data_rows += 1
            if 'href="https://' not in tr:
                errors.append(f"[{fname}] Table row #{idx} has <td> data without an official https:// source link!")

        # 5. Strict $10 rounding check on visible text (strip <script>/<style> & <code>$10</code>)
        visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        for m in re.finditer(r"\$([0-9][0-9,]*(?:\.[0-9]+)?)", visible):
            raw_num = m.group(1).replace(",", "")
            val = float(raw_num)
            if "." in raw_num:
                errors.append(f"[{fname}] Unrounded decimal dollar amount '${m.group(1)}' found (must round to nearest $10)")
            else:
                ival = int(raw_num)
                if ival != 0 and ival % 10 != 0:
                    errors.append(f"[{fname}] Unrounded integer dollar amount '${m.group(1)}' (not divisible by $10)")

        # 6. APN / SSN pattern check
        if re.search(r"\b\d{3}-\d{2}-\d{3,4}\b", visible):
            errors.append(f"[{fname}] Potential APN or SSN pattern detected!")

    # 7. Check blank cells in properties.html (3 unverified 2026 historical cells)
    prop_html = (SITE / "properties.html").read_text(encoding="utf-8")
    blank_cells = re.findall(r'<td class="blank-cell"[^>]*>(.*?)</td>', prop_html, flags=re.S)
    if len(blank_cells) != 3:
        errors.append(f"[properties.html] Expected 3 blank unverified 2026 cells, found {len(blank_cells)}")
    for bc in blank_cells:
        if bc.strip() != "":
            errors.append(f"[properties.html] Blank cell is not empty: '{bc}'")

    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print("  -", e)
        return 1

    print(f"VERIFICATION PASSED: 8/8 pages clean | {total_data_rows} data rows (100% with official .gov/utility links) | {total_ext_links} approved official links | 100% $10 rounding | 3/3 unverified cells strictly blank | 0 PII.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
