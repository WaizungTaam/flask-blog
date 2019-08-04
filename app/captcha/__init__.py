from io import BytesIO
from random import sample
from string import ascii_letters, digits

from captcha.image import ImageCaptcha
from flask import Blueprint, make_response, session


bp = Blueprint('captcha', __name__)

_captcha = ImageCaptcha()
_alphanum = ascii_letters + digits


def _rand_text(length=4, charset=_alphanum):
    return ''.join(sample(charset, length))

@bp.route('/captcha')
def captcha():
    text = _rand_text()
    image = _captcha.generate(text).getvalue()
    response = make_response(image)
    response.headers['Content-Type'] = 'image/png'
    session['captcha'] = text
    return response


from wtforms.widgets import html_params, HTMLString

class CaptchaWidget:
    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', 'text')
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        if 'required' not in kwargs and \
            'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        return HTMLString(
            '<input %s>' % self.html_params(name=field.name, **kwargs) + \
            '<img src="/captcha" onclick="this.src=\'/captcha?\' + ' + \
            'Math.random()" style="margin-top: 1rem;">')


from wtforms import Field
from wtforms.compat import text_type

class CaptchaField(Field):
    widget = CaptchaWidget()

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        elif self.data is None:
            self.data = ''

    def _value(self):
        return text_type(self.data) if self.data is not None else ''
