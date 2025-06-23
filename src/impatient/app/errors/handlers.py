from impatient.app import db
from impatient.app.errors import bp
from flask import render_template
import traceback


@bp.app_errorhandler(404)
def not_found_error(error):
    """View function for error 404.

    Args:
        error (int): Error code.

    Returns:
        str: HTML page for error 404.
    """
    return render_template("404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """View function for error 500.

    Args:
        error (int): Error code.

    Returns:
        str: HTML page for error 500.
    """
    db.session.rollback()
    # Capture the exception details
    traceback_info = traceback.format_exc()

    return (
        render_template("500.html", traceback_info=traceback_info),
        500,
    )


@bp.app_errorhandler(413)
def too_large(error):
    """View function for error 413. (too large)

    Args:
        error (int): Error code.

    Returns:
        str: HTML page for error 413.
    """
    return render_template("413.html"), 413
