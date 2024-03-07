from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class BookingForm(FlaskForm):
    num_tickets = IntegerField(
        "Number of Tickets*",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
    )
    submit = SubmitField("Book")
