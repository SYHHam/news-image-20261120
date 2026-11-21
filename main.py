#!/usr/bin/env python3
"""Copy the finished front page to /output/entry.png.

The entry image is built by build_image.py and stored in this repo as
entry.png. This program only copies it to the output directory, using the
standard library only, so two runs write identical bytes.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT = "/output/entry.png"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(SRC, OUT)
    if sha256(SRC) != sha256(OUT):
        raise SystemExit("copy mismatch: output differs from entry.png")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
