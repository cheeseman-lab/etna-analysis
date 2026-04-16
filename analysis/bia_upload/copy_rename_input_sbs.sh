#!/bin/bash
#SBATCH --job-name=mdiberna_rename_input_sbs
#SBATCH --partition=20
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=4-00:00:00
#SBATCH --output=/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload/logs/slurm/copy_rename_%j.out
#SBATCH --error=/lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload/logs/slurm/copy_rename_%j.err

set -euo pipefail

echo "======================================================================"
echo "Copy input_sbs with renamed files (commas → underscores)"
echo "Started: $(date)"
echo "======================================================================"

python3 /lab/ops_analysis_hdd/cheeseman/etna-analysis/analysis/bia_upload/copy_rename_input_sbs.py

echo ""
echo "======================================================================"
echo "Copy complete"
echo "Ended: $(date)"
echo "======================================================================"
