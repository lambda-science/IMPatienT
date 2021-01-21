from flask import Flask, render_template
from app.index import bp


@bp.route("/")
@bp.route("/index")
def index():
    print("###############")
    return render_template("index/index.html")