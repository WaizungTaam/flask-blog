from flask import render_template

from app import db
from app.error import bp


@bp.app_errorhandler(403)
def not_found_error(error):
    return render_template('error/403.html', title='403'), 403

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html', title='404'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html', title='500'), 500
