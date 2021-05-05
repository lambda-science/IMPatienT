import json
import os
from flask_login import current_user, login_required
from flask import render_template, current_app
from app.histostats import bp


@bp.route("/histostats", methods=["GET", "POST"])
def statsindex():
    """Page for histo statistics page."""
    stat_per_gene_file = open(
        os.path.join(current_app.config["CONFIG_FOLDER"], "stat_per_gene.json")
    )
    stat_per_gene = json.load(stat_per_gene_file)
    stat_per_diag_file = open(
        os.path.join(current_app.config["CONFIG_FOLDER"], "stat_per_diag.json")
    )
    stat_per_diag = json.load(stat_per_diag_file)
    stat_per_gene = sorted(stat_per_gene.items())
    stat_per_diag = sorted(stat_per_diag.items())
    return render_template(
        "histostats_index.html",
        stat_per_gene=stat_per_gene,
        stat_per_diag=stat_per_diag,
    )
