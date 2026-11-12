"""Fail closed: exact file paths AND byte identity for Jekyll's public output."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
repo = Path(__file__).resolve().parent.parent
names = {'index.html','decision.html','projection.html','stress.html','process.html','law.html','costs.html','flagged.html','style.css'}
expected = {'index.html'} | {'privacy-site/public/'+name for name in names}
actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
assert actual == expected, f'Unexpected or missing published files: {actual ^ expected}'
for name in expected:
    assert (root/name).read_bytes() == (repo/name).read_bytes(), f'Published content changed: {name}'
assert b'privacy-site/public/index.html' in (root/'index.html').read_bytes()
print(f'PASS: exact publication allowlist and source-byte identity, {len(actual)} files')
