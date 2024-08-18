import logging
from flask import request, redirect, url_for, jsonify
from configs import app, login_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.unauthorized_handler
def unauthorized_callback():
    logger.warning("Unauthorized access attempt.")
    if "api" in request.base_url:
        return jsonify({'error': 'You must be logged in to access this resource.'}), 401
    else:
        return redirect(url_for('unauthorised_access'))


@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 Not Found error: {error}")
    if "api" in request.base_url:
        return jsonify({'error': 'The requested resource was not found.'}), 404
    else:
        return redirect(url_for('not_found'))


@app.errorhandler(405)
def not_allowed_error(error):
    logger.warning(f"405 Method Not Allowed error: {error}")
    return jsonify({'error': 'The method is not allowed for the requested URL.'}), 405

@app.errorhandler(415)
def unsupported_type_error(error):
    logger.warning(f"415 Unsupported Media Type error: {error}")
    return jsonify({'error': 'The media type is not supported.'}), 415
