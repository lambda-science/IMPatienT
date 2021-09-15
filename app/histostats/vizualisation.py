import pandas as pd
import sqlite3
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


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

        my_tree = json.loads(row[8])
        for feature in my_tree:
            tree_as_dict.setdefault(feature["text"], []).append(
                float(feature["data"].get("presence", -0.25))
            )
            if index == 0:
                features_col.append(feature["text"])
    return tree_as_dict, features_col


def db_to_df():
    con = sqlite3.connect("app.db")
    df = pd.read_sql_query("SELECT * from report_histo", con)
    return df


def create_basic_viz(df):
    muscle_prelev = df["muscle_prelev"].value_counts()
    # Empty index to N/A
    as_list = muscle_prelev.index.tolist()
    idx = as_list.index("")
    as_list[idx] = "N/A"
    muscle_prelev.index = as_list
    sns.barplot(x=muscle_prelev.index, y=muscle_prelev)
    var = plt.xticks(rotation=25)

    age_biopsie = df["age_biopsie"].value_counts()
    bebe = age_biopsie.where(age_biopsie.index <= 2).sum()
    enfant = age_biopsie.where((age_biopsie.index > 2) & (age_biopsie.index < 18)).sum()
    adulte = age_biopsie.where(age_biopsie.index >= 18).sum()
    g = sns.barplot(
        x=["Bébé (<=2ans)", "Enfant (3-17ans)", "Adulte (>=18ans)"],
        y=[bebe, enfant, adulte],
    )
    for i in range(3):
        g.text(
            i,
            [bebe, enfant, adulte][i] + 0.1,
            int([bebe, enfant, adulte][i]),
            color="black",
            ha="center",
        )

    gene_diag = df["gene_diag"].value_counts()[0:4]
    gene_diag["Other"] = 89 - (14 + 11 + 8 + 7)
    fig_dims = (8, 4)
    fig, ax = plt.subplots(figsize=fig_dims)
    g = sns.barplot(x=gene_diag.index, y=gene_diag, ax=ax)
    for i in range(len(gene_diag)):
        g.text(i, gene_diag[i] + 0.1, gene_diag[i], color="black", ha="center")
    # var = plt.xticks(rotation=90)

    # Merge sub types for stats
    conclusion = df["conclusion"].value_counts()
    g = sns.barplot(x=conclusion.index, y=conclusion)
    for i in range(len(conclusion)):
        g.text(i, conclusion[i] + 0.1, conclusion[i], color="black", ha="center")


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
    with open("data/stat_per_gene.json", "w") as f:
        json.dump(stat_per_gene, f, indent=4, ensure_ascii=False)
    with open("data/stat_per_diag.json", "w") as f:
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
    g = sns.clustermap(corrMatrix, cmap="coolwarm", figsize=(20, 20))
    plt.close()
    # trace_heatmap = go.Heatmap(x=g.data2d.columns, y=g.data2d.columns,
    #                    z=g.data2d, colorscale="RdBu")
    trace_heatmap = go.Heatmap(
        x=corrMatrix.columns, y=corrMatrix.columns, z=corrMatrix, colorscale="RdBu"
    )
    data = [trace_heatmap]
    layout = go.Layout(
        title="Histology ontology terms correlation matrix (threshold n>10)",
        showlegend=True,
        width=1000,
        height=1000,
        yaxis={"scaleanchor": "x"},
    )
    figure = go.Figure(data=data, layout=layout)
    figure.show()
    figure.write_json("data/correlation_matrix.json")
