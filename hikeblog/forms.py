from flask_wtf import FlaskForm, RecaptchaField

from wtforms import StringField, TextAreaField, SelectMultipleField
from wtforms.validators import Required, Email
from wtforms.fields.html5 import EmailField


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[Required()])
    body = TextAreaField('Body', validators=[Required()])
    tags = SelectMultipleField('Tags', coerce=int)


class CommentForm(FlaskForm):
    author_name = StringField('Name', validators=[Required()])
    author_email = EmailField('Email', validators=[Required(), Email()])
    message = TextAreaField('Comment', validators=[Required()])
    recaptcha = RecaptchaField()
    

class NonValidatingSelectMultipleField(SelectMultipleField):
    """
    To accept dynamic choices added by the browser.
    """
    def pre_validate(self, form):
        pass


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[Required()])
    body = TextAreaField('Body', validators=[Required()])
    tags = NonValidatingSelectMultipleField('Tags')