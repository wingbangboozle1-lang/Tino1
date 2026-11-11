"""Fail closed if Jekyll publishes anything outside the allowlist."""
from pathlib import Path
import sys
root = Path(sys.argv[1]); public=Path(__file__).parent/'public'
expected = {'index.html'} | {'privacy-site/public/'+p.name for p in public.iterdir() if p.is_file()}
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
assert actual == expected, f'Unexpected or missing published files: {actual ^ expected}'
for name in expected - {'index.html'}:
 assert (root/name).read_bytes() == (public/Path(name).name).read_bytes(), f'Content changed by Jekyll: {name}'
assert b'privacy-site/public/index.html' in (root/'index.html').read_bytes()
print(f'PASS: exact publication allowlist, {len(actual)} files')
