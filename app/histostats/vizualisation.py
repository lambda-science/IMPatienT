import json
import os

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
from app import db
from app.models import ReportHisto
from flask import current_app
from sklearn.metrics import confusion_matrix


def table_to_df(df, onto_tree):
    """Transform the JSON JSTree in the text report table to a pandas dataframe columns

    Args:
        df (Dataframe): Dataframe version of the text report table in database

    Returns:
        Dataframe: Table as dataframe with new columns correspondig to JSTree nodes
        List: List of the columns extracted from the standard vocabulary JSTree nodes
    """
    # Transformation of the SQLite table to a Pandas DataFrame by parsing the JSON tree
    # Returns a dictionnary and a list of columns (standard terms)
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
        tree_as_dict.setdefault("mutation", []).append(row[8])
        tree_as_dict.setdefault("pheno_terms", []).append(row[9])
        tree_as_dict.setdefault("comment", []).append(row[11])
        tree_as_dict.setdefault("conclusion", []).append(row[12])
        tree_as_dict.setdefault("BOQA_prediction", []).append(row[13])
        tree_as_dict.setdefault("BOQA_prediction_score", []).append(row[14])
        tree_as_dict.setdefault("datetime", []).append(row[15])

        my_tree = row[10]
        # my_tree = dict((item['text'], item) for item in row[8])
        for feature in onto_tree:
            # node = my_tree[feature["text"]]
            node = next(
                (item for item in my_tree if item["text"] == feature["text"]), None
            )
            tree_as_dict.setdefault(node["text"], []).append(
                float(node["data"].get("presence", -0.25))
            )
            if index == 0:
                features_col.append(node["text"])
    df_return = pd.DataFrame.from_dict(tree_as_dict)
    return df_return, features_col


def db_to_df():
    """Convert the SQLite table to a pandas dataframe

    Returns:
        Dataframe: Dataframe representation of the SQLite table for text reports
    """
    df = pd.read_sql(db.session.query(ReportHisto).statement, db.session.bind)
    return df


def process_df(df):
    """Process the dataframe to replace diagnosis names and values with
    corresponding values from dictionary hardcoded in the function.

    Args:
        df (Dataframe): Dataframe representation of the SQLite table for text reports

    Returns:
        Dataframe: Processed DataFrame with modified values
    """
    df["gene_diag"].replace({"": "N/A"}, inplace=True)
    df = df.replace({-0.25: np.nan, 0.25: 1, 0.5: 1, 0.75: 1})
    return df


def create_plotly_viz(df):
    """Create the four plotly histograms for the muscle, age, gene and conclusion columns.

    Args:
        df (DataFrame): Processed DataFrame

    Returns:
        list: List of Plotly JSON Graphs for the four histograms
    """
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
    gene_diag_label = []
    for i in list(gene_diag.index):
        if len(i.split(" ")) > 1:
            gene_diag_label.append(i.split(" ")[1])
        else:
            gene_diag_label.append(i)
    fig3 = px.bar(
        x=gene_diag_label,
        y=gene_diag,
        text=gene_diag,
        color=gene_diag.index.astype(str),
        color_discrete_sequence=px.colors.qualitative.G10,
        title="Cohort repartition by gene diagnosis",
    )
    fig3.update_layout(
        xaxis_title="Gene diagnosed",
        yaxis_title="Number of reports",
        showlegend=False,
    )
    graphJSON3 = json.loads(fig3.to_json())

    conclusion = df["conclusion"].value_counts()
    conclusion_label = []
    for i in list(conclusion.index):
        conclusion_label.append(string_breaker(i, 15))
    fig4 = px.bar(
        x=conclusion.index,
        y=conclusion,
        text=conclusion,
        color=conclusion.index.astype(str),
        color_discrete_sequence=px.colors.qualitative.G10,
        title="Cohort repartition by myopathy diagnosis",
    )
    fig4.update_layout(
        xaxis_title="Myopathy class",
        yaxis_title="Number of reports",
        showlegend=False,
    )
    fig4.update_xaxes(
        tickmode="array", tickvals=conclusion.index, ticktext=conclusion_label
    )
    graphJSON4 = json.loads(fig4.to_json())

    return [graphJSON1, graphJSON2, graphJSON3, graphJSON4]


def generate_stat_per(df, features_col):
    """Generate the frequencies statistics for each standard vocbulary terms per
     genes and per conclusion. Return the stats as dataframe, write the stats
     to JSON files.

    Args:
        df (DataFrame): Processed DataFrame
        features_col (list): List of column names corresponding to Standard
         vocabulary terms

    Returns:
        DataFrame: DataFrame of frequencies statistics per gene
        DataFrame: DataFrame of frequencies statistics per conclusion
    """
    # Stats as Dataframe for HTML Template
    list_per_gene = []
    all_genes = list(set(df.gene_diag.to_list()))
    for i in all_genes:
        ds = df[df["gene_diag"] == i][features_col].sum().sort_values(ascending=False)
        ds = ds[ds > 0]
        nrow = len(df[df["gene_diag"] == i])
        for index, value in ds.items():
            list_per_gene.append([i, nrow, index, int(value), round(value / nrow, 2)])
    df_per_gene = pd.DataFrame(
        list_per_gene, columns=["Gene", "N", "Feature", "Count", "Frequency"]
    )

    list_per_diag = []
    all_diag = list(set(df.conclusion.to_list()))
    for i in all_diag:
        ds = df[df["conclusion"] == i][features_col].sum().sort_values(ascending=False)
        ds = ds[ds > 0]
        nrow = len(df[df["conclusion"] == i])
        for index, value in ds.items():
            list_per_diag.append([i, nrow, index, int(value), round(value / nrow, 2)])
    df_per_diag = pd.DataFrame(
        list_per_diag, columns=["Diag", "N", "Feature", "Count", "Frequency"]
    )
    df_per_gene.to_csv(
        os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_gene.csv"), index=False
    )
    df_per_diag.to_csv(
        os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_diag.csv"), index=False
    )

    # JSON Files for BOQA
    stat_per_gene = {}
    all_genes = list(set(df.gene_diag.to_list()))
    for i in all_genes:
        ds = df[df["gene_diag"] == i][features_col].sum().sort_values(ascending=False)
        nrow = len(df[df["gene_diag"] == i])
        ds = ds / nrow
        stat_per_gene[i] = {}
        stat_per_gene[i]["n"] = nrow
        stat_per_gene[i]["feature"] = ds[ds > 0].round().to_dict()

    stat_per_diag = {}
    all_diag = list(set(df.conclusion.to_list()))
    for i in all_diag:
        ds = df[df["conclusion"] == i][features_col].sum().sort_values(ascending=False)
        nrow = len(df[df["conclusion"] == i])
        ds = ds / nrow
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

    return df_per_gene, df_per_diag


def generate_UNCLEAR(df):
    """Generate the histogram for the re-prediction with BOQA of the UNCLEAR patients.

    Args:
        df (Dataframe): Processed DataFrame

    Returns:
        list: Plotly JSON Graph
    """
    df_unclear = df[df["conclusion"] == "UNCLEAR"]
    conclusion_boqa = df_unclear["BOQA_prediction"].value_counts()
    labels_trim = []
    for i in list(conclusion_boqa.index):
        labels_trim.append(string_breaker(i, 15))
    fig = px.bar(
        x=conclusion_boqa.index,
        y=conclusion_boqa,
        text=conclusion_boqa,
        color=conclusion_boqa.index.astype(str),
        color_discrete_sequence=px.colors.qualitative.G10,
        title="Prediction of UNCLEAR reports by BOQA",
    )
    fig.update_layout(
        xaxis_title="BOQA Myopathy Class Prediction",
        yaxis_title="Number of reports",
        showlegend=False,
    )
    fig.update_xaxes(
        tickmode="array", tickvals=conclusion_boqa.index, ticktext=labels_trim
    )
    graph_UNCLEAR = json.loads(fig.to_json())
    return graph_UNCLEAR


def generate_confusion_BOQA(df):
    """Generate the confusion matrix for the prediction of patients with BOQA
    (excluding UNCLEAR and OTHER)

    Args:
        df (DataFrame): Processed DataFrame

    Returns:
        list: Plotly JSON Graph
    """
    df_no_unclear = df[(df["conclusion"] != "UNCLEAR") & (df["conclusion"] != "OTHER")]
    y_true = df_no_unclear["conclusion"].to_list()
    y_pred = df_no_unclear["BOQA_prediction"].to_list()
    labels = ["No_Pred"] + df_no_unclear["conclusion"].unique().tolist()
    labels_trim = []
    for i in list(labels):
        labels_trim.append(string_breaker(i, 15))
    matrix_results = confusion_matrix(
        #    y_true, y_pred, labels=["No_Pred", "CNM", "COM", "NM"]
        y_true,
        y_pred,
        labels=labels,
    )
    fig = ff.create_annotated_heatmap(
        z=matrix_results,
        x=labels_trim,
        y=labels_trim,
        #    x=["No_Pred", "CNM", "COM", "NM"],
        #    y=["No_Pred", "CNM", "COM", "NM"],
        colorscale="Viridis",
    )
    fig.update_layout(
        title="Confusion matrix of histologic reports classification by BOQA",
        xaxis_title="Predicted Class (BOQA)",
        yaxis_title="True Class",
        showlegend=False,
    )
    fig["layout"]["yaxis"]["autorange"] = "reversed"
    fig["layout"]["xaxis"]["side"] = "bottom"
    graph_matrixboqa = json.loads(fig.to_json())
    return graph_matrixboqa


def generate_corr_matrix(df):
    """Generation the correlation matrix for the standard vocabulary terms.
    Internal threshold is set to at least 10 annotations (0 or 1).
    Figure is dumped to a Plotly JSON Graph to a file named correlation_matrix.json

    Args:
        df (DataFrame): Processed DataFrame
    """
    onto_values = df.iloc[:, 13:]
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
    update_correlation_data(corrMatrix)
    trace_heatmap = go.Heatmap(
        x=corrMatrix.columns,
        y=corrMatrix.columns,
        z=corrMatrix,
        colorscale="RdBu",
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


def update_phenotype_gene(df):
    """Update the phenotype and gene datamined information of the standard vocabulary
    terms in the ontology.json JSTree file.

    Args:
        df (DataFrame): Processed DataFrame
    """
    with open(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json"), "r"
    ) as fp:
        onto = json.load(fp)
    for term in onto:
        df_temp = df[df[term["text"]] == 1]
        gene_datamined_temp = list(df_temp["gene_diag"].value_counts().index)
        phenotype_datamined_temp = list(df_temp["conclusion"].value_counts().index)
        if gene_datamined_temp == []:
            term["data"]["gene_datamined"] = ""
        else:
            term["data"]["gene_datamined"] = ",".join(sorted(gene_datamined_temp))
        if phenotype_datamined_temp == []:
            term["data"]["phenotype_datamined"] = ""
        else:
            term["data"]["phenotype_datamined"] = ",".join(
                sorted(phenotype_datamined_temp)
            )
    with open(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json"), "w"
    ) as fp:
        json.dump(onto, fp, indent=4)


def update_correlation_data(corrMatrix):
    """Update the correlation information of the standard vocabulary terms in the
    ontology.json JSTree file.

    Args:
        corrMatrix (Dataframe): Correlation Dataframe computed from processed dataframe.
    """
    with open(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json"), "r"
    ) as fp:
        onto = json.load(fp)
    for term in onto:
        if term["text"] in corrMatrix:
            correlation_series = corrMatrix[term["text"]]
            correlation_series = correlation_series[(correlation_series > 0.5)]
            term["data"]["correlates_with"] = ",".join(sorted(correlation_series.index))
        else:
            pass
    with open(
        os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json"), "w"
    ) as fp:
        json.dump(onto, fp, indent=4)


def string_breaker(s, max_length=10):
    # s = s.split(" ")
    # s_elem_len = [len(i) for i in s]
    lines_nb = int(len(s) / max_length)
    new_string = []
    for i in range(lines_nb):
        new_string.append(s[i * max_length : i * max_length + max_length])
    new_string.append(s[lines_nb * max_length :])
    return "<br>".join(new_string)
