from flask import request, redirect, url_for, render_template, Blueprint, flash
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user
from application.forms.venue_forms import RegistrationForm, EditForm
from application.models import User, Venue, Show, Booking
from application.database import db
from application.decorators import admin_required

venue_bp = Blueprint("venue", __name__)

# prefix of /venue has been applied for this blueprint


@venue_bp.route("/register", methods=["GET", "POST"])  # Create a new venue
@login_required
@admin_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_venue = Venue(
            name=form.name.data,
            capacity=form.capacity.data,
            city=form.city.data,
            state=form.state.data,
            mobile_number=form.mobile_number.data,
            email=form.email.data,
            description=form.description.data,
        )
        db.session.add(new_venue)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed: venue.name" in str(e):
                flash("Registration unsuccessful: Name already exists", "warning")
            if "UNIQUE constraint failed: venue.email" in str(e):
                flash("Registration unsuccessful: Email already exists", "warning")
            if "UNIQUE constraint failed: venue.mobile_number" in str(e):
                flash("Registration unsuccessful: Mobile number already exists", "warning")
            return redirect(url_for("venue.register"))
        flash("Venue registered successfully!", "success")
        return redirect(url_for("user.dashboard"))
    elif request.method == "POST":
        for field_name, field in form._fields.items():
            if field.errors:
                for error in field.errors:
                    flash(f"{field.label.text} error: {error}", "warning")
    return render_template("venue/register.html", form=form)


@venue_bp.route("/<int:id>", methods=["GET", "POST"])
# render venue page as well allow edits (edit button should be showed only for admins)!
@login_required  # may have to redirect role="user" post requests to some error page
def venue(id):
    venue = Venue.query.get_or_404(id)
    # Venue not found error shouldn't be possible as the link will be displayed only if the show exists but handle it using some error page ig
    form = EditForm()
    if current_user.role == "user":  # even if user sends post req...only non editable page will be displayed
        return render_template("venue/venue.html", venue=venue)
    else:
        if form.validate_on_submit():
            venue = Venue.query.get(id)
            venue.name = form.name.data
            venue.email = form.email.data
            venue.mobile_number = form.mobile_number.data
            venue.description = form.description.data
            venue.city = form.city.data
            venue.state = form.state.data

            try:  # db constraints validations
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                if "UNIQUE constraint failed: venue.name" in str(e):
                    flash("Edit unsuccessful: Venue Name already exists", "warning")
                if "UNIQUE constraint failed: venue.mobile_number" in str(e):
                    flash("Edit unsuccessful: Mobile number already exists", "warning")
                if "UNIQUE constraint failed: venue.email" in str(e):
                    flash("Edit unsuccessful: Email already exists", "warning")
                return redirect(url_for("venue.venue", id=id))
            flash("Edit successful!", "success")  # (message,category)
            return redirect(url_for("venue.venue", id=id))
        elif request.method == "POST":
            for field_name, field in form._fields.items():
                if field.errors:
                    for error in field.errors:
                        flash(f"{field.label.text} error: {error}", "warning")
    form.process(obj=venue)  # display editable venue page for admin get request
    return render_template("venue/venue_admin.html", venue=venue, form=form)


@venue_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete(id):
    venue = Venue.query.get_or_404(id)

    if venue.shows:
        # If shows are associated with the venue, return an error message
        flash(
            "Cannot delete a venue with associated shows. Please remove all shows before deleting the venue.", "danger"
        )
        return redirect(url_for("venue.venue", id=id))

    # If no shows are associated, delete the venue and redirect back to the dashboard
    db.session.delete(venue)
    try:
        db.session.commit()
        flash("Venue successfully deleted.", "success")
        return redirect(url_for("user.dashboard"))
    except Exception as e:
        flash("Error in deleting venue", "warning")
        return redirect(url_for("venue.venue", id=id))


@venue_bp.route("/filter")
@login_required
def filter():
    name = request.args.get("name", None)
    city = request.args.get("city", None)
    state = request.args.get("state", None)

    query = Venue.query

    if name:
        query = query.filter(Venue.name == name)
    if city:
        query = query.filter(Venue.city == city)
    if state:
        query = query.filter(Venue.state == state)

    venues = query.all()
    shows = Show.query.all()
    users = User.query.all()
    bookings = Booking.query.all() if current_user.role == "admin" else current_user.bookings

    return render_template("user/dashboard.html", venues=venues, shows=shows, bookings=bookings, users=users)
