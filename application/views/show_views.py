from flask import request, redirect, url_for, render_template, Blueprint, flash
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user
from application.forms.show_forms import RegistrationForm, EditForm
from application.forms.booking_forms import BookingForm
from application.models import Show, Venue, User, Booking
from application.database import db
from application.decorators import admin_required

show_bp = Blueprint("show", __name__)

# prefix of /show has been applied for this blueprint


@show_bp.route("/register", methods=["GET", "POST"])  # Create a new venue
@login_required
@admin_required
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        venue = Venue.query.get(form.venue_id.data)
        rating = calculate_static_rating(form.start_time.data, form.end_time.data, form.ticket_price.data)

        new_show = Show(
            name=form.name.data,
            tags=form.tags.data,
            ticket_price=form.ticket_price.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            description=form.description.data,
            unsold_tickets=venue.capacity,
            rating=rating,
        )
        db.session.add(new_show)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "foreign key constraint" in str(e).lower():
                flash("The provided venue does not exist.", "warning")
            else:
                flash("Registration unsuccessful", "warning")

            return redirect(url_for("show.register"))
        flash("Show registered successfully!", "success")
        venue_id = request.form.get("venue_id", None)
        if venue_id:
            return redirect(url_for("venue.venue", id=venue_id))
        return redirect(url_for("user.dashboard"))
    elif request.method == "POST":
        for field_name, field in form._fields.items():
            if field.errors:
                for error in field.errors:
                    flash(f"{field.label.text} error: {error}", "warning")

    id = request.args.get("id", None)  # get('param_name',default)
    return render_template("show/register.html", form=form, venue_id=id)


@show_bp.route("/<int:id>", methods=["GET", "POST"])
# render show page as well allow edits (edit button should be shown only for admins)
@login_required  # may have to redirect role="user" post requests to some error page
def show(id):
    show = Show.query.get_or_404(id)
    form = EditForm()

    if current_user.role == "user":  # even if user sends post request, only non-editable page will be displayed
        return render_template("show/show.html", show=show, form=BookingForm())
    else:
        if form.validate_on_submit():
            show = Show.query.get(id)

            show.tags = form.tags.data
            show.description = form.description.data

            try:  # db constraints validations
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                flash("Registration unsuccessful", "warning")
                return redirect(url_for("show.show", id=id))
            flash("Edit successful!", "success")
            return redirect(url_for("show.show", id=id))
        elif request.method == "POST":
            for field_name, field in form._fields.items():
                if field.errors:
                    for error in field.errors:
                        flash(f"{field.label.text} error: {error}", "warning")
    form.process(obj=show)  # display editable show page for admin get request
    return render_template("show/show_admin.html", show=show, form=form)


@show_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete(id):
    show = Show.query.get_or_404(id)

    if show.bookings:
        # If shows are associated with the venue, return an error message
        flash(
            "Cannot delete a show with associated bookings. Please remove all bookings before deleting the show.",
            "danger",
        )
        return redirect(url_for("show.show", id=id))

    # If no shows are associated, delete the venue and redirect back to the dashboard
    db.session.delete(show)
    try:
        db.session.commit()
        flash("Show successfully deleted.", "success")
        return redirect(url_for("user.dashboard"))
    except Exception as e:
        flash("Error in deleting show", "warning")
        return redirect(url_for("show.show", id=id))


@show_bp.route("/filter")
@login_required
def filter():
    name = request.args.get("name", None)
    tag = request.args.get("tag", None)
    rating = request.args.get("rating", None)
    start_datetime = request.args.get("start_datetime", None)
    end_datetime = request.args.get("end_datetime", None)
    min_price = request.args.get("min_price", None)
    max_price = request.args.get("max_price", None)

    query = Show.query

    if name:
        query = query.filter(Show.name == name)
    if tag:
        query = query.filter(Show.tags.ilike(f"%{tag}%"))
    if rating:
        query = query.filter((Show.rating >= int(rating) - 1) & (Show.rating <= int(rating) + 1))
    if start_datetime:
        query = query.filter(Show.start_time >= start_datetime)
    if end_datetime:
        query = query.filter(Show.end_time <= end_datetime)
    if min_price:
        query = query.filter(Show.ticket_price >= int(min_price))
    if max_price:
        query = query.filter(Show.ticket_price <= int(max_price))

    venues = Venue.query.all()
    shows = query.all()
    users = User.query.all()
    bookings = Booking.query.all() if current_user.role == "admin" else current_user.bookings

    return render_template("user/dashboard.html", venues=venues, shows=shows, bookings=bookings, users=users)


# Static part of rating (2 points) calculated at show creation
def calculate_static_rating(start_time, end_time, price):
    rating = 0

    duration = (end_time - start_time).seconds / 3600
    optimal_duration = 2.5
    rating += max(1 - abs(duration - optimal_duration) / optimal_duration, 0)

    optimal_price = 500

    if price <= optimal_price:
        rating += 1
    else:
        rating += max(1 - (price - optimal_price) / optimal_price, 0)  # rating of 0  at twice the optimal price
    return round(rating, 2)
