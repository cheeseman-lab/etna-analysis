#!/usr/bin/env python3
"""
Copy input_sbs to a new directory with sanitized filenames.
Replace commas with underscores in all filenames.
Parallelized with multiprocessing.
"""

import os
import shutil
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

SRC = Path('/archive/cheeseman/ops_data/etna/input_sbs')
DST = Path('/lab/ops_analysis_hdd/cheeseman/etna-analysis/input_sbs_renamed')

if not SRC.exists():
    print(f"ERROR: Source directory not found: {SRC}")
    sys.exit(1)

print(f"Copying from: {SRC}")
print(f"Copying to:   {DST}")
print()

DST.mkdir(parents=True, exist_ok=True)

# Collect all files
all_files = list(SRC.rglob('*.nd2'))
total = len(all_files)
print(f"Total files to copy: {total:,}")
print()

def copy_file_with_rename(src_file):
    """Copy single file with renamed destination."""
    rel_path = src_file.relative_to(SRC)
    parts = list(rel_path.parts)
    parts[-1] = parts[-1].replace(',', '_')

    dst_file = DST / Path(*parts)
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)

    return dst_file.name

# Parallel copy with 8 workers
copied = 0
max_workers = 8

with ProcessPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(copy_file_with_rename, f): f for f in all_files}

    for i, future in enumerate(as_completed(futures), 1):
        try:
            dst_name = future.result()
            copied += 1

            if i % 5000 == 0 or i == total:
                pct = 100 * i / total
                print(f"  [{i:6d}/{total:6d}] {pct:5.1f}% — {dst_name[:80]}")
        except Exception as e:
            print(f"ERROR copying {futures[future]}: {e}")

print()
print(f"✓ Copied {copied:,} files with sanitized names")
print(f"Ready to upload from: {DST}")
