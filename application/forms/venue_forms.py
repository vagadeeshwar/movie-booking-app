from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp


class RegistrationForm(FlaskForm):
    name = StringField("Venue Name*", validators=[DataRequired(), Length(min=2, max=80)])
    capacity = IntegerField("Capacity*", validators=[DataRequired()])
    city = StringField("City*", validators=[DataRequired(), Length(min=2, max=20)])
    state = StringField("State*", validators=[DataRequired(), Length(min=2, max=20)])
    mobile_number = StringField(
        "Mobile Number*",
        validators=[DataRequired(), Regexp(r"^\d{10}$", message="Mobile number must be exactly 10 digits")],
    )
    email = StringField("Email*", validators=[DataRequired(), Email()])
    description = TextAreaField("Description", validators=[Length(max=200)])
    submit = SubmitField("Create Venue")


class EditForm(FlaskForm):
    mobile_number = StringField(
        "Mobile Number", validators=[Regexp(r"^\d{10}$", message="Mobile number must be exactly 10 digits")]
    )
    email = StringField("Email", validators=[Email()])
    description = TextAreaField("Description", validators=[Length(max=200)])

    name = StringField("Venue Name", validators=[Length(min=2, max=80)])
    city = StringField("City", validators=[Length(min=2, max=20)])
    state = StringField("State", validators=[Length(min=2, max=20)])

    submit = SubmitField("Apply Changes")
