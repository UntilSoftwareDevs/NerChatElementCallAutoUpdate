"""Check the deployed artifact rather than treating an upload as acceptance."""
import json
from pathlib import Path
import sys
import urllib.request
import urllib.parse

root = Path(__file__).resolve().parents[1]
target = sys.argv[1] if len(sys.argv) > 1 else None
if target == 'production':
    target = 'https://meet.neboer.site'
elif target == 'preview':
    target = json.loads((root / f'.work/{target}.json').read_text())['url']
if target and urllib.parse.urlsplit(target).query:
    # The platform authorizes the source IP when the signed root URL is visited.
    with urllib.request.urlopen(target, timeout=30) as response:
        response.read()
    base = urllib.parse.urlsplit(target)
    target = urllib.parse.urlunsplit((base.scheme, base.netloc, '', '', ''))

def read(path):
    if target:
        base = urllib.parse.urlsplit(target)
        url = urllib.parse.urlunsplit((base.scheme, base.netloc, '/' + path, base.query, ''))
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    return (root / 'dist' / path).read_bytes()

assert b'<html' in read('index.html').lower()
assert json.loads(read('config.json')) == json.loads((root / 'overlay/config.json').read_text())
assert json.loads(read('nerchat-release.json')) == json.loads((root / '.work/release.json').read_text())
if target:
    assert b'<html' in read('room/nerchat-route-check').lower(), 'SPA fallback missing'
print('Verified HTML, NerChat configuration, release identity and routing' if target else 'Verified local artifact')
