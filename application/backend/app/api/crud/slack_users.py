from flask import views
from flask_smorest import Blueprint, abort
from app.models.slack_user_schema import SlackUserSchema, SlackUserUpdateSchema, SlackUserQueryArgsSchema
from flask_jwt_extended import jwt_required
from app.services.injector import injector
from app.services.slack_user_service import SlackUserService

bp = Blueprint("users", "users", url_prefix="/users", description="Operations on users")

@bp.route("/")
class SlackUsers(views.MethodView):
    @bp.arguments(SlackUserQueryArgsSchema, location="query")
    @bp.response(200, SlackUserSchema(many=True))
    @bp.paginate()
    def get(self, args, pagination_parameters):
        """List slack_users"""
        slack_user_service = injector.get(SlackUserService)
        total, slack_users = slack_user_service.get(args, pagination_parameters.page, pagination_parameters.page_size, order_by_ascending = True)
        pagination_parameters.item_count = total
        return slack_users

@bp.route("/<slack_user_id>")
class SlackUsersById(views.MethodView):
    @bp.response(200, SlackUserSchema)
    def get(self, slack_user_id):
        """Get slack_user by ID"""
        slack_user_service = injector.get(SlackUserService)
        slack_user = slack_user_service.get_by_id(slack_user_id)
        if slack_user is None:
            abort(404, message = "User not found.")
        return slack_user

    @bp.arguments(SlackUserUpdateSchema)
    @bp.response(200, SlackUserSchema)
    @jwt_required()
    def put(self, update_data, slack_user_id):
        """Update existing user"""
        slack_user_service = injector.get(SlackUserService)
        updated_slack_user = slack_user_service.update(slack_user_id, update_data)
        if updated_slack_user is None:
            abort(422, message = "User not found.")
        return updated_slack_user
