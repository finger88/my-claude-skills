#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrapper around markitdown to correctly read PPTX content on Windows.
Fixes GBK stdout encoding issues by forcing UTF-8 and writing to a file.
"""

import sys
import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Extract text from PPTX")
    parser.add_argument("pptx", help="Path to the .pptx file")
    parser.add_argument("-o", "--output", help="Output markdown file (default: print to stdout)")
    args = parser.parse_args()

    env = os.environ.copy()
    # Force UTF-8 for Python stdio on Windows
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = [sys.executable, "-m", "markitdown", args.pptx]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)

    if result.returncode != 0:
        print("Error:", result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    content = result.stdout

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved to {args.output}")
    else:
        # On Windows, re-encode to the console's code page to avoid gibberish
        if sys.platform == "win32" and sys.stdout.isatty():
            sys.stdout.buffer.write(content.encode("utf-8"))
        else:
            print(content)

if __name__ == "__main__":
    main()
