# ENA Scrape

Script to scrape metadata from ENA using the [portal API](https://www.ebi.ac.uk/ena/portal/api/swagger-ui/index.html).

This script runs a query text search against the ENA dataset (including metagenomes). It returns all the possible data fields for the requested dataset as a tsv file.

## Prerequisites

```bash
python>=3.12
curl>=8.5
```

## Running the script

1. Update the `RESULT_TYPE` and `QUERY` at the top of `runner.py`.
2. Run the script.

```bash
python runner.py
```
