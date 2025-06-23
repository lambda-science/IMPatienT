from flask import send_from_directory, current_app
from impatient.app.dashapp import bp


# @bp.route(bp.static_folder + "/<path:filename>")
# def image_folder_seg(filename):
#     """Serve files located in patient subfolder inside folder"""
#     return send_from_directory(bp.static_folder, filename)


@bp.route("/data/images/<path:filename>")
def images_folder(filename):
    """Serve files located in patient subfolder inside folder"""
    return send_from_directory(current_app.config["IMAGES_FOLDER"], filename)
