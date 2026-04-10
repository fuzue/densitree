#!/usr/bin/env Rscript
# Run FlowSOM on benchmark datasets for comparison with densitree.
#
# Usage:
#   Rscript run_flowsom.R <input_csv> <n_clusters> <output_csv>
#
# Input CSV: rows = cells, columns = markers (no label column).
# Output CSV: single column "label" with cluster assignments.
#
# Requirements:
#   install.packages("BiocManager")
#   BiocManager::install("FlowSOM")
#   install.packages("jsonlite")

suppressPackageStartupMessages({
    library(FlowSOM)
    library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
    cat("Usage: Rscript run_flowsom.R <input_csv> <n_clusters> <output_csv>\n")
    quit(status = 1)
}

input_csv <- args[1]
n_clusters <- as.integer(args[2])
output_csv <- args[3]

cat("Loading data from:", input_csv, "\n")
data <- as.matrix(read.csv(input_csv, header = TRUE))
cat("  Cells:", nrow(data), " Markers:", ncol(data), "\n")

# Arcsinh transform (cofactor=5 for CyTOF)
data_t <- asinh(data / 5)

cat("Running FlowSOM with", n_clusters, "metaclusters...\n")
t_start <- proc.time()

# FlowSOM needs a flowFrame; create one from the matrix
ff <- flowCore::flowFrame(data_t)

# Run FlowSOM: 10x10 SOM grid -> metaclustering
fsom <- FlowSOM(
    ff,
    colsToUse = seq_len(ncol(data_t)),
    nClus = n_clusters,
    seed = 42
)

labels <- GetMetaclusters(fsom)
elapsed <- (proc.time() - t_start)["elapsed"]

cat("  Done in", round(elapsed, 1), "seconds\n")
cat("  Clusters found:", length(unique(labels)), "\n")

# Save results
result <- data.frame(label = as.integer(labels))
write.csv(result, output_csv, row.names = FALSE)
cat("Saved to:", output_csv, "\n")

# Also save timing
timing <- list(
    method = "FlowSOM_R",
    runtime_s = as.numeric(elapsed),
    n_clusters = length(unique(labels)),
    n_cells = nrow(data)
)
timing_file <- sub("\\.csv$", "_timing.json", output_csv)
write(toJSON(timing, auto_unbox = TRUE, pretty = TRUE), timing_file)
