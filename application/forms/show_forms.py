from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, FloatField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, ValidationError


class RegistrationForm(FlaskForm):
    name = StringField("Name*", validators=[DataRequired(), Length(min=2, max=80)])
    tags = StringField("Tags", validators=[Length(max=255)])
    ticket_price = FloatField("Ticket Price*", validators=[DataRequired()])
    venue_id = IntegerField("Venue ID*", validators=[DataRequired()])
    start_time = DateTimeLocalField("Start Time*", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    end_time = DateTimeLocalField("End Time*", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])

    description = TextAreaField("Description", validators=[Length(max=200)])
    submit = SubmitField("Create Show")

    def validate_start_time(form, field):
        if form.start_time.data >= form.end_time.data:
            raise ValidationError("Start time must be earlier than the end time.")


class EditForm(FlaskForm):
    tags = StringField("Tags", validators=[Length(max=255)])
    description = TextAreaField("Description", validators=[Length(max=200)])

    submit = SubmitField("Apply Changes")
