"""Verify the packaged executable and all included PE binaries."""
import argparse
import json
from pathlib import Path
import struct


def architecture(path):
    with path.open('rb') as stream:
        if stream.read(2) != b'MZ':
            raise ValueError(f'{path}: missing DOS signature')
        stream.seek(0x3C)
        offset = struct.unpack('<I', stream.read(4))[0]
        stream.seek(offset)
        if stream.read(4) != b'PE\0\0':
            raise ValueError(f'{path}: missing PE signature')
        return struct.unpack('<H', stream.read(2))[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    root = args.folder
    exe = root / 'Velqora PDF.exe'
    if not exe.is_file() or not list(root.rglob('qwindows.dll')):
        raise SystemExit('The executable or Windows Qt plugin is missing.')
    binaries = sorted(
        path for path in root.rglob('*')
        if path.is_file() and path.suffix.lower() in ('.exe', '.dll', '.pyd')
    )
    for path in binaries:
        if architecture(path) != 0x8664:
            raise SystemExit(f'{path} is not AMD64.')
    args.report.write_text(json.dumps({
        'status': 'passed',
        'architecture': 'AMD64',
        'binaries': [path.relative_to(root).as_posix() for path in binaries],
    }, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
