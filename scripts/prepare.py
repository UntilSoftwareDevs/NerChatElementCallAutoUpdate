"""Download the stable upstream artifact, verify its digest, and apply our overlay."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.work'
DIST = ROOT / 'dist'


def main():
    WORK.mkdir(exist_ok=True)
    release = json.loads(subprocess.check_output([
        'gh', 'api', 'repos/element-hq/element-call/releases/latest']))
    tag = release['tag_name']
    if not re.fullmatch(r'v\d+\.\d+\.\d+', tag) or release['draft'] or release['prerelease']:
        raise ValueError('Expected a stable release')
    name = f'element-call-{tag[1:]}.tar.gz'
    asset = next(a for a in release['assets'] if a['name'] == name)
    digest = asset.get('digest', '')
    if not re.fullmatch(r'sha256:[a-f0-9]{64}', digest):
        raise ValueError('Upstream SHA-256 digest is required')
    archive = WORK / name
    if not archive.exists() or 'sha256:' + hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
        subprocess.run(['gh', 'release', 'download', tag, '--repo', 'element-hq/element-call',
                        '--pattern', name, '--dir', str(WORK), '--clobber'], check=True)
    if 'sha256:' + hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
        raise ValueError('Release digest mismatch')
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or '\\' in member.name or ':' in member.name:
                raise ValueError('Unsafe archive path')
            if not (member.isfile() or member.isdir()):
                raise ValueError('Archive links and special files are forbidden')
        indexes = [PurePosixPath(m.name) for m in members if m.isfile() and PurePosixPath(m.name).name == 'index.html']
        if not indexes:
            raise ValueError('No index.html in release')
        prefix = min(indexes, key=lambda p: len(p.parts)).parent
        if DIST.exists():
            shutil.rmtree(DIST)
        DIST.mkdir()
        for member in members:
            path = PurePosixPath(member.name)
            try:
                relative = path.relative_to(prefix)
            except ValueError:
                continue
            target = DIST.joinpath(*relative.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
    shutil.copytree(ROOT / 'overlay', DIST, dirs_exist_ok=True)
    shutil.copyfile(ROOT / 'edgeone.json', DIST / 'edgeone.json')
    metadata = {'tag': tag, 'asset': asset['browser_download_url'], 'sha256': digest[7:]}
    for path in (WORK / 'release.json', DIST / 'nerchat-release.json'):
        path.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    if not (DIST / 'index.html').is_file():
        raise ValueError('Missing entrypoint')
    print(f'Prepared Element Call {tag}; SHA-256 verified')


if __name__ == '__main__':
    main()
