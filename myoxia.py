from app import create_app, db
from app.models import User, Image, Patient, Pdf, ReportHisto

# Create instance of app
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Add DB object in the flask shell"""
    return {
        "db": db,
        "User": User,
        "Image": Image,
        "Patient": Patient,
        "Pdf:": Pdf,
        "ReportHisto": ReportHisto,
    }


if __name__ == "__main__":
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)