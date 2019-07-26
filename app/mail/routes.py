from flask import render_template, abort, redirect, url_for, flash
from flask_login import current_user, login_required

from app.mail import bp
from app.mail.models import Mail
from app.mail.forms import MailForm
from app import db
from app.user.models import User


@bp.route('/mails', methods=['GET', 'POST'])
@login_required
def mailbox():
    form = MailForm()
    if form.validate_on_submit():
        mail = Mail(
            title=form.title.data,
            content=form.content.data,
            read=False,
            sender=current_user,
            receiver=User.query.filter_by(username=form.receiver.data).first()
        )
        db.session.add(mail)
        db.session.commit()
        flash('Mail sent.')
        return redirect(url_for('mail.mailbox'))
    return render_template('mail/mailbox.html', title='Mailbox', form=form)

@bp.route('/mails/<int:id>')
@login_required
def show_mail(id):
    mail = Mail.query.get(id)
    if current_user != mail.sender and current_user != mail.receiver:
        abort(403)
    if current_user == mail.receiver and not mail.read:
        mail.read = True
        db.session.commit()
    return render_template('mail/show_mail.html', title=mail.title, mail=mail)
