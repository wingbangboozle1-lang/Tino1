# GitHub Pages source

This directory is served by GitHub Pages as the live analysis site.

- `index.html` — executive summary / landing page
- 10 subpages by category
- `assets/style.css` — single stylesheet, no JavaScript anywhere
- `data/` — the generated datasets linked from the Sources page

Everything here is generated from `/tools` against `/data`. Do not hand-edit the HTML;
regenerate with `python3 tools/build_data.py && python3 tools/gen.py && python3 tools/render.py`
and validate with `python3 tools/check.py`.
