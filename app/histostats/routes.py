import json
import os
from flask_login import login_required
from flask import render_template, current_app
from app.histostats import bp
from app.histostats.vizualisation import *


@bp.route("/histostats", methods=["GET", "POST"])
@login_required
def statsindex():
    """Page for histo statistics page."""
    # Up to stat_per_diag to move in the historeport part to not always regenerate
    df = db_to_df()
    df, features_col = table_to_df(df)
    df = process_df(df)
    generate_stat_per(df, features_col)
    graph_viz = create_plotly_viz(df)
    # create_basic_viz(df)
    generate_corr_matrix(df)
    update_phenotype_gene(df)
    stat_per_gene_file = open(
        os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_gene.json")
    )
    stat_per_gene = json.load(stat_per_gene_file)
    stat_per_diag_file = open(
        os.path.join(current_app.config["VIZ_FOLDER"], "stat_per_diag.json")
    )
    stat_per_diag = json.load(stat_per_diag_file)
    stat_per_gene = sorted(stat_per_gene.items())
    stat_per_diag = sorted(stat_per_diag.items())

    graphJSON = json.load(
        open(
            os.path.join(current_app.config["VIZ_FOLDER"], "correlation_matrix.json"),
            "r",
        )
    )
    return render_template(
        "histostats_index.html",
        stat_per_gene=stat_per_gene,
        stat_per_diag=stat_per_diag,
        graphJSON=graphJSON,
        graph_viz=graph_viz,
    )
