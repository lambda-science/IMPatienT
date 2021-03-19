from app import create_app, db
from app.models import User, Image, Patient, Pdf, ReportHisto

# Create instance of app and push app context
app = create_app()
app_context = app.app_context()
app_context.push()


@app.shell_context_processor
def make_shell_context():
    """Add DB object in the flask shell"""
    return {
        'db': db,
        'User': User,
        'Image': Image,
        'Patient': Patient,
        'Pdf:': Pdf,
        "ReportHisto": ReportHisto
    }
