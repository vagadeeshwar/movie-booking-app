from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, PasswordField, SubmitField, DateField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional
from flask_login import current_user
from werkzeug.security import check_password_hash


class RegistrationForm(FlaskForm):
    username = StringField("Username*", validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField(
        "Password*", validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "min 8 characters"}
    )
    confirm_password = PasswordField("Confirm Password*", validators=[DataRequired(), EqualTo("password")])
    email = StringField("Email*", validators=[DataRequired(), Email()])
    gender = RadioField("Gender*", choices=[("M", "Male"), ("F", "Female")], validators=[DataRequired()])
    mobile_number = StringField(
        "Mobile Number*",
        validators=[
            DataRequired(),
            Regexp(r"^\d{10}$", message="Mobile number must be exactly 10 digits"),
        ],  # message is used for error messages
    )
    dob = DateField("Date of Birth (YYYY-MM-DD)", format="%Y-%m-%d", validators=[Optional()])
    # Need not be filled - Optional() is only for code clarity
    submit = SubmitField("Sign Up")
    # Using no validators is same as Optional() "sometimes"... you will have to use Optional() in EditForm->dob as format is mentioned but we need the input to be optional also


class EditForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=4, max=80)])
    old_password = PasswordField(
        "Old Password", validators=[Length(min=8), Optional()], render_kw={"placeholder": "min 8 characters"}
    )
    new_password = PasswordField(
        "New Password", validators=[Length(min=8), Optional()], render_kw={"placeholder": "min 8 characters"}
    )
    email = StringField("Email", validators=[Email()])
    gender = RadioField("Gender", choices=[("M", "Male"), ("F", "Female")])
    mobile_number = StringField(
        "Mobile Number", validators=[Regexp(r"^(?:\d{10})?$", message="Mobile number must be exactly 10 digits")]
    )
    dob = DateField("Date of Birth (YYYY-MM-DD)", format="%Y-%m-%d", validators=[Optional()])
    submit = SubmitField("Apply Changes")

    # We can define custom validation functions for each field like this using validate_* function
    # validate_* -> * is passed into field... use form to access other values if necessary
    def validate_old_password(form, field):
        if field.data:  # Old password is filled
            if not check_password_hash(current_user.password, field.data):
                raise ValidationError("Old password is incorrect.")
        else:  # Old password is not filled
            if form.new_password.data:
                raise ValidationError("Please enter the old password.")

    def validate_new_password(form, field):
        if field.data:  # New password is filled
            if not form.old_password.data:
                raise ValidationError("Please enter the old password.")
        else:  # New password is not filled
            if form.old_password.data:
                raise ValidationError("Please enter a new password.")

    # render_kw, data(to set input value) can be set through a constructor like this also
    # def __init__(  # current_user is a proxy object that gets resolved at runtime, which means it's not accessible during the class definition. Instead, you should pass the user object when initializing the form.
    #     self, current_user, *args, **kwargs
    # ):  # accepting *args and **kwargs not necessary... this basically allows the function to take any number of args/pos args
    #     super(EditForm, self).__init__(*args, **kwargs)
    # self.email.render_kw = {"value": current_user.email}
    # self.gender.render_kw = {"value": current_user.gender}
    # # self.mobile_number.data = current_user.mobile_number
    # if current_user.dob:  # For non text input types it's not render_kw->placeholder, it's just default/data
    #     self.dob.render_kw = {"value": current_user.dob.strftime("%Y-%m-%d")}


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "min 8 characters"}
    )
    log_in = SubmitField("Log In")
