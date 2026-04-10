#!/usr/bin/env Rscript
# Run R SPADE (spade2) on benchmark datasets for comparison with densitree.
#
# Usage:
#   Rscript run_spade.R <input_csv> <n_clusters> <output_csv>
#
# Requirements:
#   install.packages("devtools")
#   devtools::install_github("nolanlab/spade2")
#   OR
#   BiocManager::install("spade")  # archived, may not be available

suppressPackageStartupMessages({
    library(jsonlite)
})

# Try to load spade2 or spade
spade_available <- FALSE
tryCatch({
    library(spade)
    spade_available <- TRUE
    spade_pkg <- "spade"
}, error = function(e) {
    tryCatch({
        library(spade2)
        spade_available <<- TRUE
        spade_pkg <<- "spade2"
    }, error = function(e2) {
        cat("Neither 'spade' nor 'spade2' R packages are available.\n")
        cat("Install with:\n")
        cat("  devtools::install_github('nolanlab/spade2')\n")
        cat("  OR: BiocManager::install('spade')\n")
    })
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
    cat("Usage: Rscript run_spade.R <input_csv> <n_clusters> <output_csv>\n")
    quit(status = 1)
}

if (!spade_available) {
    cat("SPADE R package not installed. Skipping.\n")
    quit(status = 0)
}

input_csv <- args[1]
n_clusters <- as.integer(args[2])
output_csv <- args[3]

cat("Loading data from:", input_csv, "\n")
data <- as.matrix(read.csv(input_csv, header = TRUE))
cat("  Cells:", nrow(data), " Markers:", ncol(data), "\n")

# Arcsinh transform
data_t <- asinh(data / 5)

cat("Running R SPADE with", n_clusters, "clusters...\n")
t_start <- proc.time()

# SPADE.cluster performs density-dependent downsampling + clustering
# The exact API depends on the package version
result <- SPADE.cluster(
    data_t,
    k = n_clusters,
    downsampling_target_percent = 0.1
)

elapsed <- (proc.time() - t_start)["elapsed"]
labels <- result$cluster

cat("  Done in", round(elapsed, 1), "seconds\n")

# Save
out <- data.frame(label = as.integer(labels))
write.csv(out, output_csv, row.names = FALSE)
cat("Saved to:", output_csv, "\n")

timing <- list(
    method = "SPADE_R",
    runtime_s = as.numeric(elapsed),
    n_clusters = length(unique(labels)),
    n_cells = nrow(data)
)
timing_file <- sub("\\.csv$", "_timing.json", output_csv)
write(toJSON(timing, auto_unbox = TRUE, pretty = TRUE), timing_file)
