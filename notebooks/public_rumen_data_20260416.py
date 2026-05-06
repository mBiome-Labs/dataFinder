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
    import plotly.graph_objects as go

    return Counter, Path, go, literal_eval, mo, pd, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rumen Metagenome Datasets on SRA

    Datasets' metadata was downloaded using `dataFinder` script. Data was obtained on 04Apr2026.
    """)
    return


@app.cell
def _(Path, literal_eval, pd):
    sra_data_path = Path("../data/sra_rumen_microbiome__2026_05_04.tsv")

    r_data = pd.read_csv(
        sra_data_path,
        sep="\t",
        converters={"SampleAttributes": literal_eval, "Published": pd.to_datetime},
    )
    return (r_data,)


@app.cell
def _(r_data):
    r_data
    return


@app.cell
def _(r_data):
    print(f"Number of studies: {len((studies:=r_data['SRAStudy'].unique()))}")
    print(
        f"Library Strategies covered: {list(r_data['LibraryStrategy'].unique())}"
    )
    print(f"Library sources covered: {list(r_data['LibrarySource'].unique())}")
    print(f"Sequencers used: {list(r_data['Sequencer'].unique())}")
    print(
        f"Data ranges from {sorted(r_data['Published'])[0]} -TO- {sorted(r_data['Published'])[-1]}"
    )
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
    print(
        f"Number of missing values for LibraryStrategy: {sum(r_data['LibraryStrategy'].isna())}"
    )
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
    # seperate the samples y sequencing strategy for further analysis
    amplicon_data = r_data.loc[r_data["LibraryStrategy"] == "AMPLICON"].copy()
    rnaseq_data = r_data.loc[r_data["LibraryStrategy"] == "RNA-Seq"].copy()
    wgs_data = r_data.loc[r_data["LibraryStrategy"].isin(["WGS", "OTHER"])].copy()
    return (wgs_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## WGS Data

    Data specificall for the *in silico* proteomics.
    """)
    return


@app.cell
def _(wgs_data):
    print(f"Number of WGS studies: {len(wgs_data['SRAStudy'].unique())}")
    print(f"Number of samples: {len(wgs_data)}")
    print(f"Sequenincg technology: {wgs_data['Sequencer'].unique()}")
    return


@app.cell
def _(Counter, wgs_data):
    host = []
    for h in wgs_data["SampleAttributes"]:
        if h.get("host scientific name"):
            host.append(h.get("host scientific name"))
        elif h.get("host"):
            host.append(h.get("host"))
        elif h.get("breed"):
            host.append(h.get("breed"))
        else:
            host.append("missing")
    wgs_data["host"] = host
    Counter(host)
    return


@app.cell
def _(wgs_data):
    wgs_data["host"] = [
        "Bos taurus" if i == "bos_taurus" else i for i in wgs_data["host"]
    ]

    # map the hosts to more general categories for better visualisation
    mapper = {
        "Bos taurus": "Cattle",
        "Capra hircus": "Goat",
        "Ovis aries": "Sheep",
        "Hu sheep": "Sheep",
        "Holstein": "Cattle",
        "Tibetan sheep": "Sheep",
        "Huacaya alpaca": "Alpaca",
        "Simmental": "Cattle",
        "cattle": "Cattle",
        "cow": "Cattle",
    }
    wgs_data["host_general"] = [mapper.get(i, i) for i in wgs_data["host"]]

    # add sequencing type into the dataframe
    wgs_data["sequencing_type"] = [
        "long-read" if "ION" in i else "short-read" for i in wgs_data["Sequencer"]
    ]

    wgs_data["Gb"] = wgs_data["Bases"] / 1e9
    return


@app.cell
def _(wgs_data):
    host_seq_counts = (
        wgs_data[["host", "host_general", "Sequencer", "sequencing_type"]]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "Samples Sequenced"})
    )
    host_seq_counts
    return


@app.cell
def _(wgs_data):
    wgs_data["Sequencer"].value_counts()
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
def _(pd, wgs_data):
    pd.crosstab(wgs_data["Sequencer"], wgs_data["host_general"])
    return


@app.cell
def _(pd, wgs_data):
    pd.crosstab(wgs_data["sequencing_type"], wgs_data["host_general"])
    return


@app.cell
def _(px, wgs_data):
    data_with_missing = wgs_data.loc[wgs_data["host_general"] == "missing"].copy()
    fig5 = px.histogram(
        data_frame=data_with_missing,
        x="Gb",
        marginal="violin",
        color="sequencing_type",
        template="plotly_white",
        nbins=100,
        title="SRA Metagenome: Missing host info Gb of data per sample on SRA",
        labels={"Gb": "Gb of sequencing data/sample", "count": "Count"},
        color_discrete_map={
            "long-read": px.colors.qualitative.Dark2[0],
            "short-read": px.colors.qualitative.Dark2[1],
        },
        category_orders={"sequencing_type": ["long-read", "short-read"]},
    )
    fig5.update_traces(
        marker=dict(line=dict(color="#000000", width=1)),
    )
    fig5.update_xaxes(tick0=0, nticks=20)
    fig5.update_yaxes(tick0=0, nticks=15)
    fig5.update_legends(title="Sequencing Type")
    fig5.show()
    return


@app.cell
def _(wgs_data):
    wgs_data.loc[wgs_data["host_general"] == "missing"][
        ["SRAStudy", "Sequencer"]
    ].value_counts()

    # ERP186382 are dairy cattle
    # SRP665216 are Bos grunniens (Yak)
    return


@app.cell
def _(wgs_data):
    wgs_data.loc[wgs_data["SRAStudy"] == "SRP637515"]
    return


@app.cell
def _(wgs_data):
    idx_cattle = wgs_data.loc[wgs_data["SRAStudy"] == "ERP186382"].index
    wgs_data.loc[idx_cattle, "host"] = "Bos taurus"
    wgs_data.loc[idx_cattle, "host_general"] = "Cattle"
    return


@app.cell
def _(wgs_data):
    idx_yak = wgs_data.loc[wgs_data["SRAStudy"] == "SRP665216"].index
    wgs_data.loc[idx_yak, "host"] = "Bos grunniens"
    wgs_data.loc[idx_yak, "host_general"] = "Yak"
    return


@app.cell
def _(wgs_data):
    host_seq_counts2 = (
        wgs_data[["host", "host_general", "Sequencer", "sequencing_type"]]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "Samples Sequenced"})
    )
    host_seq_counts2
    return (host_seq_counts2,)


@app.cell
def _(host_seq_counts2, px):
    fig = px.bar(
        data_frame=host_seq_counts2,
        x="host_general",
        y="Samples Sequenced",
        color="Sequencer",
        barmode="stack",
        template="plotly_white",
    )
    fig.show()
    return


@app.cell
def _(host_seq_counts2, px):
    fig2 = px.bar(
        data_frame=host_seq_counts2,
        x="host_general",
        y="Samples Sequenced",
        color="sequencing_type",
        barmode="stack",
        template="plotly_white",
    )
    fig2.show()
    return


@app.cell
def _(go, host_seq_counts2, px):
    cattle_long_short = (
        host_seq_counts2.loc[host_seq_counts2["host_general"] == "Cattle"]
        .groupby("sequencing_type")
        .sum("Samples Sequenced")
    )
    fig3 = go.Figure(
        data=[
            go.Pie(
                labels=cattle_long_short.index,
                values=cattle_long_short["Samples Sequenced"],
                hole=0.4,
                pull=[0, 0.1],
                marker=dict(colors=px.colors.qualitative.Dark2),
            )
        ]
    )
    fig3.update_traces(
        textposition="inside",
        textinfo="percent+label+value",
        marker=dict(line=dict(color="#000000", width=1)),
    )
    fig3.update_layout(
        title_text="Sequencing Type for Cattle WGS Samples on SRA", width=600
    )
    fig3.show()
    return


@app.cell
def _(px, wgs_data):
    fig4 = px.histogram(
        data_frame=wgs_data.loc[wgs_data["host_general"] == "Cattle"],
        x="Gb",
        marginal="violin",
        color="sequencing_type",
        template="plotly_white",
        nbins=100,
        title="SRA Cattle Metagenome: Gb of data per sample on SRA",
        labels={"Gb": "Gb of sequencing data/sample", "count": "Count"},
        color_discrete_map={
            "long-read": px.colors.qualitative.Dark2[0],
            "short-read": px.colors.qualitative.Dark2[1],
        },
    )
    fig4.update_traces(
        marker=dict(line=dict(color="#000000", width=1)),
    )
    fig4.update_xaxes(tick0=0, nticks=20)
    fig4.update_yaxes(tick0=0, nticks=15)
    fig4.update_legends(title="Sequencing Type")
    fig4.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rumen Metagenome Datasets on ENA

    Datasets' metadata was downloaded using `ena_src/runner.py` script. Data was obtained on 06Apr2026.
    """)
    return


@app.cell
def _(Path, pd):
    ena_data_path = Path("../data/ena_rumen_microbiome__2026_05_06.tsv")

    e_data = pd.read_csv(
        ena_data_path,
        sep="\t",
        na_values=["Missing", "missing", "not applicable"],
    )
    e_data["Gb"] = e_data["base_count"] / 1e9

    useful_cols = (e_data.isna().sum() / len(e_data) < 1).values
    print(
        f"Number of columns without comlpetely absent data: {sum(useful_cols)}/{e_data.shape[1]}"
    )

    e_data = e_data.loc[:, useful_cols].copy()
    e_data
    return (e_data,)


@app.cell
def _(e_data):
    print(
        f"Number of studies: {len((e_studies:=e_data['study_accession'].unique()))}"
    )
    print(
        f"Library Strategies covered: {list(e_data['library_strategy'].unique())}"
    )
    print(f"Library sources covered: {list(e_data['library_source'].unique())}")
    print(f"Sequencers used: {list(e_data['instrument_model'].unique())}")
    return


@app.cell
def _(e_data, r_data):
    not_in_sra = [
        i
        for i in e_data["experiment_accession"].unique()
        if i not in r_data["Experiment"].unique()
    ]
    print(f"Number of experiments in ENA not already in the SRA set: {len(not_in_sra)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Conclusion

    ENA data is a subset of the data available on SRA for the time periods and queries used. Therefore we can just use the SRA datasets for experiments.
    """)
    return


if __name__ == "__main__":
    app.run()
