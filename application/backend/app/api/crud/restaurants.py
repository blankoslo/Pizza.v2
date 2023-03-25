from flask import views
from flask_smorest import Blueprint, abort
from app.models.restaurant_schema import RestaurantResponseSchema, RestaurantQueryArgsSchema, RestaurantUpdateSchema, RestaurantCreateSchema
from flask_jwt_extended import jwt_required, current_user
from app.services.injector import injector
from app.services.restaurant_service import RestaurantService

bp = Blueprint("restaurants", "restaurants", url_prefix="/restaurants", description="Operations on restaurants")

@bp.route("/")
class Restaurants(views.MethodView):
    @bp.arguments(RestaurantQueryArgsSchema, location="query")
    @bp.response(200, RestaurantResponseSchema(many=True))
    @bp.paginate()
    @jwt_required()
    def get(self, args, pagination_parameters):
        """List restaurants"""
        restaurant_service = injector.get(RestaurantService)
        total, restaurants = restaurant_service.get(filters=args, page=pagination_parameters.page, per_page=pagination_parameters.page_size, team_id=current_user.slack_organization.team_id)
        pagination_parameters.item_count = total
        return restaurants
    
    @bp.arguments(RestaurantCreateSchema)
    @bp.response(201, RestaurantResponseSchema)
    @jwt_required()
    def post(self, new_data):
        """Add a restaurant"""
        restaurant_service = injector.get(RestaurantService)
        return restaurant_service.add(data=new_data, team_id=current_user.slack_organization.team_id)

@bp.route("/<restaurant_id>")
class RestaurantsById(views.MethodView):
    @bp.response(200, RestaurantResponseSchema)
    @jwt_required()
    def get(self, restaurant_id):
        """Get restaurant by ID"""
        restaurant_service = injector.get(RestaurantService)
        restaurant = restaurant_service.get_by_id(restaurant_id=restaurant_id, team_id=current_user.slack_organization_id)
        if restaurant is None:
            abort(404, message = "Restaurant not found.")
        return restaurant
    
    @bp.arguments(RestaurantUpdateSchema)
    @bp.response(200, RestaurantResponseSchema)
    @jwt_required()
    def put(self, update_data, restaurant_id):
        """Update existing restaurant"""
        restaurant_service = injector.get(RestaurantService)
        updated_restaurant = restaurant_service.update(restaurant_id=restaurant_id, data=update_data, team_id=current_user.slack_organization_id)
        if updated_restaurant is None:
            abort(404, message = "Restaurant not found.")
        return updated_restaurant

    @bp.response(204)
    @jwt_required()
    def delete(self, restaurant_id):
        """Delete restaurant"""
        restaurant_service = injector.get(RestaurantService)
        success = restaurant_service.delete(restaurant_id=restaurant_id, team_id=current_user.slack_organization_id)
        if not success:
            abort(404, message="Restaurant not found.")
