import sys
import logging
import json
import time
from subprocess import run
import pandas as pd

# with open("params.json") as handle:
#     RUN_PARAMS: dict = json.load(handle)

# API_ENV = f"export NCBI_API_KEY={RUN_PARAMS['entrez_api']}"

# Table S2 from Xie et al. 2026 Science: 10.1126/science.adv4244
SCI_PAPER_METADATA = "/home/darren/Documents/3_Programming/2_my_repos/mBiomeLabs/dataFinder/data/science.adv4244_table_s2.xlsx"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
    stream=sys.stderr,
)


def main(sra_file: str, ena_file: str) -> None:
    begin = time.time()
    logging.info("Script Starting...")

    sra_data = pd.read_csv(sra_file, sep="\t", low_memory=False)
    logging.info(
        f"SRA data loaded: {sra_data.shape[0]} rows, {sra_data.shape[1]} columns"
    )

    ena_data = pd.read_csv(ena_file, sep="\t", low_memory=False)
    logging.info(
        f"ENA data loaded: {ena_data.shape[0]} rows, {ena_data.shape[1]} columns"
    )

    # add tag to ENA names
    ena_data.columns = [col.strip() + "__ENA" for col in ena_data.columns]

    logging.info("Merging SRA and ENA data...")
    combined_data = pd.merge(
        sra_data,
        ena_data,
        left_on="Run",
        right_on="run_accession__ENA",
        how="outer",
        suffixes=("_SRA", "_ENA"),
    )
    logging.info(
        f"Combined data loaded: {combined_data.shape[0]} rows, {combined_data.shape[1]} columns"
    )

    # bs_cmd = f"{API_ENV}; efetch -db biosample -id {','.join(biosamples)} -format xml | python bs_parser.py > biosample_info.tsv"

    sci_paper_meta = pd.read_excel(
        SCI_PAPER_METADATA, sheet_name="Table S2a", skiprows=1
    )
    cols_to_ffill = ["Reference & from", "NCBI BioProject", "Study description"]
    sci_paper_meta[cols_to_ffill] = sci_paper_meta[cols_to_ffill].ffill()

    # fill whitespaces in column names with underscores
    sci_paper_meta.columns = [
        col.strip().replace(" ", "_") + "__Xie_sci_2026"
        for col in sci_paper_meta.columns
    ]

    logging.info(
        f"Science Paper Metadata loaded: {sci_paper_meta.shape[0]} rows, {sci_paper_meta.shape[1]} columns"
    )
    combined = pd.merge(
        combined_data,
        sci_paper_meta,
        how="left",
        left_on="Run",
        right_on="SRA_accession__Xie_sci_2026",
    )
    logging.info(
        f"Combined data with Xie et al.: {combined.shape[0]} rows, {combined.shape[1]} columns"
    )

    # remove columns with all empty values
    combined = combined.dropna(axis=1, how="all")
    logging.info(
        f"Final dataset: {combined.shape[0]} rows, {combined.shape[1]} columns"
    )

    combined.to_csv("combined_sra_ena_metadata.tsv", sep="\t", index=False)

    end = time.time()
    logging.info(f"Script Completed in {round(end-begin)}s")


if __name__ == "__main__":
    sra = "/home/darren/Documents/3_Programming/2_my_repos/mBiomeLabs/dataFinder/data/sra_rumen_microbiome__2026_05_09.tsv"
    ena = "/home/darren/Documents/3_Programming/2_my_repos/mBiomeLabs/dataFinder/data/ena_rumen_microbiome__2026_05_09.tsv"
    main(sra, ena)
