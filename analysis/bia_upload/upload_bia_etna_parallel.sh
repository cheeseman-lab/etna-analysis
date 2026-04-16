#!/bin/bash
#SBATCH --job-name=mdiberna_bia_etna_v3
#SBATCH --partition=20
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=21-00:00:00
#SBATCH --array=1-31%5
#SBATCH --output=/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload/logs/slurm/mdiberna_bia_etna_v3_%a_%j.out
#SBATCH --error=/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload/logs/slurm/mdiberna_bia_etna_v3_%a_%j.err

# =============================================================================
# Re-upload to BioStudies — 31 tasks, 5 concurrent max
#
# Task mapping:
#   1     → input_ph/plate_2/round_1 (incomplete from v2 task 4)
#   2–16  → input_sbs/plate_1/c1–c15 (renamed, commas → underscores)
#   17–31 → input_sbs/plate_2/c1–c15 (renamed, commas → underscores)
#
# IMPORTANT: Run AFTER copy_rename_input_sbs job completes.
# input_sbs files are uploaded from the renamed copy, overwriting the
# comma-named originals on BIA.
# =============================================================================

set -uo pipefail

BIA_USER="bs-upload"
BIA_SERVER="fasp.ebi.ac.uk"
BIA_PORT=33001
BIA_BASE="/d9/610818-a855-441f-9bd4-5e5304a7ed1b-a30517/etna"
export ASPERA_SCP_PASS="vsr5nW7Y"

ARCHIVE_BASE="/archive/cheeseman/ops_data/etna"
RENAMED_BASE="/lab/ops_analysis_hdd/cheeseman/etna-analysis/input_sbs_renamed"
LOG_DIR="/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload/logs/aspera_manifests"
RATE_LIMIT="2500M"

mkdir -p "${LOG_DIR}"
eval "$(conda shell.bash hook)" && conda activate aspera

T=${SLURM_ARRAY_TASK_ID}

# Map task ID to source and destination
if [[ ${T} -eq 1 ]]; then
    # Incomplete input_ph from v2
    SRC="${ARCHIVE_BASE}/input_ph/plate_2/round_1"
    DEST="${BIA_BASE}/input_ph/plate_2/"
    LABEL="input_ph/plate_2/round_1"
else
    # Renamed input_sbs
    T_SBS=$(( T - 1 ))
    PLATE_NUM=$(( (T_SBS - 1) / 15 + 1 ))
    CYCLE_NUM=$(( (T_SBS - 1) % 15 + 1 ))
    PLATE="plate_${PLATE_NUM}"
    CYCLE="c${CYCLE_NUM}"
    SRC="${RENAMED_BASE}/${PLATE}/${CYCLE}"
    DEST="${BIA_BASE}/input_sbs/${PLATE}/"
    LABEL="input_sbs/${PLATE}/${CYCLE} (renamed)"
fi

echo "===================================================================="
echo "BioStudies Upload v3: etna ${LABEL} (task ${T})"
echo "Started: $(date)"
echo "  src:  ${SRC}"
echo "  dest: ${DEST}"
echo "===================================================================="

which ascp
ascp --version 2>&1 | head -1

run_ascp() {
    local src="$1"
    local dest="$2"
    echo ""
    echo "Uploading: ${src} -> ${dest}"
    set +e
    ascp \
        -k 1 \
        -Q \
        -T \
        -l "${RATE_LIMIT}" \
        -P "${BIA_PORT}" \
        -r \
        --file-manifest=text \
        --file-manifest-path="${LOG_DIR}" \
        "${src}" \
        "${BIA_USER}@${BIA_SERVER}:${dest}" 2>&1
    local ec=$?
    set -e
    echo "ascp exit code: ${ec}"
    return ${ec}
}

if [[ -d "${SRC}" ]]; then
    run_ascp "${SRC}" "${DEST}"
else
    echo "ERROR: ${SRC} not found — is copy_rename job complete?"
    exit 1
fi

echo ""
echo "===================================================================="
echo "Task ${T} (${LABEL}) complete"
echo "Ended: $(date)"
echo "===================================================================="
