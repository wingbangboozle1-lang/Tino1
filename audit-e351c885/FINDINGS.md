# Findings — fresh-session close-out pass (session `arena/e351c885-tino1`, 2026-11-13 UTC)

Nothing below blocks publication or the merge. Items F1–F3 are recorded so the owner can
review them; F4–F7 are process records.

## Observations and irregularities

- **F1 — County page wording on the Prop 19 cap cadence.** The Santa Clara County Assessor's
  Prop 19 page says the $1 million allowance "will be adjusted annually beginning in 2023",
  while BOE Letter to Assessors 2025/009 (the implementing authority) says the adjustment
  happens **every other February 16** ($1,000,000 → $1,022,600 → $1,044,586). The site cites
  and follows the BOE letter, which is correct. No site change needed. Source:
  https://asr.santaclaracounty.gov/tax-savings/transferring-your-assessed-value/parent-to-child-2
  vs https://www.boe.ca.gov/proptaxes/pdf/lta25009.pdf
- **F2 — SF Treasurer page refreshed to FY2026-27.** The live page now publishes the FY2026-27
  secured rate 1.18162182% (earlier passes recorded the FY2025-26 rate 1.18268325%). The
  model's `rate_sf` already equals the current published rate, so no change is needed; the
  superseded figure in older board notes is not a defect.
- **F3 — Model projects the Prop 19 cap annually.** `final/model.py` compounds the
  $1,044,586 cap every year by the FHFA California HPI path, whereas BOE adjusts it
  **biennially** (every other February 16). Compounding annually at the same average growth
  gives a slightly different projected cap for a 2040s transfer than biennial steps would.
  The direction of the difference is small relative to the figures at stake and the model
  documents the mechanism (`cap *= 1 + g_ca`); recorded as a methodology note for owner
  review, not a defect. If the owner wants the biennial cadence replicated exactly, that is a
  small change to `final/model.py` (request it via the board; do not edit while other
  sessions hold claims on shared files).
- **F4 — Branch alignment.** This session's branch was an orphan snapshot of `551179b` with
  no shared history, so it was aligned in place to `origin/main` (`e4f7d29` at the time) by
  `git reset --hard` before any work; recorded in the claim entry. One accidental push of the
  pre-rebase tip to the (then-new) remote branch was corrected immediately with
  `--force-with-lease`; only this session's single claim commit was ever on that ref.
- **F5 — Board conflicts during claim.** PR #77 landed mid-rebase; the append-only board
  conflict was resolved by union (main's PR #74 record kept in full, this session's claim
  appended). Nothing discarded.
- **F6 — Privacy.** All four fetched live pages contain placeholder people only; no name,
  street address, e-mail, phone or parcel-number pattern appeared. This audit directory is
  excluded from Jekyll by the regenerated `_config.yml` (same mechanism as
  `session-5ea93a0e/`), and `final/published.txt` allowlist is unchanged (39 files). The
  durable repository/history exposures remain owner decisions (flags P01/P02) and are not
  resolvable by any session.
- **F7 — Gates.** All local gates green on the final audited tree (origin/main `5ffe94a` — PRs #73-#79 — plus this session's commits): `privacy-site/build.py` reproducible (no diff), `privacy-site/check.py` PASS (11 pages, **318** rows), unittest 8/8, `final/publish.py --check` PASS (**13 files**, privacy-first boundary), `final/check.py .` PASS (25 pages, **983** sourced rows, **2,522** links, **2,398** dollar figures $10-clean, 51 model paths), `final/integrate.py` clean. Two earlier gate runs during concurrent merges (938/2451/2375 pre-#75; 966/2543/2419 post-#75) are superseded; raw output of the final run in GATES.txt. Three board conflicts during this session (PRs #75, #77, #78 landing concurrently) were all resolved by union; every other session's entry is preserved (verified by count greps).

- **F8 — Board corruption found on main and repaired here.** `origin/main`'s `COORDINATION.md`
  (tip `2b727aa`, merged via PR #81) contained unresolved conflict-marker lines
  (`<<<<<<< HEAD` / `=======` / `>>>>>>> origin/main`) inside the da3f2b99 close-out region.
  This session's merge inherited the corruption as a malformed hunk; the markers were removed
  with a line-level repair, all sessions' entries verified present by content probes
  (da3f2b99 D-0…D-6 close-out, f8de1d0b F8 entry, 022b1ea7 record, owner-analysis-2026, this
  session's entry), and the repaired board is what this PR proposes to merge. No published
  page is affected (the board is Jekyll-excluded), but future sessions should diff the board
  for stray markers before appending.

- **F9 — Publication boundary changed mid-session (PR #79, merged as `5ffe94a`).** The final-integrator
  session `arena/fdd454a6` moved the Pages allowlist from 39 files (dual edition) to **13 files
  (privacy-first)**: a generic `index.html` plus `privacy-site/public/*`. The numeric edition
  (`summary.html` etc.) remains in the repository, fully gated by `final/check.py`, but is no longer
  published to GitHub Pages. This is consistent with the owner's stated top priority (personal
  information privacy) and with the long-standing G01/G02 and P01/P02 owner decisions recorded on the
  Flagged for Review page; it is owner-reversible via `final/publish.py` (the generator is the single
  source of truth). Consequences for this pack: `LIVE-SITE.md` is a point-in-time record of the earlier
  dual-edition deployment (timestamps preserved) and `summary.html` will stop being served after this
  PR merges; the official-source reads in `VERIFICATION.md` are unaffected. The site now presents the
  decision framework and official facts without household figures; the owner's brief also asked for
  the rounded-figures analysis on the site, so the boundary choice stays an open owner decision, not
  something this session reverses.

## What this pass did not do

- It did not edit any published page, the model, the flags register, or any file claimed by
  the concurrently-active sessions (PR #75 scopes: `final/build.py`, `final/flags.py`,
  `flagged.html`, `index.html`, `review.html`, `style.css`, `suggestions.html`,
  `verification.html`).
- It did not re-read all ~75 register entries (see VERIFICATION.md).
- It did not resolve any open flag; flags stay open for the owner by design.
