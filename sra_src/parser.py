import sys
import time
import xml.etree.ElementTree as ET
from collections import OrderedDict
from runner import logging

GB_IN_BYTES = 1024**3


def return_text(element: ET.Element) -> str | None:
    return None if element == None else element.text


def extract_data(record: ET.Element) -> list[OrderedDict]:
    """Extracts the important information from a EXPERIMENT_PACKAGE record.

    Args:
        record (ET.Element): xml element of the EXPERIMENT_PACKAGE record

    Returns:
        list[dict]: list of all the run records extracted into a dict.
    """
    data_rec = OrderedDict()
    data_rec["Experiment"] = record.find("EXPERIMENT").attrib.get("accession")

    # library info
    design = record.find("EXPERIMENT/DESIGN")
    data_rec["DesignDescription"] = return_text(design.find("DESIGN_DESCRIPTION"))
    data_rec["LibraryStrategy"] = return_text(
        design.find("LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY")
    )
    data_rec["LibrarySelection"] = return_text(
        design.find("LIBRARY_DESCRIPTOR/LIBRARY_SELECTION")
    )
    data_rec["LibrarySource"] = return_text(
        design.find("LIBRARY_DESCRIPTOR/LIBRARY_SOURCE")
    )
    data_rec["LibraryLayout"] = [
        i.tag for i in design.find("LIBRARY_DESCRIPTOR/LIBRARY_LAYOUT")
    ][0]
    data_rec["LibraryProtocol"] = return_text(
        design.find("LIBRARY_CONSTRUCTION_PROTOCOL")
    )

    # sequencer
    platform = record.find("EXPERIMENT/PLATFORM")
    data_rec["Sequencer"] = [
        [return_text(gc) for gc in child][0] for child in platform
    ][0]

    # study info
    data_rec["SRAStudy"] = return_text(record.find("STUDY/IDENTIFIERS/PRIMARY_ID"))
    data_rec["BioProject"] = return_text(record.find("STUDY/IDENTIFIERS/EXTERNAL_ID"))

    # sample info
    data_rec["Sample"] = record.find("SAMPLE").attrib.get("accession")
    data_rec["BioSample"] = return_text(record.find("SAMPLE/IDENTIFIERS/EXTERNAL_ID"))
    data_rec["ScientificName"] = return_text(
        record.find("SAMPLE/SAMPLE_NAME/SCIENTIFIC_NAME")
    )
    data_rec["SampleAttributes"] = {
        attr.find("TAG").text: attr.find("VALUE").text
        for attr in record.find("SAMPLE").findall("SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE")
    }

    # run info for the experiment
    run_records = []
    for run in record.findall("RUN_SET/RUN"):
        data_rec_n = data_rec.copy()
        size = (
            None
            if run.attrib.get("size") == None
            else str(round(int(run.attrib.get("size")) / GB_IN_BYTES, 4))
        )
        data_rec_n.update(
            {
                "Run": run.attrib.get("accession"),
                "Bases": run.attrib.get("total_bases"),
                "SizeGB": size,
                "Published": run.attrib.get("published"),
                "IsPublic": run.attrib.get("is_public"),
            }
        )
        run_records.append(data_rec_n)
    return run_records


logging.info("Record parsing started...")
start_run = time.time()

record = []
count = 0
for line in sys.stdin:
    if (line := line.strip()) in [
        '<?xml version="1.0" encoding="UTF-8" ?>',
        "<!DOCTYPE EXPERIMENT_PACKAGE_SET>",
        "<EXPERIMENT_PACKAGE_SET>",
    ]:
        continue
    record.append(line)

    # find the end of the experiment package xml record
    if line == "</EXPERIMENT_PACKAGE>":
        parsed_records = extract_data(ET.fromstringlist(record))
        record = []
        count += 1
        if count == 1:
            print("\t".join(list(parsed_records[0].keys())))
        for rec in parsed_records:
            data = [str(i) for _, i in rec.items()]
            print("\t".join(data), file=sys.stdout)

        if count % 1000 == 0:
            logging.info(f"{count} records parsed in {round(time.time()-start_run)}s")

logging.info(f"Run records parsed = {count}")
sys.exit(0)
