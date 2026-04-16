#!/bin/bash
# =============================================================================
# Pre-create etna directory tree on BioStudies before parallel upload.
# Run this interactively ONCE before submitting upload_bia_etna_v2.sh.
# Creates: etna/input_ph/plate_1/, etna/input_ph/plate_2/,
#          etna/input_sbs/plate_1/, etna/input_sbs/plate_2/
# =============================================================================

set -euo pipefail

BIA_USER="bs-upload"
BIA_SERVER="fasp.ebi.ac.uk"
BIA_PORT=33001
BIA_DEPOSIT="/d9/610818-a855-441f-9bd4-5e5304a7ed1b-a30517"
export ASPERA_SCP_PASS="vsr5nW7Y"

TMPDIR="/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload/.etna_tree_tmp"

eval "$(conda shell.bash hook)" && conda activate aspera

echo "Creating local directory tree..."
mkdir -p \
    "${TMPDIR}/input_ph/plate_1" \
    "${TMPDIR}/input_ph/plate_2" \
    "${TMPDIR}/input_sbs/plate_1" \
    "${TMPDIR}/input_sbs/plate_2"

echo "Uploading input_ph structure to BIA..."
ascp -r -P "${BIA_PORT}" -T \
    "${TMPDIR}/input_ph" \
    "${BIA_USER}@${BIA_SERVER}:${BIA_DEPOSIT}/etna/" 2>&1

echo "Uploading input_sbs structure to BIA..."
ascp -r -P "${BIA_PORT}" -T \
    "${TMPDIR}/input_sbs" \
    "${BIA_USER}@${BIA_SERVER}:${BIA_DEPOSIT}/etna/" 2>&1

echo "Done. Directory tree created on BIA."
echo "Expected: etna/input_ph/plate_1/, etna/input_ph/plate_2/,"
echo "          etna/input_sbs/plate_1/, etna/input_sbs/plate_2/"
rm -rf "${TMPDIR}"
