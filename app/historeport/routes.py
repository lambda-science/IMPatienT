import json
from contextlib import suppress
from app import db
from app.historeport import bp
from app.historeport.boqa import *
from app.historeport.forms import (
    DeleteButton,
    OntologyDescriptPreAbs,
    ReportForm,
    PdfUpload,
)
from app.histostats.vizualisation import (
    db_to_df,
    table_to_df,
)
from app.historeport.ocr import TextReport
from app.historeport.onto_func import StandardVocabulary
from app.models import ReportHisto
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    make_response,
)
from flask_login import current_user, login_required


@bp.route("/historeport", methods=["GET", "POST"])
@login_required
def histoindex():
    """View function for the text report index

    Returns:
        str: Report Index HTML Page
    """
    form = DeleteButton()
    report_history = ReportHisto.query.all()
    return render_template("histo_index.html", history=report_history, form=form)


@bp.route("/historeport/download", methods=["GET"])
@login_required
def histo_download():
    with open(os.path.join("data/ontology", "ontology.json"), "r") as fp:
        onto_tree = json.load(fp)
    df = db_to_df()
    df, features_col = table_to_df(df, onto_tree)
    df = df.replace({-0.25: np.nan})
    resp = make_response(df.to_csv(index=False))
    resp.headers["Content-Disposition"] = "attachment; filename=text_reports.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@bp.route("/historeport/new", methods=["GET", "POST"])
@login_required
def historeport():
    """View function for the text report registration form.
    Or modify an existing report.

    Returns:
        str: Report Registration HTML Page
    """
    # If args in URL, try to retrive report from DB and pre-fill it
    ontology_tree_exist = False
    if request.args:
        report_request = ReportHisto.query.get(request.args.get("id"))
        if report_request is not None:
            form = ReportForm(
                patient_id=report_request.patient_id,
                expert_id=report_request.expert_id,
                biopsie_id=report_request.biopsie_id,
                muscle_prelev=report_request.muscle_prelev,
                age_biopsie=report_request.age_biopsie,
                date_envoie=report_request.date_envoie,
                mutation=report_request.mutation,
                pheno_terms=report_request.pheno_terms,
                gene_diag=report_request.gene_diag,
                ontology_tree=report_request.ontology_tree,
                comment=report_request.comment,
                conclusion=report_request.conclusion,
            )
            if form.ontology_tree.data:
                ontology_tree_exist = True
        else:
            return redirect(url_for("historeport.histoindex"))
    # If no args: empty form
    else:
        with open(
            os.path.join(current_app.config["ONTOLOGY_FOLDER"], "ontology.json")
        ) as f:
            empty_json_tree = json.load(f)
        form = ReportForm(ontology_tree=empty_json_tree)
    # Form for panel on the right with node description
    form2 = OntologyDescriptPreAbs()
    pdf_form = PdfUpload()

    # On validation, save to database
    if form.validate_on_submit():
        # Update existing DB entry or create a new one (else)
        if request.args:
            report_entry = ReportHisto.query.get(request.args.get("id"))
            if report_entry is not None:
                form.populate_obj(report_entry)
                onto_jstree = StandardVocabulary(report_entry.ontology_tree)
                # Process Tagify Output JSON
                with suppress(json.decoder.JSONDecodeError):
                    pheno_terms_list = [
                        i["value"] for i in json.loads(report_entry.pheno_terms)
                    ]
                    report_entry.pheno_terms = ",".join(pheno_terms_list)
                with suppress(json.decoder.JSONDecodeError):
                    report_entry.gene_diag = json.loads(report_entry.gene_diag)[0][
                        "value"
                    ]
                with suppress(json.decoder.JSONDecodeError):
                    report_entry.conclusion = json.loads(report_entry.conclusion)[0][
                        "value"
                    ]
                report_entry.ontology_tree = onto_jstree.clean_tree()
                report_entry.expert_id = current_user.id
                try:
                    results = get_boqa_pred(json.dumps(report_entry.ontology_tree))
                except:
                    results = ["No_Pred", 0]
                if results[1] > 0.5:
                    report_entry.BOQA_prediction = results[0]
                    report_entry.BOQA_prediction_score = results[1]
                else:
                    report_entry.BOQA_prediction = "No_Pred"
                    report_entry.BOQA_prediction_score = 0
                # Update of template ontology
                # template_ontology = Ontology(template)
                # current_report_ontology = Ontology(report_entry.ontology_tree)
                # template_ontology.update_ontology(current_report_ontology)
                # template_ontology.dump_updated_to_file("config/ontology.json")
                db.session.commit()
                return redirect(url_for("historeport.histoindex"))

        else:
            report_entry = ReportHisto()
            form.populate_obj(report_entry)
            # Process Tagify Output JSON
            with suppress(json.decoder.JSONDecodeError):
                pheno_terms_list = [
                    i["value"] for i in json.loads(report_entry.pheno_terms)
                ]
                report_entry.pheno_terms = ",".join(pheno_terms_list)
            with suppress(json.decoder.JSONDecodeError):
                report_entry.gene_diag = json.loads(report_entry.gene_diag)[0]["value"]
            with suppress(json.decoder.JSONDecodeError):
                report_entry.conclusion = json.loads(report_entry.conclusion)[0][
                    "value"
                ]
            onto_jstree = StandardVocabulary(report_entry.ontology_tree)
            report_entry.ontology_tree = onto_jstree.clean_tree()
            report_entry.expert_id = current_user.id
            db.session.add(report_entry)
            try:
                results = get_boqa_pred(json.dumps(report_entry.ontology_tree))
            except:
                results = ["No_Pred", 0]
            if results[1] > 0.5:
                report_entry.BOQA_prediction = results[0]
                report_entry.BOQA_prediction_score = results[1]
            else:
                report_entry.BOQA_prediction = "No_Pred"
                report_entry.BOQA_prediction_score = 0
            # Update of template ontology
            # template_ontology = Ontology(template)
            # current_report_ontology = Ontology(report_entry.ontology_tree)
            # template_ontology.update_ontology(current_report_ontology)
            # template_ontology.dump_updated_to_file("config/ontology.json")
            db.session.commit()
            return redirect(url_for("historeport.histoindex"))

    return render_template(
        "historeport.html",
        form=form,
        form2=form2,
        pdf_form=pdf_form,
        ontology_tree_exist=ontology_tree_exist,
    )


@bp.route("/delete_report/<id_report>", methods=["POST"])
@login_required
def delete_report(id_report):
    """Route for the deletion of a registered text report.

    Args:
        id_report (int): ID of the report to delete

    Returns:
        redirect: Redirect to the report index HTML page
    """
    form = DeleteButton()
    # Retrieve database entry and delete it if existing
    if form.validate_on_submit():
        report_form = ReportHisto.query.get(id_report)
        if report_form is None:
            flash("Report {} not found.".format(id), "danger")
            return redirect(url_for("histoindex"))
        db.session.delete(report_form)
        db.session.commit()
        flash("Deleted entry {}!".format(id_report), "success")
        return redirect(url_for("historeport.histoindex"))
    else:
        return redirect(url_for("historeport.histoindex"))


@bp.route("/predict_diag_boqa/", methods=["POST"])
@login_required
def predict_diag_boqa():
    """API POST route for the prediction of a text report class using BOQA.

    Returns:
        str: JSON string with the best prediction results and its score
    """
    raw_data = request.get_data()
    results = get_boqa_pred(raw_data)
    return (
        json.dumps(
            {
                "success": True,
                "class": results[0],
                "proba": round(results[1], 2),
            }
        ),
        200,
        {"ContentType": "application/json"},
    )


@bp.route("/ocr_pdf", methods=["POST"])
@login_required
def ocr_pdf():
    """API POST route for the OCR/NLP of a PDF file.

    Returns:
        str: JSON string with the results of the OCR/NLP (list of matched
        standard terms)
    """
    if request.method == "POST":
        file_val = request.files["pdf_file"]
        pdf_object = TextReport(file_obj=file_val, lang=request.form["language"])
        pdf_object.pdf_to_text()
        # pdf_object.detect_sections()
        # pdf_object.extract_section_text()
        match_list = pdf_object.analyze_text()
        results = {"full_text": pdf_object.text_as_list, "match_list": match_list}
    return (
        json.dumps({"success": True, "results": results}),
        200,
        {"ContentType": "application/json"},
    )
