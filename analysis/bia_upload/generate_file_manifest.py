"""
Generate BioImage Archive file list manifest from brieflow sample TSVs.
Converts local archive paths to BIA-relative paths, combined SBS + phenotype.
"""

import pandas as pd
from pathlib import Path

CONFIG_DIR = Path("/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/config")
OUT_DIR = Path("/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload")

LOCAL_PREFIXES = [
    "/archive/cheeseman/ops_data/etna/",
    "/lab/ops_data/etna/",
]
BIA_PREFIX = "etna/"


def convert_path(fp: str) -> str:
    for prefix in LOCAL_PREFIXES:
        if fp.startswith(prefix):
            return BIA_PREFIX + fp[len(prefix):]
    return fp


def sanitize_filename(fp: str) -> str:
    """Replace commas with underscores in filenames (BIA/S3 requirement)."""
    parts = fp.rsplit("/", 1)
    if len(parts) == 2:
        return parts[0] + "/" + parts[1].replace(",", "_")
    return fp.replace(",", "_")


sbs = pd.read_csv(CONFIG_DIR / "sbs_samples.tsv", sep="\t")
sbs["sample_fp"] = sbs["sample_fp"].apply(convert_path).apply(sanitize_filename)
sbs["data_type"] = "sbs"

ph = pd.read_csv(CONFIG_DIR / "phenotype_samples.tsv", sep="\t")
ph["sample_fp"] = ph["sample_fp"].apply(convert_path)
ph["data_type"] = "phenotype"

combined = pd.concat([sbs, ph], ignore_index=True)
combined = combined.rename(columns={"sample_fp": "Files"})
combined.to_csv(OUT_DIR / "file_manifest_bia.tsv", sep="\t", index=False)

assert not combined["Files"].str.startswith("/").any(), "Manifest has absolute paths!"
print(f"Generated {len(combined)} rows ({len(sbs)} sbs + {len(ph)} phenotype)")
print(f"  Output: {OUT_DIR / 'file_manifest_bia.tsv'}")
