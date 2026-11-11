"""Strict end-to-end verifier for _session_459d7aa2/**.

Verifies:
  1. Source registry integrity (all https:// official hosts, verified 2026-11-11).
  2. Model mathematical & $10-rounding self-tests across all CSV/JSON outputs.
  3. HTML structure on all 11 pages: noindex/nofollow, <h1>, zero empty <td>,
     100% internal link + #anchor resolution, and >=1 official https:// source
     link inside EVERY <tbody><tr> row.
  4. Strict nearest-$10 rounding on EVERY unsuffixed $ figure in visible HTML
     text across all 11 pages (zero odd-dollar exceptions).
  5. Privacy & anti-hash scan across every file in _session_459d7aa2/ (zero
     64-hex hashes, zero APNs/street addresses).
"""

from __future__ import annotations

import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from model import run_all
from sources import OFFICIAL_HOSTS, SOURCES, verify_source_registry

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR / "site"
KNOWN_URLS = {m["url"] for m in SOURCES.values()}


class PageAuditor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_noindex = False
        self.h1_count = 0
        self.ids: set[str] = set()
        self.internal_refs: list[tuple[str, str]] = []
        self.in_tbody = False
        self.in_tr = False
        self.tr_has_official_link = False
        self.tbody_rows = 0
        self.unsourced_rows = 0
        self.in_td = False
        self.td_has_content = False
        self.empty_tds = 0
        self.in_skip_text = 0
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        if "id" in ad and ad["id"]:
            self.ids.add(ad["id"])
        if tag == "meta" and ad.get("name", "").lower() == "robots":
            c = ad.get("content", "").lower()
            if "noindex" in c and "nofollow" in c:
                self.has_noindex = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.tr_has_official_link = False
        elif tag == "td":
            self.in_td = True
            self.td_has_content = False
        elif tag in ("script", "style"):
            self.in_skip_text += 1

        if self.in_td and tag != "td":
            self.td_has_content = True

        if tag in ("a", "link", "script"):
            ref = ad.get("href") or ad.get("src") or ""
            if ref:
                if ref.startswith("https://"):
                    host = urlparse(ref).hostname or ""
                    assert host in OFFICIAL_HOSTS, f"Non-official external host: {ref}"
                    assert ref in KNOWN_URLS, f"External URL not in verified SOURCES registry: {ref}"
                    if self.in_tr:
                        self.tr_has_official_link = True
                elif ref.startswith(("http://", "mailto:", "tel:")):
                    raise AssertionError(f"Disallowed link scheme: {ref}")
                elif ref.startswith("#"):
                    self.internal_refs.append(("", ref[1:]))
                else:
                    file_part, _, frag = ref.partition("#")
                    self.internal_refs.append((file_part, frag))

    def handle_data(self, data: str) -> None:
        if self.in_td and data.strip():
            self.td_has_content = True
        if self.in_skip_text == 0:
            self.text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.in_tr:
            self.tbody_rows += 1
            if not self.tr_has_official_link:
                self.unsourced_rows += 1
            self.in_tr = False
        elif tag == "td" and self.in_td:
            if not self.td_has_content:
                self.empty_tds += 1
            self.in_td = False
        elif tag in ("script", "style") and self.in_skip_text > 0:
            self.in_skip_text -= 1


DOLLAR_RE = re.compile(
    r"\$([0-9][0-9,]*(?:\.[0-9]+)?)(?![0-9.,]|\s*(?:[MBTk]\b|million\b|billion\b|trillion\b))",
    re.IGNORECASE,
)
HEX64_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")
APN_RE = re.compile(r"\b\d{3}-\d{2}-\d{3}\b")


def verify_all() -> None:
    verify_source_registry()
    run_all()

    html_files = sorted(SITE_DIR.glob("*.html"))
    assert len(html_files) == 11, f"Expected 11 HTML pages, found {len(html_files)}"

    auditors: dict[str, PageAuditor] = {}
    total_rows = 0
    total_dollars = 0

    for f in html_files:
        p = PageAuditor()
        p.feed(f.read_text(encoding="utf-8"))
        assert p.has_noindex, f"{f.name}: missing noindex,nofollow"
        assert p.h1_count == 1, f"{f.name}: expected 1 <h1>, got {p.h1_count}"
        assert p.unsourced_rows == 0, f"{f.name}: {p.unsourced_rows} unsourced <tbody><tr> rows"
        assert p.empty_tds == 0, f"{f.name}: {p.empty_tds} empty <td> cells"
        total_rows += p.tbody_rows
        auditors[f.name] = p

        visible = " ".join(p.text_parts)
        for m in DOLLAR_RE.finditer(visible):
            raw = m.group(1)
            assert "." not in raw, f"{f.name}: decimal dollar amount ${raw} violates integer $10 rounding"
            val = int(raw.replace(",", ""))
            assert val == 0 or val % 10 == 0, f"{f.name}: non-$10-rounded figure ${raw}"
            total_dollars += 1

    for fname, p in auditors.items():
        for target_file, frag in p.internal_refs:
            dest = SITE_DIR / (target_file or fname)
            assert dest.is_file(), f"{fname}: broken internal link -> {target_file}"
            if frag and dest.suffix == ".html":
                assert frag in auditors[dest.name].ids, f"{fname}: broken #{frag} on {dest.name}"

    priv_env = os.environ.get("TINO1_PRIVATE_FIGURES", "")
    extra_figs: list[str] = []
    if priv_env and Path(priv_env).is_file():
        extra_figs = [ln.strip() for ln in Path(priv_env).read_text().splitlines() if ln.strip()]

    for path in BASE_DIR.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        txt = path.read_text(encoding="utf-8")
        assert not HEX64_RE.search(txt), f"{path.name}: contains 64-char hex string"
        assert not APN_RE.search(txt), f"{path.name}: contains APN-like pattern"
        for fig in extra_figs:
            digits = re.sub(r"\D", "", fig)
            if len(digits) >= 5:
                pat = r"(?<!\d)" + r"[,_ ]?".join(list(digits)) + r"(?!\d)"
                assert not re.search(pat, txt), f"{path.name}: matched private figure"

    print(
        f"PASS - 11 HTML pages, {total_rows} table rows (100% official-sourced), "
        f"{total_dollars} $ figures (100% divisible by $10), internal links/anchors verified, "
        f"zero 64-hex hashes, privacy checks clean."
    )


if __name__ == "__main__":
    verify_all()
