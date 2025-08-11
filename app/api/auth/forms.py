from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email


class ForgotPasswordForm(FlaskForm):
    email = StringField("Enter your email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send reset link")


class ResetPasswordForm(FlaskForm):
    password = StringField("New Password", validators=[DataRequired()])
    submit = SubmitField("Reset")
