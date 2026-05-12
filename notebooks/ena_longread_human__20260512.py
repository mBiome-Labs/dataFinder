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
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go

    return Path, go, mo, pd, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Human Gut Microbiome

    Data from ENA and accessed on 12-May-2026
    """)
    return


@app.cell
def _(Path, pd):
    sra_data_path = Path("../data/ena_human_microbiome_longread__2026_05_12.tsv")

    r_data = pd.read_csv(
        sra_data_path,
        sep="\t",
        converters={"first_public": pd.to_datetime},
        low_memory=False,
        na_values=["unspecified", ""],
    )
    r_data["Gb"] = r_data["base_count"] / 1e9
    return (r_data,)


@app.cell
def _(r_data):
    r_data
    return


@app.cell
def _(r_data):
    # find any missing human metagenome WGS samples that might be hidden under the ambiguous "human metagenome" or "metagenome" scientific names
    r_data.loc[
        r_data["scientific_name"].isin(["human metagenome", "metagenome"])
        & (r_data["library_strategy"] == "WGS")
    ].sort_values("Gb", ascending=False)

    # searched from the ambigious records above
    hand_picked_gut = [
        "SRR23814922",
        "RR23814925",
        "SRR23814917",
        "SRR23814919",
        "SRR23814921",
        "SRR23814923",
        "SRR23814918",
        "SRR23814916",
        "SRR23814920",
        "SRR23814924",
    ]
    return (hand_picked_gut,)


@app.cell
def _(hand_picked_gut, r_data):
    # check the selection
    r_data.loc[
        r_data["scientific_name"].isin(
            ["human gut metagenome", "gut metagenome", "human feces metagenome"]
        )
        & (r_data["library_strategy"] == "WGS")
        | (r_data["run_accession"].isin(hand_picked_gut))
    ]
    return


@app.cell
def _(r_data):
    # some stats
    print(
        f"Number of studies: {len((studies:=r_data['study_accession'].unique()))}"
    )
    print(f"Number of runs: {len(r_data['run_accession'].unique())}")
    print(
        f"Library Strategies covered: {list(r_data['library_strategy'].unique())}"
    )
    print(f"Library sources covered: {list(r_data['library_source'].unique())}")
    print(f"Sequencers used: {list(r_data['instrument_platform'].unique())}")
    return


@app.cell
def _(hand_picked_gut, r_data):
    # select the WGS data
    wgs_data = r_data.loc[
        r_data["scientific_name"].isin(
            ["human gut metagenome", "gut metagenome", "human feces metagenome"]
        )
        & (r_data["library_strategy"] == "WGS")
        | (r_data["run_accession"].isin(hand_picked_gut))
    ]
    return (wgs_data,)


@app.cell
def _(wgs_data):
    print(f"Number of studies: {len(wgs_data['study_accession'].unique())}")
    print(f"Number of runs: {len(wgs_data['run_accession'].unique())}")
    return


@app.cell
def _(px, wgs_data):
    fig = px.histogram(
        data_frame=wgs_data,
        x=wgs_data["first_public"].dt.year,
        color="instrument_model",
        nbins=12,
        template="plotly_white",
        title="Number of long-read human gut metagenome WGS samples per year on ENA",
        labels={"x": "Year", "count": "Number of WGS samples"},
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=1)))
    fig.update_xaxes(tick0=0, nticks=12, tickangle=315)
    fig.show()
    return


@app.cell
def _(go, px, wgs_data):
    host_seq_counts = (
        wgs_data[
            [
                "host",
                "host_scientific_name",
                "instrument_model",
                "instrument_platform",
            ]
        ]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "Samples Sequenced"})
    )
    host_seq_counts

    long_short = host_seq_counts.groupby("instrument_model").sum(
        "Samples Sequenced"
    )
    fig2 = go.Figure(
        data=[
            go.Pie(
                labels=long_short.index,
                values=long_short["Samples Sequenced"],
                marker=dict(colors=px.colors.qualitative.Dark2),
            )
        ]
    )
    fig2.update_traces(
        textposition="inside",
        textinfo="percent+label+value",
        marker=dict(line=dict(color="#000000", width=1)),
    )
    fig2.update_layout(
        title_text="Sequencing Instrument for long-read human gut WGS Samples on ENA",
        width=600,
    )
    fig2.show()
    return


@app.cell
def _(px, wgs_data):
    fig3 = px.histogram(
        data_frame=wgs_data.loc[wgs_data["Gb"] >= 1],
        x="Gb",
        marginal="violin",
        color="instrument_platform",
        template="plotly_white",
        nbins=150,
        title="Human gut Metagenome: Gb of data per sample on ENA",
        labels={"Gb": "Gb of sequencing data/sample", "count": "Count"},
        color_discrete_map={
            "long-read": px.colors.qualitative.Dark2[0],
            "short-read": px.colors.qualitative.Dark2[1],
        },
    )
    fig3.update_traces(
        marker=dict(line=dict(color="#000000", width=1)),
    )
    fig3.update_xaxes(tick0=0, nticks=25)
    fig3.update_yaxes(tick0=0, nticks=15)
    fig3.update_legends(title="Sequencing Type")
    fig3.show()
    return


@app.cell
def _(px, wgs_data):
    fig4 = px.scatter(
        data_frame=wgs_data,
        x="first_public",
        y="Gb",
        color="instrument_platform",
        template="plotly_white",
        hover_data=[
            "host_scientific_name",
            "instrument_model",
            "host_body_site",
            "isolation_source",
        ],
    )
    fig4.update_traces(marker=dict(line=dict(color="#000000", width=1)))
    fig4.show()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
