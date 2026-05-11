import os
import sys
import logging
import json
import time
from subprocess import run

with open("params.json") as handle:
    RUN_PARAMS: dict = json.load(handle)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
    stream=sys.stderr,
)

# globals
SUPPORTED_SEARCHES = ["sra"]
API_ENV = f"export NCBI_API_KEY={RUN_PARAMS['entrez_api']}"


def main() -> None:
    begin = time.time()
    logging.info("Script Starting...")

    # get the possible taxonomies from NCBI
    logging.info("Getting requested taxonomies using query...")
    cmd_taxonomy = (
        f"{API_ENV}; esearch -db taxonomy -query \"{RUN_PARAMS['taxonomy_query']}\" "
        "| efetch -format xml | xtract -pattern Taxon -element ScientificName"
    )
    taxonomy_lst = (
        run(cmd_taxonomy, shell=True, capture_output=True)
        .stdout.decode("utf-8")
        .rstrip()
        .split("\n")
    )

    match (search_type := RUN_PARAMS["search_type"]):
        case "sra":
            # get the uids for the SRA records with correct organisms
            logging.info(
                "Getting SRA run IDs from requested organism(s) and additional queries..."
            )
            cmd_final_query = (
                f"{API_ENV}; efetch -db sra -input {RUN_PARAMS['id_file']} -format xml | python parser.py "
                f"> data__{time.strftime('%Y_%m_%d', time.gmtime())}.tsv"
            )
        case _:
            logging.error(
                msg := f"search_type '{search_type}' not valid, supported types strings {SUPPORTED_SEARCHES}. "
                "Update params and repeat"
            )
            raise ValueError(msg)

    # gather uids for the final query database
    search_taxas = (
        "[ORGANISM] OR ".join(taxonomy_lst)
        if len(taxonomy_lst) > 1
        else taxonomy_lst[0]
    )
    search_term = f"({search_taxas}[ORGANISM]{RUN_PARAMS['final_query']}"
    cmd_uid = (
        f'{API_ENV}; esearch -db {search_type} -query "{search_term}" '
        f"| efetch -format uid > {RUN_PARAMS['id_file']}"
    )
    run(cmd_uid, shell=True)

    # read id list and count
    with open(RUN_PARAMS["id_file"], "r") as handle:
        n_ids = len(handle.readlines())
    logging.info(f"{n_ids} ids to be retrieved from {search_type} DB...")

    # run the final query command
    run(cmd_final_query, shell=True)

    # remove the ids file as not needed
    os.remove(RUN_PARAMS["id_file"])

    end = time.time()
    logging.info(f"Script Completed in {round(end-begin)}s")


if __name__ == "__main__":
    main()
