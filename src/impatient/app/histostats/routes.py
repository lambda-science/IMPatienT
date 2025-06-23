from flask import current_app, render_template

from impatient.app.histostats import bp
from impatient.app.histostats.vizualisation import *


@bp.route("/histostats", methods=["GET", "POST"])
def statsindex():
    """View function for the automatic dashboard visualization

    Returns:
        str: Dashboard HTML Page
    """
    # Up to stat_per_diag to move in the historeport part to not always regenerate
    with open(
        os.path.join("/home/impatient/data/ontology/", "ontology.json"), "r"
    ) as fp:
        onto_tree = json.load(fp)
    df = db_to_df()
    df, features_col = table_to_df(df, onto_tree)
    df = process_df(df)
    df_per_gene, df_per_diag = generate_stat_per(df, features_col, onto_tree)
    graph_viz = create_plotly_viz(df)
    graph_UNCLEAR = generate_UNCLEAR(df)
    graph_matrixboqa = generate_confusion_BOQA(df)
    generate_corr_matrix(df, onto_tree)
    update_phenotype_gene(df)

    graphJSON = json.load(
        open(
            os.path.join(current_app.config["VIZ_FOLDER"], "correlation_matrix.json"),
            "r",
        )
    )
    return render_template(
        "histostats_index.html",
        df_per_gene=df_per_gene.to_html(
            table_id="per-gene-table",
            classes="table table-striped table-bordered table-hover table-responsive",
            index=False,
        ),
        df_per_diag=df_per_diag.to_html(
            table_id="per-diag-table",
            classes="table table-striped table-bordered table-hover table-responsive",
            index=False,
        ),
        graphJSON=graphJSON,
        graph_viz=graph_viz,
        graph_UNCLEAR=graph_UNCLEAR,
        matrixboqa=graph_matrixboqa,
    )
