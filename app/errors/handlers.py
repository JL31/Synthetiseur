"""
    Module to handle the errors for the application
"""

# ==================================================================================================
#
# IMPORTS
#
# ==================================================================================================

from flask import render_template, request

from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response


# ==================================================================================================
#
# INITIALIZATIONS
#
# ==================================================================================================

# ==================================================================================================
#
# CLASSES
#
# ==================================================================================================

# ==================================================================================================
#
# FUNCTIONS
#
# ==================================================================================================

# ========================
def wants_json_response():
    """
        ...
    """

    return request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]

# =========================
@bp.app_errorhandler(404)
def not_found_error(error):
    """
        Function to display specific page for 400 error
    """

    if wants_json_response():

        return api_error_response(404)

    return render_template("errors/error_404.html"), 404

# ========================
@bp.app_errorhandler(500)
def internal_error(error):
    """
        Function to display specific page for 500 error
    """

    db.session.rollback()

    if wants_json_response():

        return api_error_response(500)

    return render_template("errors/error_500.html"), 500


# ==================================================================================================
#
# USE
#
# ==================================================================================================
