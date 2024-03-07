from application.database import db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):  # UserMixin is used for flask-login auth
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gender = db.Column(db.String(1), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    mobile_number = db.Column(db.String(15), nullable=False, unique=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "gender": self.gender,
            "dob": self.dob.strftime("%Y-%m-%d") if self.dob else None,
            "mobile_number": self.mobile_number,
        }


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(200))

    shows = db.relationship("Show", backref="venue", lazy=True)  # Show objects can use .venue

    # and venue objects can use .shows
    def __repr__(self):
        return f"<Venue {self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "capacity": self.capacity,
            "mobile_number": self.mobile_number,
            "email": self.email,
            "description": self.description,
            "created_at": self.created_at,
        }


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Float)  # Some alg must dynamically change this value based on bookings
    tags = db.Column(db.String(255), nullable=True)
    ticket_price = db.Column(db.Float, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(200))
    unsold_tickets = db.Column(db.Integer)  # change this when a booking happens

    def __repr__(self):
        return f"<Show {self.name}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rating": self.rating,
            "tags": self.tags,
            "ticket_price": self.ticket_price,
            "venue_id": self.venue_id,
            "start_time": self.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": self.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "description": self.description,
            "unsold_tickets": self.unsold_tickets,
        }


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship(
        "User", backref="bookings", lazy=True
    )  # user_obj.bookings -> see arguments & booking_obj.user -> .user attribute in Booking
    show = db.relationship("Show", backref="bookings", lazy=True)

    def __repr__(self):
        return f"<Booking {self.id} - User: {self.user_id}, Show: {self.show_id}>"

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "show_id": self.show_id,
            "num_tickets": self.num_tickets,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
