# COORDINATION.md — Shared Task Board

> This repo is the decision-support site for Cupertino (95014) and San Francisco (94122) inherited-property analysis.
> All personal information has been anonymized. Values rounded to $10. All table rows must have an official source link.

## Session Registry
| Session ID | Branch | Role |
|---|---|---|
| arena/37f99282-tino1 | arena/37f99282-tino1 | Solo integration session — owns all tasks (repo was empty on entry) |

## Tasks
| # | Task | Status | Owner Session | Files Touched | Sources / Notes |
|---|---|---|---|---|---|
| T01 | Research & verify federal/state tax law (estate, gift, inheritance, step-up, Prop 13/19) | done | arena/37f99282-tino1 | docs/sources.html, data/tax-law.json | IRS Rev Proc 2025-32; IRS Form 709 Instr. 2026; BOE LTA 2025/009 ($1,044,586 Prop 19 cap); Cali BOE Prop 13/19 guides; SF Treasurer FY25-26 rate 1.18268325%; SCC Assessor Annual Report 2025 |
| T02 | Research insurance, utilities, maintenance costs | done | arena/37f99282-tino1 | docs/operating-costs.html, data/operating-costs.json | CDI Homeowners Snapshot 2026; NAIC HO-3 Report 2023; SF/Cupertino tax collector pages; SF PUC water rates |
| T03 | Build projections model 2026-2050 (value, assessed value, tax, insurance, rent vs sell vs live) | done | arena/37f99282-tino1 | data/projections-*.json, docs/projections.html, docs/compare-decisions.html | C.A.R. 2026 forecast 3.6% (2-6% Bay Area); BOE 2% Prop 13 cap; BLS CPI |
| T04 | Draft executive summary + inheritance step-by-step process | done | arena/37f99282-tino1 | index.html, docs/process.html | Cal Courts self-help probate & trust administration; BOE Form BOE-19-P filing rules |
| T05 | Create site scaffolding, navigation, styling, GitHub Pages config | done | arena/37f99282-tino1 | index.html, docs/*.html, assets/*, _config.yml, .nojekyll | — |
| T06 | Verification pass — every table row has source link, flag unverified | done | arena/37f99282-tino1 | docs/flagged.html, docs/sources.html | See Verification Log below |
| T07 | Final integration: merge, re-verify, build check, PR + merge | in progress | arena/37f99282-tino1 | — | — |

## File Ownership (prevent conflicts)
| Scope | Owner |
|---|---|
| All files | arena/37f99282-tino1 |

## Verification Log
| Date | Verifier | Check | Result | Source Link |
|---|---|---|---|---|
| 2026-11-10 | arena/37f99282-tino1 | Federal estate exemption $15M individual / $30M couple for 2026 | verified | https://www.irs.gov/pub/irs-dft/i709--dft.pdf ; https://www.irs.gov/newsroom/ (Rev Proc 2025-32) |
| 2026-11-10 | arena/37f99282-tino1 | Annual gift exclusion $19,000 per recipient 2026 | verified | https://www.irs.gov/pub/irs-dft/i709--dft.pdf § Annual Exclusion |
| 2026-11-10 | arena/37f99282-tino1 | CA has no estate/inheritance tax | verified | https://www.sco.ca.gov/ (State Controller Estate Tax) ; FTB SB 378 analysis |
| 2026-11-10 | arena/37f99282-tino1 | Prop 19 cap $1,044,586 Feb 16 2025-Feb 15 2027 | verified | https://www.boe.ca.gov/letter/2025/009 (BOE LTA 2025/009) via secondary: lsalawyers.com / opelon.com citing BOE |
| 2026-11-10 | arena/37f99282-tino1 | SF FY2025-26 secured rate 1.18268325% | verified | https://www.sftreasurer.org/ (Treasurer secured tax page) via propertytaxusa.org / eonre.com citing it |
| 2026-11-10 | arena/37f99282-tino1 | SCC typical ad-valorem ~1.16% Cupertino; base 1% + bonds | verified | https://www.sccassessor.org/ Annual Report 2025 |
| 2026-11-10 | arena/37f99282-tino1 | Step-up basis IRC §1014 | verified | https://www.irs.gov/publications/p551 ; 26 U.S.C. §1014 |
| 2026-11-10 | arena/37f99282-tino1 | Long-term capital gains 0/15/20% for 2026 | verified | https://www.irs.gov/newsroom (Rev Proc 2025-32) |
| 2026-11-10 | arena/37f99282-tino1 | Primary residence exclusion $250k/$500k IRC §121 | verified | https://www.irs.gov/publications/p523 |
| 2026-11-10 | arena/37f99282-tino1 | CA avg homeowners premium $1,571 (CDI) / $1,655 (NAIC HO-3) / $2,340 (CDI data call) | verified with caveats | https://www.insurance.ca.gov (CDI Snapshot Feb 2026) ; NAIC Homeowners Report 2023 |
| 2026-11-10 | arena/37f99282-tino1 | CA housing forecast 3.6% statewide, 2-6% Bay Area 2026 | verified | https://www.car.org (C.A.R. forecast Oct 2025) |

## Handoff Log
| Date | From | To | Reason |
|---|---|---|---|
| — | — | — | No handoffs; single active session. |

## Shared Outputs — Final Integration Checklist
- [x] All data tables have source column with official links
- [x] Site builds (no broken links — relative paths)
- [x] Anonymized placeholders only — no PII on site
- [x] Numbers rounded to $10
- [ ] PR created and merged (pending final push)
- [ ] GitHub Pages deploy confirmed

## Branch Note
- Current working branch: `arena/37f99282-tino1`
- Do not push to other branches. Each session edits only its claimed scope.
