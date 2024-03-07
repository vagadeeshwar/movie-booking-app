from flask import request, redirect, url_for, render_template, Blueprint, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, login_required, logout_user, current_user
from application.forms.user_forms import RegistrationForm, LoginForm, EditForm
from application.models import User, Show, Venue, Booking
from application.database import db
from application.decorators import admin_required

user_bp = Blueprint("user", __name__)  # (blueprint_name, module_name)


@user_bp.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)  # flask-login library
            return redirect(url_for("user.dashboard"))
        else:
            flash("Invalid username or password.", "warning")
    return render_template("user/login.html", form=form)


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            role="user",
            mobile_number=form.mobile_number.data,
            dob=form.dob.data,
            gender=form.gender.data,
        )
        db.session.add(new_user)
        try:  # db constraints validations
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed: user.username" in str(e):
                flash("Registration unsuccessful: Username already exists", "warning")
            if "UNIQUE constraint failed: user.email" in str(e):
                flash(
                    "Registration unsuccessful: Email already exists", "warning"
                )  # Only the latest flashed message gets printed onto webpage ....dk why...dw too much...whereas in the below elif snipped all flashed messages get printed
            if "UNIQUE constraint failed: user.mobile_number" in str(e):
                flash("Registration unsuccessful: Mobile number already exists", "warning")
            return redirect(url_for("user.register"))
        flash("Registration successful! Please log in.", "success")  # (message,category)
        return redirect(url_for("user.login"))
    elif request.method == "POST":
        # if form.password.errors or form.confirm_password.errors:
        #     for error in form.password.errors + form.confirm_password.errors:
        #         flash(f"Password error: {error}", "warning")
        # if form.mobile_number.errors:
        #     for error in form.mobile_number.errors:
        #         flash(f"Mobile Number error: {error}", "warning")
        for field_name, field in form._fields.items():
            if field.errors:
                for error in field.errors:
                    flash(f"{field.label.text} error: {error}", "warning")

    return render_template("user/register.html", form=form)  # get request


@user_bp.route("/user", methods=["GET", "POST"])
@login_required
def profile():
    form = EditForm()  # pass current_user if you are using constructor initialization instead of form.process
    if form.validate_on_submit():
        flag = False  # Will be set if password/username is changed
        user = User.query.get(current_user.id)
        user.email = form.email.data
        if form.dob.data is not None:
            user.dob = form.dob.data
        if form.mobile_number.data:
            user.mobile_number = form.mobile_number.data
        if form.old_password.data and form.new_password.data:
            current_user.password = generate_password_hash(form.new_password.data)
            flag = True
        user.gender = form.gender.data
        if current_user.username != form.username.data:
            flag = True
            user.username = form.username.data

        try:  # db constraints validations
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed: user.email" in str(e):
                flash("Edit unsuccessful: Email already exists", "warning")
            if "UNIQUE constraint failed: user.mobile_number" in str(e):
                flash("Edit unsuccessful: Mobile number already exists", "warning")
            if "UNIQUE constraint failed: user.username" in str(e):
                flash("Edit unsuccessful: Username already exists", "warning")
            return redirect(url_for("user.profile"))
        flash("Edit successful!", "success")  # (message,category)
        if flag:
            logout_user()
            return redirect(url_for("user.login"))
        return redirect(url_for("user.profile"))
    elif request.method == "POST":
        for field_name, field in form._fields.items():
            if field.errors:
                for error in field.errors:
                    flash(f"{field.label.text} error: {error}", "warning")
    form.process(obj=current_user)
    # Automatically matches input names and attributes of current_user tuple to fill up the form... uses placeholders for some and values for others...can't seem to override this behaviour
    return render_template("user/profile.html", form=form)


@user_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.login"))


@user_bp.route("/dashboard")
@login_required
def dashboard():  # All venues,bookings,shows will be displayed
    shows = Show.query.all()
    venues = Venue.query.all()
    users = User.query.all()
    bookings = Booking.query.all() if current_user.role == "admin" else current_user.bookings

    return render_template("user/dashboard.html", venues=venues, shows=shows, bookings=bookings, users=users)


@user_bp.route("/delete", methods=["POST"])
@login_required
def delete():
    try:
        user = User.query.get(current_user.id)

        # Delete all bookings associated with the user
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
        for booking in bookings:
            db.session.delete(booking)

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        flash("Your account and bookings have been deleted.", "success")
        return redirect(url_for("user.login"))

    except Exception as e:
        db.session.rollback()
        flash("An error occurred while trying to delete your account. Please try again.", "warning")
        return redirect(url_for("user.profile"))


@user_bp.route("/get")
@login_required
@admin_required
def user():
    user_id = request.args.get("user_id", None)
    if user_id:
        user = User.query.get(user_id)
        return render_template("user/user.html", user=user)
    return redirect("user.dashboard")
