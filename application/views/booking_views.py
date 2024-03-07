from flask import redirect, url_for, render_template, Blueprint, flash
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user
from application.forms.booking_forms import BookingForm
from application.models import Booking, Show
from application.database import db
from datetime import datetime
from application.views.show_views import calculate_static_rating

booking_bp = Blueprint("booking", __name__)

# prefix of /book has been applied for this blueprint


@booking_bp.route("/register/<int:show_id>", methods=["POST"])
@login_required
def register(show_id):
    form = BookingForm()
    show = Show.query.get(show_id)

    if form.validate_on_submit():
        num_tickets = form.num_tickets.data

        if show.unsold_tickets >= num_tickets:
            new_booking = Booking(user_id=current_user.id, show_id=show_id, num_tickets=num_tickets)
            db.session.add(new_booking)

            show.unsold_tickets -= num_tickets
            show.rating += calculate_dynamic_rating(show)
            show.rating = min(5, show.rating)

            try:
                db.session.commit()
                flash("Booking successful!", "success")
                return redirect(url_for("user.dashboard"))
            except IntegrityError as e:
                db.session.rollback()
                if "foreign key constraint" in str(e).lower():
                    flash("The provided show does not exist.", "warning")
                else:
                    flash("Booking unsuccessful", "warning")
        else:
            flash(f"Only {show.unsold_tickets} tickets are available!", "warning")

    for field_name, field in form._fields.items():
        if field.errors:
            for error in field.errors:
                flash(f"{field.label.text} error: {error}", "warning")

    return render_template("show/show.html", show=show, form=form)


@booking_bp.route("/delete/<int:id>", methods=["POST"])
@login_required  # only for user
def delete(id):
    booking = Booking.query.get_or_404(id)
    show = booking.show
    show.unsold_tickets += booking.num_tickets
    show.rating = calculate_static_rating(show.start_time, show.end_time, show.ticket_price) + calculate_dynamic_rating(
        show
    )
    db.session.delete(booking)

    try:
        db.session.commit()
        flash("Booking successfully deleted", "success")
        return redirect(url_for("user.dashboard"))
    except Exception as e:
        flash("Error in deleting booking", "warning")
        return redirect(url_for("user.dashboard"))


def calculate_dynamic_rating(show):
    time_elapsed_seconds = (datetime.utcnow() - show.created_at).seconds

    # Calculate the rate of tickets sold
    sold_tickets = show.venue.capacity - show.unsold_tickets
    tickets_sold_per_second = sold_tickets / time_elapsed_seconds

    max_rate = 1 / 3600  # Assuming the max rate is 1 ticket sold per hour
    rating = min(tickets_sold_per_second / max_rate, 1) * 2
    rating += sold_tickets / show.venue.capacity

    return round(min(rating, 3), 2)
