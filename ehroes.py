from app import create_app, db
from app.models import Image, ReportHisto, User

# Create instance of app
app = create_app()


@app.before_first_request
def create_admin():
    """Create admin user if no user registered"""
    User.create_admin_account()


@app.shell_context_processor
def make_shell_context():
    """Add DB object in the flask shell"""
    return {
        "db": db,
        "User": User,
        "Image": Image,
        "ReportHisto": ReportHisto,
    }


if __name__ == "__main__":
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)
