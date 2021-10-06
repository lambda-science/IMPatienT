import json
import os
import pandas as pd
# import seaborn as sns
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objs as go
from flask import current_app

from app import db
from app.models import ReportHisto


def table_to_df(df):
    # Transformation de la table SQLite en dataframe en parsant l'arbre JSON
    # Return un dictionnaire et une liste de colonnes (les features histo)
    tree_as_dict = {}
    features_col = []
    for index, row in df.iterrows():
        tree_as_dict.setdefault("id", []).append(row[0])
        tree_as_dict.setdefault("patient_id", []).append(row[1])
        tree_as_dict.setdefault("expert_id", []).append(row[2])
        tree_as_dict.setdefault("biopsie_id", []).append(row[3])
        tree_as_dict.setdefault("muscle_prelev", []).append(row[4])
        tree_as_dict.setdefault("age_biopsie", []).append(row[5])
        tree_as_dict.setdefault("date_envoie", []).append(row[6])
        tree_as_dict.setdefault("gene_diag", []).append(row[7])
        tree_as_dict.setdefault("comment", []).append(row[9])
        tree_as_dict.setdefault("conclusion", []).append(row[10])
        tree_as_dict.setdefault("datetime", []).append(row[11])

        my_tree = row[8]
        for feature in my_tree:
            tree_as_dict.setdefault(feature["text"], []).append(
                float(feature["data"].get("presence", -0.25))
            )
            if index == 0:
                features_col.append(feature["text"])
    df_return = pd.DataFrame.from_dict(tree_as_dict)
    return df_return, features_col


def db_to_df():
    df = pd.read_sql(db.session.query(ReportHisto).statement, db.session.bind)
    return df


def process_df(df):
    df = df.replace(
        {
            "COM_CCD": "COM",
            "COM_MMM": "COM",
            "NM_CAP": "NM",
            "CFTD": "OTHER",
            "NON_CM": "OTHER",
            "CM": "UNCLEAR",
        }
    )
    df = df.replace({-0.25: np.nan, 0.25: 1, 0.5: 1, 0.75: 1})
    return df


def create_plotly_viz(df):
    df["age_biopsie"].replace({"N/A": -1}, inplace=True)
    muscle_prelev = df["muscle_prelev"].value_counts()
    as_list = muscle_prelev.index.tolist()
    idx = as_list.index("")
    as_list[idx] = "N/A"
    muscle_prelev.index = as_list
    fig1 = px.bar(
        x=muscle_prelev.index,
        y=muscle_prelev,
        text=muscle_prelev,
        color=muscle_prelev.index.astype(str),
        color_discrete_sequence=px.colors.qualitative.G10,
        title="Cohort repartition by muscle",
    )
    fig1.update_layout(
        xaxis_title="Biopsy muscle", yaxis_title="Number of reports", showlegend=False
    )
    graphJSON1 = json.loads(fig1.to_json())

    age_biopsie = df["age_biopsie"].value_counts()
    NA_age = age_biopsie.where(age_biopsie.index == -1).sum()
    bebe = age_biopsie.where(age_biopsie.index <= 2).sum()
    enfant = age_biopsie.where((age_biopsie.index > 2) & (age_biopsie.index < 18)).sum()
    adulte = age_biopsie.where(age_biopsie.index >= 18).sum()
    fig2 = px.bar(
        x=["Newborn (<=2 years)", "Child (3-17 years)", "Adult (>=18 years)", "N/A"],
        y=[bebe, enfant, adulte, NA_age],
        text=[bebe, enfant, adulte, NA_age],
        color=[
            "Newborn (<=2 years)",
            "Child (3-17 years)",
            "Adult (>=18 years)",
            "N/A",
        ],
        color_discrete_sequence=px.colors.qualitative.G10,
        title="Cohort repartition by age group",
    )
    fig2.update_layout(
        xaxis_title="Age Group", yaxis_title="Number of reports", showlegend=False
    )
    graphJSON2 = json.loads(fig2.to_json())

    gene_diag = df["gene_diag"].value_counts()
    fig3 = px.bar(
        x=gene_diag.index,
        y=gene_diag,
        text=gene_diag,
        color=gene_diag.index.astype(str),
        color_discrete_sequence=px.colors.qualitative.G10,
        title="Cohort repartition by gene diagnosis",
    )
    fig3.update_layout(
        xaxis_title="Gene diagnosed", yaxis_title="Number of reports", showlegend=False,
    )
    graphJSON3 = json.loads(fig3.to_json())

    conclusion = df["conclusion"].value_counts()
    fig4 = px.bar(
        x=conclusion.index,
        y=conclusion,
        text=conclusion,
        color=conclusion.index.astype(str),
        color_discrete_sequence=px.colors.qualitative.G10,
        title="Cohort repartition by myopathy diagnosis",
    )
    fig4.update_layout(
        xaxis_title="Myopathy class", yaxis_title="Number of reports", showlegend=False
    )
    graphJSON4 = json.loads(fig4.to_json())

    return [graphJSON1, graphJSON2, graphJSON3, graphJSON4]


# def create_basic_viz(df):
#     df["age_biopsie"].replace({"N/A": -1}, inplace=True)

#     muscle_prelev = df["muscle_prelev"].value_counts()
#     as_list = muscle_prelev.index.tolist()
#     idx = as_list.index("")
#     as_list[idx] = "N/A"
#     muscle_prelev.index = as_list
#     sns_plot = sns.barplot(x=muscle_prelev.index, y=muscle_prelev)
#     fig = sns_plot.get_figure()
#     plt.xticks(rotation=25)
#     fig.savefig(
#         os.path.join(current_app.config["VIZ_FOLDER"], "fig1.jpg"),
#         dpi=300,
#         bbox_inches="tight",
#     )
#     plt.clf()

#     age_biopsie = df["age_biopsie"].value_counts()
#     NA_age = age_biopsie.where(age_biopsie.index == -1).sum()
#     bebe = age_biopsie.where(age_biopsie.index <= 2).sum()
#     enfant = age_biopsie.where((age_biopsie.index > 2) & (age_biopsie.index < 18)).sum()
#     adulte = age_biopsie.where(age_biopsie.index >= 18).sum()
#     sns_plot2 = sns.barplot(
#         x=["Newborn (<=2 years)", "Child (3-17 years)", "Adult (>=18 years)", "N/A"],
#         y=[bebe, enfant, adulte, NA_age],
#     )
#     for i in range(4):
#         sns_plot2.text(
#             i,
#             [bebe, enfant, adulte, NA_age][i] + 0.1,
#             int([bebe, enfant, adulte, NA_age][i]),
#             color="black",
#             ha="center",
#         )
#     fig2 = sns_plot.get_figure()
#     plt.xticks(rotation=25)
#     fig2.savefig(
#         os.path.join(current_app.config["VIZ_FOLDER"], "fig2.jpg"),
#         dpi=300,
#         bbox_inches="tight",
#     )
#     plt.clf()

#     gene_diag = df["gene_diag"].value_counts()
#     # gene_diag = df["gene_diag"].value_counts()[0:4]
#     # gene_diag["Other"] = len(df) - (df["gene_diag"].value_counts()[0:4].sum())

#     sns_plot3 = sns.barplot(x=gene_diag.index, y=gene_diag)
#     for i in range(len(gene_diag)):
#         sns_plot3.text(i, gene_diag[i] + 0.1, gene_diag[i], color="black", ha="center")
#     fig3 = sns_plot3.get_figure()
#     plt.xticks(rotation=90)
#     fig3.savefig(
#         os.path.join(current_app.config["VIZ_FOLDER"], "fig3.jpg"),
#         dpi=300,
#         bbox_inches="tight",
#     )
#     plt.clf()

#     conclusion = df["conclusion"].value_counts()
#     sns_plot4 = sns.barplot(x=conclusion.index, y=conclusion)
#     for i in range(len(conclusion)):
#         sns_plot4.text(
#             i, conclusion[i] + 0.1, conclusion[i], color="black", ha="center"
#         )
#     fig4 = sns_plot4.get_figure()
#     fig4.savefig(
#         os.path.join(current_app.config["VIZ_FOLDER"], "fig4.jpg"),
#         dpi=300,
#         bbox_inches="tight",
#     )
#     plt.clf()


def generate_stat_per(df, features_col):
    stat_per_gene = {}
    all_genes = list(set(df.gene_diag.to_list()))
    for i in all_genes:
        ds = df[df["gene_diag"] == i][features_col].sum().sort_values(ascending=False)
        nrow = len(df[df["gene_diag"] == i])
        ds = ds / nrow * 100
        stat_per_gene[i] = {}
        stat_per_gene[i]["n"] = nrow
        stat_per_gene[i]["feature"] = ds[ds > 0].round().to_dict()

    stat_per_diag = {}
    all_diag = list(set(df.conclusion.to_list()))
    for i in all_diag:
        ds = df[df["conclusion"] == i][features_col].sum().sort_values(ascending=False)
        nrow = len(df[df["conclusion"] == i])
        ds = ds / nrow * 100
        stat_per_diag[i] = {}
        stat_per_diag[i]["n"] = nrow
        stat_per_diag[i]["feature"] = ds[ds > 0].round().to_dict()
    with open(
        os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_gene.json"), "w"
    ) as f:
        json.dump(stat_per_gene, f, indent=4, ensure_ascii=False)
    with open(
        os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_diag.json"), "w"
    ) as f:
        json.dump(stat_per_diag, f, indent=4, ensure_ascii=False)


def generate_corr_matrix(df):
    onto_values = df.iloc[:, 11:]
    onto_values = onto_values.dropna(axis=1, thresh=10)
    onto_values = onto_values.replace({0: -1})
    # onto_values = onto_values.fillna(0)
    corrMatrix = onto_values.corr()
    corrMatrix = corrMatrix.fillna(0)
    col_row_to_drop = []
    for i in range(len(corrMatrix)):
        if corrMatrix.iloc[i, i] == 0:
            col_row_to_drop.append(corrMatrix.columns[i])

    corrMatrix.drop(col_row_to_drop, axis=1, inplace=True)
    corrMatrix.drop(col_row_to_drop, axis=0, inplace=True)
    # Use Seaborn to cluster data
    # g = sns.clustermap(corrMatrix, cmap="coolwarm", figsize=(20, 20))
    # plt.close()
    # trace_heatmap = go.Heatmap(x=g.data2d.columns, y=g.data2d.columns,
    #                    z=g.data2d, colorscale="RdBu")
    trace_heatmap = go.Heatmap(
        x=corrMatrix.columns, y=corrMatrix.columns, z=corrMatrix, colorscale="RdBu",
    )
    data = [trace_heatmap]
    layout = go.Layout(
        title="Standard Vocabulary terms correlation matrix (threshold n>=10)",
        showlegend=True,
        width=1000,
        height=1000,
        yaxis={"scaleanchor": "x"},
    )
    figure = go.Figure(data=data, layout=layout)
    figure.write_json(
        os.path.join(current_app.config["VIZ_FOLDER"], "correlation_matrix.json")
    )
