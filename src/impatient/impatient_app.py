from impatient.app import create_app, db
from impatient.app.models import Image, ReportHisto

# Create instance of app
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Add DB object in the flask shell"""
    return {
        "db": db,
        "Image": Image,
        "ReportHisto": ReportHisto,
    }


if __name__ == "__main__":
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)
