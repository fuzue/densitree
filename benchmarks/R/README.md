# R Benchmarks

These scripts run R-based clustering methods for comparison with densitree.

## Requirements

```r
install.packages("BiocManager")
BiocManager::install("FlowSOM")
BiocManager::install("flowCore")
install.packages("jsonlite")

# Optional: SPADE (may be archived)
install.packages("devtools")
devtools::install_github("nolanlab/spade2")
```

## Usage

### Prepare data

First, export the benchmark dataset from Python:

```bash
cd benchmarks
python -c "
from download_data import load_dataset
import pandas as pd
import numpy as np
X, labels, markers = load_dataset('Levine_32dim')
pd.DataFrame(X, columns=markers).to_csv('data/Levine_32dim_markers.csv', index=False)
np.savetxt('data/Levine_32dim_labels.csv', labels, fmt='%d', header='label', comments='')
"
```

### Run FlowSOM

```bash
Rscript R/run_flowsom.R data/Levine_32dim_markers.csv 14 results/flowsom_levine.csv
```

### Run SPADE (R)

```bash
Rscript R/run_spade.R data/Levine_32dim_markers.csv 14 results/spade_r_levine.csv
```

### Compare with Python results

```bash
python compare_with_r.py results/flowsom_levine.csv data/Levine_32dim_labels.csv FlowSOM_R
```
