# Etna OPS Screen Analysis (v1.0.0)

Reanalysis of the combinatorial optical pooled CRISPR screen (CROPseq-multi) from Walton et al. (Nature Biotechnology), processed with [brieflow v1.2.0](https://github.com/cheeseman-lab/brieflow).

## Screen Overview

| Parameter | Value |
|-----------|-------|
| Cell line | HeLa (doxycycline-inducible Cas9) |
| Library | CROPseq-multi-v2 (CSMv2), 6,000 constructs |
| Targets | 360 essential genes + 280 gene combinations (combinatorial CRISPR-KO) |
| Guides per gene | 4 |
| Plates | 2 (9 wells total) |
| SBS cycles | 15 (3 iBAR1 recombination + 12 iBAR2 mapping) |
| Phenotype rounds | 2 (10 markers, 9 final channels) |
| Phenotype markers | DAPI, Ki-67, COX IV, Cleaved Caspase-3, WGA, α-Tubulin, Vimentin, γH2AX, Phalloidin |
| Microscope | Nikon Ti2 inverted epifluorescence |

## Analysis

Raw data was processed end-to-end with [brieflow](https://github.com/cheeseman-lab/brieflow), covering preprocessing, SBS decoding, phenotype feature extraction, merge, aggregate, and clustering steps. Configuration notebooks and Slurm scripts are in `analysis/`.

## Data

Raw imaging data (ND2 format) is archived at [BioImage Archive S-BIAD3248](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD3248). Brieflow outputs are stored at `/lab/ops_analysis_hdd/cheeseman/etna-analysis/`. Source data used for figure generation is in `analysis/source_data/`.

## Citation

> *Citation will be added upon publication.*
