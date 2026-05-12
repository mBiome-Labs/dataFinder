import sys
import logging
import time
from subprocess import run
from urllib import parse

RESULT_TYPE = "read_run"
QUERY = '(host_tax_id=9606 OR host_scientific_name="homo sapiens" OR host="human") AND (library_source="metagenomic" AND ( instrument_platform="pacbio_smrt" OR instrument_platform="oxford_nanopore" ))'
# QUERY = (
#     '((tax_tree(749906) OR tax_tree(506599) OR tax_tree(256318)) AND (description="rumen" OR study_title="rumen" OR sample_title="rumen")) OR tax_tree(3394441)'
#     'AND (library_source="metagenomic" OR library_source="metatranscriptomic" OR library_source="other")'
# )

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
    stream=sys.stderr,
)


def main():
    logging.info("Script Starting...")
    fields_cmd = (
        f"curl -X 'GET' 'https://www.ebi.ac.uk/ena/portal/api/returnFields?dataPortal=ena&result={RESULT_TYPE}&format=tsv' "
        "-H 'accept: */*' | awk '{OFS=\"\t\"; print $1}'"
    )

    fields = (
        run(fields_cmd, shell=True, capture_output=True, text=True)
        .stdout.rstrip()
        .split("\n")
    )
    logging.info(f"Number of fields pulled: {len(fields)}")
    logging.info(f"Fields pulled: {fields}")

    logging.info(f"Dataset accessed: {RESULT_TYPE}")
    logging.info(f"Query used: {QUERY}")
    logging.info("Pulling data from ENA...")
    tsv_cmd = (
        "curl -X 'GET' "
        f"'https://www.ebi.ac.uk/ena/portal/api/search?result={RESULT_TYPE}&query={parse.quote(QUERY)}"
        f"&fields={parse.quote(','.join(fields[1:]))}&dataPortal=ena&includeMetagenomes=true&format=tsv&download=true' "
        f"-H 'accept: */*' > ena_data__{time.strftime('%Y_%m_%d', time.gmtime())}.tsv"
    )
    run(tsv_cmd, shell=True)
    logging.info("Script Finished!")


if __name__ == "__main__":
    main()
