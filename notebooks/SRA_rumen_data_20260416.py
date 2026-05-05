import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def _():
    from collections import Counter
    from pathlib import Path
    from ast import literal_eval
    import marimo as mo
    import pandas as pd
    import plotly.express as px

    return Path, literal_eval, mo, pd, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rumen Metagenome Datasets on SRA

    Datasets' metadata was downloaded using `dataFinder` script. Data was obtained on 12Apr2026.
    """)
    return


@app.cell
def _(Path, literal_eval, pd):
    data_path = Path("../data/rumen_microbiome__2026_05_04.tsv")

    r_data = pd.read_csv(data_path, sep="\t", converters={"SampleAttributes": literal_eval, "Published": pd.to_datetime})
    return (r_data,)


@app.cell
def _(r_data):
    r_data
    return


@app.cell
def _(r_data):
    print(f"Number of studies: {len((studies:=r_data['SRAStudy'].unique()))}")
    print(f"Library Strategies covered: {list(r_data['LibraryStrategy'].unique())}")
    print(f"Library sources covered: {list(r_data['LibrarySource'].unique())}")
    print(f"Sequencers used: {list(r_data['Sequencer'].unique())}")
    print(f"Data ranges from {sorted(r_data['Published'])[0]} -TO- {sorted(r_data['Published'])[-1]}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Questions:
    - What are OTHER and WCS library strategies?
    - How many WGS/shotgun datasets are there?
    """)
    return


@app.cell
def _(r_data):
    print(f"Number of missing values for LibraryStrategy: {sum(r_data['LibraryStrategy'].isna())}")
    return


@app.cell
def _(r_data):
    # whole chromosome sequencing - not sure what that means for metagenomic... >> exclude these samples
    r_data.loc[r_data["LibraryStrategy"] == "WCS"]
    return


@app.cell
def _(r_data):
    # these look like WGS as they have high Gb data range >> include theses
    r_data.loc[r_data["LibraryStrategy"] == "OTHER"]
    return


@app.cell
def _(r_data):
    amplicon_data = r_data.loc[r_data["LibraryStrategy"] == "AMPLICON"].copy()
    rnaseq_data = r_data.loc[r_data["LibraryStrategy"] == "RNA-Seq"].copy()
    wgs_data = r_data.loc[r_data["LibraryStrategy"].isin(["WGS", "OTHER"])].copy()
    return (wgs_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## WGS Data
    """)
    return


@app.cell
def _(wgs_data):
    print(f"Number of WGS studies: {len(wgs_data['SRAStudy'].unique())}")
    print(f"Number of samples: {len(wgs_data)}")
    print(f"Sequenincg technology: {wgs_data['Sequencer'].unique()}")
    return


@app.cell
def _(wgs_data):
    wgs_data["Sequencer"].value_counts()
    return


@app.cell
def _(wgs_data):
    wgs_data["host"] = [i.get("host", "missing") for i in wgs_data["SampleAttributes"]]
    wgs_data["host"] = ["Bos taurus" if i == "bos_taurus" else i for i in wgs_data["host"]]
    return


@app.cell
def _(wgs_data):
    wgs_data["host"].value_counts()
    return


@app.cell
def _(pd, wgs_data):
    pd.crosstab(wgs_data["Sequencer"], wgs_data["host"])
    return


@app.cell
def _():
    return


@app.cell
def _(px, wgs_data):
    fig = px.bar(wgs_data[["host", "Sequencer"]].value_counts().reset_index(), x="host", y="count", color="Sequencer", barmode="stack", template="plotly_white")
    fig.show()
    return


@app.cell
def _(wgs_data):
    wgs_data["Sequencer"].value_counts()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
