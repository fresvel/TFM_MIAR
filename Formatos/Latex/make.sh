#! /bin/bash
set -euo pipefail

IMAGE="viu-tex"
BUILD_DIR="build"
OUT_DIR="out"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1 || [ "${BUILD_IMAGE:-0}" = "1" ]; then
  docker build -t "$IMAGE" -f docker/Dockerfile docker
fi

mkdir -p "$BUILD_DIR" "$OUT_DIR"

docker run --rm -u "$(id -u)":"$(id -g)" -v "$(pwd)":/workdir -w /workdir "$IMAGE" \
  bash -lc "xelatex -interaction=nonstopmode -halt-on-error -output-directory=$BUILD_DIR main.tex && \
  bibtex $BUILD_DIR/main && \
  xelatex -interaction=nonstopmode -halt-on-error -output-directory=$BUILD_DIR main.tex && \
  xelatex -interaction=nonstopmode -halt-on-error -output-directory=$BUILD_DIR main.tex"

cp "$BUILD_DIR/main.pdf" "$OUT_DIR/main.pdf"
gs -o "$OUT_DIR/report.pdf" -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 "$OUT_DIR/main.pdf"
