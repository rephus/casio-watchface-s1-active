#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build-casio-face.py
mkdir -p watchfaces/casio-time/output dist
# Locally prepared Wine 8 + wine32 + Wine Mono 8.0 image; no network during build.
docker image inspect s1-face-builder:local >/dev/null
rm -f watchfaces/casio-time/output/CasioTime.face
docker run --rm --network none --platform linux/amd64 \
  -e WINEPREFIX=/tmp/face-wine -e WINEARCH=win32 \
  -v "$PWD/.toolchain/easyface-compiler:/compiler:ro" \
  -v "$PWD/watchfaces/casio-time:/face" \
  --entrypoint sh s1-face-builder:local -c \
  'cd /compiler && xvfb-run -a /usr/lib/wine/wine Compiler.exe -b Z:\\face\\CasioTime.fprj Z:\\face\\output CasioTime.face 1731859101'
python3 scripts/package-casio-face.py
