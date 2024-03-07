from flask_restful import Api, Resource
from flask import Blueprint, jsonify
from flask_login import login_required
from application.models import User, Show, Venue, Booking
from application.decorators import admin_required

# Create a new Flask blueprint for the API
api_bp = Blueprint("api", __name__)
api = Api(api_bp)


class VenueResource(Resource):
    def get(self, venue_id):
        venue = Venue.query.get(venue_id)
        if venue:
            return jsonify(venue.serialize())
        else:
            return {"error": "Venue not found"}, 404


class ShowResource(Resource):
    def get(self, show_id):
        show = Show.query.get(show_id)
        if show:
            return jsonify(show.serialize())
        else:
            return {"error": "Show not found"}, 404


class BookingResource(Resource):
    @login_required
    @admin_required
    def get(self, booking_id):
        booking = Booking.query.get(booking_id)
        if booking:
            return jsonify(booking.serialize())
        else:
            return {"error": "Booking not found"}, 404


class UserResource(Resource):
    @login_required
    @admin_required
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return jsonify(user.serialize())
        else:
            return {"error": "User not found"}, 404


api.add_resource(VenueResource, "/venue/<int:venue_id>")
api.add_resource(ShowResource, "/show/<int:show_id>")
api.add_resource(BookingResource, "/booking/<int:booking_id>")
api.add_resource(UserResource, "/user/<int:user_id>")
