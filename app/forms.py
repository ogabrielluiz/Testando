from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import Usuario
from app import mongo



class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = mongo.db.usuario.find_one({"_id": username.data})
        if user is not None:
            raise ValidationError("Escolha um nome diferente.")

    def validate_email(self, email):
        user = mongo.db.usuario.find_one({"email": email.data})
        if user is not None:
            raise ValidationError("Escolha um email diferente.")

class EditProfileForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('Sobre mim', validators=[Length(min=0, max=140)])
    submit = SubmitField('Salvar')

    def __init__(self,original_username,*args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = mongo.db.usuario.find_one({"_id": self.username.data})
            if user is not None:
                raise ValidationError("Please use a different username.")

class PostForm(FlaskForm):
    post = TextAreaField("Escreva algo", validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    submit = SubmitField('Salvar')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Email()])
    password2 = PasswordField('Repeat password',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request password reset')

