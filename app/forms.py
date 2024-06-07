from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, DataRequired, Email, EqualTo, Regexp
from app import db
from app.models import User, select_user_by_email, insert_user

#BASED ON THIS: https://en.wikipedia.org/wiki/Email_address
# Valid characters: The domain name must only consist of letters (a-z), numbers (0-9), and hyphens ("-").
# Starting characters: The domain name must start and end with a letter or number.
quotes = r"(\"[a-zA-Z0-9\!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~\.\(\)\,\:\;\<\>\[\]\\\@\s]+\")"
valid_starting_characters = r"([a-zA-Z0-9\!\#\$\%\&\'\*\+\-\/\=\?\^\_\\\`\{\|\}\~]|("+quotes+r"))"
local_part = f"{valid_starting_characters}+(\.{valid_starting_characters}+)*"
main_domain_name = r"[a-zA-Z0-9](([a-zA-Z0-9]|-)*[a-zA-Z0-9])?"
chained_domain_names = f"{main_domain_name}(\.{main_domain_name})*"
possible_domain_endings = r"(com|org|net|int|edu|gov|mil|us|dk|se|no)" #VERY RESTRICTIVE
email_regexp = f"{local_part}@{chained_domain_names}\.{possible_domain_endings}"
email_validator = Regexp(email_regexp, message="Not valid email.")


class LoginForm(FlaskForm):
    email = StringField('Email-address', validators=[DataRequired(), email_validator])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), email_validator]) #Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = select_user_by_email(email)
        
        if user is not None:
            raise ValidationError('Please use a different email address.')