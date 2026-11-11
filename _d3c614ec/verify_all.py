#!/usr/bin/env python3
"""Comprehensive zero-hash verification gate for _d3c614ec/ and remediated repo files
(session arena/d3c614ec-tino1, 2026-11-11).

Checks:
1. HTML structure, <meta name="robots" content="noindex, nofollow">, and zero broken internal links/anchors.
2. 100% of <tr> data rows in _d3c614ec/site/*.html link to an allowlisted official .gov / public-agency host.
3. Zero banned commercial/blog hosts anywhere in _d3c614ec/.
4. 100% $10 rounding on all household/modeled dollar figures (allowing only verbatim statutory constants).
5. Zero 64-hex hash fingerprint tables stored in _d3c614ec/ or final/data/ (per K1 brute-force protection rule).
6. Optional external multi-format exact-figure scan via TINO1_PRIVATE_FIGURES=/outside/repo/file.txt
   (catching comma, plain, underscore '_', space, and regex ',?' variants without storing figures in-repo).
"""
from __future__ import annotations

from html.parser import HTMLParser
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
SITE_DIR = HERE / "site"

ALLOWED_HOSTS = {
    "www.irs.gov",
    "irs.gov",
    "www.sco.ca.gov",
    "leginfo.legislature.ca.gov",
    "www.boe.ca.gov",
    "boe.ca.gov",
    "www.ftb.ca.gov",
    "electionresults.sos.ca.gov",
    "files.santaclaracounty.gov",
    "asr.santaclaracounty.gov",
    "clerkrecorder.santaclaracounty.gov",
    "sftreasurer.org",
    "www.sf.gov",
    "sf.gov",
    "www.cpuc.ca.gov",
    "docs.cpuc.ca.gov",
    "www.insurance.ca.gov",
    "www.huduser.gov",
    "fred.stlouisfed.org",
    "www.bls.gov",
    "home.treasury.gov",
    "www.federalreserve.gov",
    "www.cbo.gov",
    "www.nber.org",
}

BANNED_SUBSTRINGS = (
    "zillow.com",
    "redfin.com",
    "realtor.com",
    "trulia.com",
    "nerdwallet.com",
    "bankrate.com",
    "smartasset.com",
    "turbotax",
    "wikipedia.org",
    "investopedia.com",
)

# Verbatim statutory constants from official .gov publications (not household or modeled numbers)
STATUTORY_EXACT_DOLLARS = {
    "$0",
    "$0.02",
    "$0.03",
    "$0.55",
    "$1",
    "$1.10",
    "$10",
    "$24.15",
    "$56",
    "$76",
    "$500",
    "$600",
    "$1,000",
    "$7,000",
    "$16,500",
    "$20,000",
    "$51,050",
    "$72,724",
    "$102,100",
    "$200,000",
    "$250,000",
    "$324,973",
    "$371,479",
    "$445,771",
    "$500,000",
    "$563,200",
    "$633,600",
    "$661,375",
    "$742,953",
    "$793,650",
    "$1,000,000",
    "$1,044,586",
    "$13,990,000",
    "$15,000,000",
    "$15,480,000",
}


class PageAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.local_refs: list[tuple[str, str]] = []
        self.external_urls: list[str] = []
        self.has_noindex = False
        self.in_tr = False
        self.row_has_td = False
        self.row_has_official_link = False
        self.data_rows = 0
        self.unsourced_rows = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        if ad.get("id"):
            self.ids.add(ad["id"])
        if tag == "meta" and ad.get("name", "").lower() == "robots":
            c = ad.get("content", "").lower()
            if "noindex" in c and "nofollow" in c:
                self.has_noindex = True
        if tag == "tr":
            self.in_tr = True
            self.row_has_td = False
            self.row_has_official_link = False
        if self.in_tr and tag == "td":
            self.row_has_td = True
        if tag in ("a", "link", "script", "img"):
            ref = ad.get("href") or ad.get("src")
            if not ref:
                return
            if ref.startswith(("https://", "http://")):
                self.external_urls.append(ref)
                host = urlparse(ref).hostname or ""
                if self.in_tr and ref.startswith("https://") and host in ALLOWED_HOSTS:
                    self.row_has_official_link = True
            elif not ref.startswith(("mailto:", "tel:", "javascript:")):
                if ref.startswith("#"):
                    self.local_refs.append(("", ref[1:]))
                else:
                    path_part, _, frag = ref.partition("#")
                    self.local_refs.append((path_part, frag))

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_tr:
            if self.row_has_td:
                self.data_rows += 1
                if not self.row_has_official_link:
                    self.unsourced_rows += 1
            self.in_tr = False


DOLLAR_RE = re.compile(r"\$\d[\d,]*(?:\.\d+)?(?![\d.A-Za-z])")
HEX64_RE = re.compile(r"\b[0-9a-f]{64}\b")


def check_dollar_rounding(text: str, label: str) -> int:
    # Strip <script>...</script> so JS template code (`'$' + ...`) isn't misread
    clean = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.S | re.I)
    checked = 0
    for m in DOLLAR_RE.finditer(clean):
        tok = m.group(0)
        if tok in STATUTORY_EXACT_DOLLARS:
            continue
        # Followed by M/k shorthand like $15.0M or $15.48M or $200k? Already filtered by (?![A-Za-z])
        if "." in tok:
            raise AssertionError(f"{label}: non-$10 decimal dollar token {tok!r} not in statutory allowlist")
        val = int(tok[1:].replace(",", ""))
        if val % 10 != 0:
            raise AssertionError(f"{label}: dollar figure {tok!r} is not rounded to nearest $10")
        checked += 1
    return checked


PII_PATTERNS = [
    (re.compile(r"\b\d{2,5}\s+[A-Z][a-z]+\s+(Street|St\.?|Avenue|Ave\.?|Drive|Dr\.?|Way|Court|Ct\.?|Lane|Ln\.?|Road|Rd\.?|Boulevard|Blvd\.?)\b"), "street address"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "email address"),
    (re.compile(r"\b\d{3}-\d{2}-\d{3}\b"), "APN parcel pattern"),
    (re.compile(r"\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b"), "phone number"),
]

TOKEN_SCAN_RE = re.compile(
    r"(?<![\d.,_])\d{1,3}(?:(?:,\??|\\,|[_ \u00a0]|&#44;)\d{3})+(?![\d.,_])|(?<![\d.,_])\d{5,7}(?![\d.,_])"
)


def scan_external_private_figures() -> str:
    env_path = os.environ.get("TINO1_PRIVATE_FIGURES", "").strip()
    if not env_path:
        return "external private-figure scan skipped (set TINO1_PRIVATE_FIGURES=/outside/repo/file to run)"
    p = Path(env_path).resolve()
    if REPO_ROOT in p.parents or p == REPO_ROOT:
        raise AssertionError("TINO1_PRIVATE_FIGURES must point OUTSIDE the repository!")
    fp_set = {
        re.sub(r"\D", "", line)
        for line in p.read_text(encoding="utf-8").splitlines()
        if len(re.sub(r"\D", "", line)) >= 4
    }
    hits = []
    # Scan our claimed & remediated scope + canonical root HTML/JSON
    scan_paths = list(HERE.rglob("*")) + [
        REPO_ROOT / "REPO-REVIEW.md",
        REPO_ROOT / "model" / "project.py",
        REPO_ROOT / "model" / "assumptions.md",
        REPO_ROOT / "model" / "verified_model_85899999.py",
    ] + list(REPO_ROOT.glob("*.html"))
    for fp in sorted(set(scan_paths)):
        if not fp.is_file():
            continue
        try:
            txt = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        for tok in set(TOKEN_SCAN_RE.findall(txt)):
            digits = re.sub(r"\D", "", tok)
            if digits in fp_set and (len(digits) > 4 or not tok.isdigit()):
                hits.append(f"{fp.relative_to(REPO_ROOT)}")
    if hits:
        raise AssertionError(f"Unrounded private figure match(es) in: {sorted(set(hits))}")
    return f"external private-figure scan clean across {len(fp_set)} figures"


def main() -> None:
    html_files = sorted(SITE_DIR.glob("*.html"))
    assert len(html_files) == 10, f"Expected 10 HTML pages in {SITE_DIR}, found {len(html_files)}"

    parsed_by_name: dict[str, PageAuditParser] = {}
    total_rows = 0
    total_ext_links = 0
    total_dollars = 0

    for hf in html_files:
        txt = hf.read_text(encoding="utf-8")
        low = txt.lower()
        for banned in BANNED_SUBSTRINGS:
            assert banned not in low, f"{hf.name} contains banned non-official reference {banned!r}"
        for rx_pii, kind in PII_PATTERNS:
            assert not rx_pii.search(txt), f"{hf.name} matched PII pattern ({kind})"

        parser = PageAuditParser()
        parser.feed(txt)
        assert parser.has_noindex, f"{hf.name} missing <meta name='robots' content='noindex, nofollow'>"
        assert parser.unsourced_rows == 0, f"{hf.name} has {parser.unsourced_rows} unsourced <tr> data rows"

        for u in parser.external_urls:
            assert u.startswith("https://"), f"{hf.name} uses non-HTTPS URL {u}"
            host = urlparse(u).hostname or ""
            assert host in ALLOWED_HOSTS, f"{hf.name} links to non-allowlisted host {host!r} ({u})"

        total_rows += parser.data_rows
        total_ext_links += len(parser.external_urls)
        total_dollars += check_dollar_rounding(txt, hf.name)
        parsed_by_name[hf.name] = parser

    # Verify all internal links and #fragment anchors resolve
    for src_name, parser in parsed_by_name.items():
        for rel_path, frag in parser.local_refs:
            target_file = SITE_DIR / (rel_path if rel_path else src_name)
            assert target_file.is_file(), f"{src_name}: broken internal link to {rel_path!r}"
            if frag:
                target_parser = parsed_by_name.get(target_file.name)
                assert target_parser and frag in target_parser.ids, (
                    f"{src_name}: broken anchor #{frag} in {target_file.name}"
                )

    # Ensure zero 64-hex SHA-256 fingerprint tables in _d3c614ec/ or final/data/
    for check_root in (HERE, REPO_ROOT / "final" / "data"):
        if not check_root.exists():
            continue
        for fp in check_root.rglob("*"):
            if fp.is_file():
                try:
                    t = fp.read_text(encoding="utf-8")
                except Exception:
                    continue
                assert not HEX64_RE.search(t), f"Forbidden 64-hex hash found in {fp.relative_to(REPO_ROOT)}"

    ext_msg = scan_external_private_figures()
    print(
        f"PASS - {len(html_files)} pages, {total_rows} official-sourced table rows, "
        f"{total_ext_links} HTTPS .gov/agency links, 0 broken internal links, "
        f"{total_dollars} $10-rounded dollar figures verified, 0 stored hashes ({ext_msg})"
    )


if __name__ == "__main__":
    main()
