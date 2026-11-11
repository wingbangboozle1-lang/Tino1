# verify-4395771d — independent register, reference model and staged site

Session `4395771d`'s own directory. Nothing here edits another session's file.

| Path | What it is |
|---|---|
| `facts/*.csv` | Fact register. Each row was read on the official page on 2026-11-11: value, link, the wording found, status. Unconfirmed values are blank. `_schema.md` explains the columns. |
| `data/*.csv` | Historical series used for the black-swan analysis (FHFA home prices, California CPI and Prop 13 factors, US CPI, US stock/bill/bond/home returns, Japan). Each file names its source in its header. |
| `model/model.py` | The model. Standard library only. All assumptions are in one block at the top. |
| `model/out/` | Model output (CSV and `summary.json`). |
| `tools/build_site.py` | Builds the site from the register and the model output. No figure is typed by hand. |
| `tools/check_site.py` | Checks the built site: links, a source on every table row, $10 rounding, privacy patterns, no third-party resources. |
| `site/` | The built site (10 pages). |

Reproduce:

```
python3 verify-4395771d/model/model.py
python3 verify-4395771d/tools/build_site.py            # or: build_site.py <output_dir>
python3 verify-4395771d/tools/check_site.py            # or: check_site.py <output_dir>
```

Privacy: owner-supplied figures appear rounded to $10 only. The checker is rule-based and holds no list of the owner's figures.
