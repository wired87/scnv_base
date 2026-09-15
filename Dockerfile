FROM condaforge/miniforge3:25.3.1-0

ARG STEMCNV_COMMIT=e050dcf0737e1c260135d0f41832f3151f7b117e

RUN mamba install -y -n base -c conda-forge -c bioconda \
        python=3.12 \
        apptainer \
        fuse-overlayfs \
        squashfuse \
        git \
        snakemake=8.28 \
        pip \
    && python -m pip install --no-cache-dir \
        "git+https://github.com/bihealth/StemCNV-check.git@${STEMCNV_COMMIT}" \
    && mamba clean --all --yes

# StemCNV-check 1.0.0 passes str workdirs to the Snakemake 8.28 Python API,
# whose WorkdirHandler requires pathlib.Path. The module already imports Path.
RUN sed -i 's/workdir=args.directory/workdir=Path(args.directory)/g' \
        /opt/conda/lib/python3.12/site-packages/stemcnv_check/app/make_staticdata.py \
    && sed -i 's/cores=args.local_cores/cores=int(args.local_cores)/g; s/local_cores=args.local_cores/local_cores=int(args.local_cores)/g; s/'"'"'mem_mb'"'"': args.memory_mb/'"'"'mem_mb'"'"': int(args.memory_mb)/g' \
        /opt/conda/lib/python3.12/site-packages/stemcnv_check/app/make_staticdata.py \
    && sed -i 's/hgdownload\.cse\.ucsc\.edu/hgdownload.soe.ucsc.edu/g' \
        /opt/conda/lib/python3.12/site-packages/stemcnv_check/rules/static_creation_global_files.smk



COPY entrypoint.sh /usr/local/bin/stemcnv-entrypoint
RUN sed -i 's/\r$//' /usr/local/bin/stemcnv-entrypoint \
    && mkdir -p /work /cache \
    && touch /etc/localtime

WORKDIR /work
VOLUME ["/work", "/cache"]

ENTRYPOINT ["/usr/local/bin/stemcnv-entrypoint"]
CMD ["run"]

# Auto-generated ENV from .env
ENV     STEMCNV_DOCKER_TIMEOUT=300 \
    STEMCNV_RUN_ROOT_HOST=./.runtime/stemcnv-runs \
    STEMCNV_EXAMPLE_DATA_HOST=./stemcnv-example-data \
    STEMCNV_WORKFLOW_MEMORY_MB=11000 \
    DOCKER_MEMORY_LIMIT=12000m \
    CORES=8 \
    STEMCNV_SNAKEMAKE_OPTIONS="--notemp --resources mem_mb=10500 --latency-wait 4  --keep-going --set-resources run_CBS:mem_mb=10000 combined_PennCNV_output:mem_mb=10000 run_PennCNV:mem_mb=10000 run_SNV_analysis:mem_mb=10000 run_process_CNV_calls:mem_mb=10000 knit_report:mem_mb=10000" \
    PYTHONUNBUFFERED=1 \
    STEMCNV_CACHE=/cache \
    STEMCNV_DOCKER_IMAGE="stemcnv-check:1.0.0"