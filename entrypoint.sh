#!/bin/sh
set -eu

action="${1:-run}"
if [ "$#" -gt 0 ]; then
    shift
fi

config="${STEMCNV_CONFIG:-config.yaml}"
sample_table="${STEMCNV_SAMPLE_TABLE:-sample_table.tsv}"
cores="${CORES:-8}"
memory_mb="${STEMCNV_MEMORY_MB:-11000}"
snake_options="${STEMCNV_SNAKEMAKE_OPTIONS:---notemp --resources mem_mb=10500 --latency-wait 4  --keep-going --set-resources run_CBS:mem_mb=10000 combined_PennCNV_output:mem_mb=10000 run_PennCNV:mem_mb=10000 run_SNV_analysis:mem_mb=10000 run_process_CNV_calls:mem_mb=10000 knit_report:mem_mb=10000}"
cache="${STEMCNV_CACHE:-/cache}"

common_args="--directory /work --config $config --sample-table $sample_table --local-cores $cores --memory-mb $memory_mb --cache-path $cache"

case "$action" in
    validate)
        stemcnv-check --version
        stemcnv-check run --help >/dev/null
        ;;
    setup)
        cd /work
        exec stemcnv-check setup-files "$@"
        ;;
    make-staticdata)
        # shellcheck disable=SC2086
        exec stemcnv-check make-staticdata $common_args "$@"
        ;;
    run)
        # 1. Statische Dateien (PFB/GCmodel) automatisch generieren, falls sie fehlen
        stemcnv-check make-staticdata $common_args "$@" || true
        
        # 2. Haupt-Workflow starten
        # shellcheck disable=SC2086
        exec stemcnv-check run $common_args "$@" -- $snake_options
        ;;
esac
