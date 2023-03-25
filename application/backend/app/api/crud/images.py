from flask import views
from flask_smorest import Blueprint, abort
from app.models.image_schema import ImageResponseSchema, ImageQueryArgsSchema
from flask_jwt_extended import jwt_required, current_user
from app.services.injector import injector
from app.services.image_service import ImageService

bp = Blueprint("images", "images", url_prefix="/images", description="Operations on images")

@bp.route("/")
class Images(views.MethodView):
    @bp.arguments(ImageQueryArgsSchema, location="query")
    @bp.response(200, ImageResponseSchema(many=True))
    @bp.paginate()
    @jwt_required()
    def get(self, args, pagination_parameters):
        """List images"""
        image_service = injector.get(ImageService)
        order = None
        if 'order' in args:
            order = args.pop('order')
        total, images = image_service.get(filters=args, order_by=order, page=pagination_parameters.page, per_page=pagination_parameters.page_size, team_id=current_user.slack_organization_id)
        pagination_parameters.item_count = total
        return images

@bp.route("/<image_id>")
class ImagesById(views.MethodView):
    @bp.response(200, ImageResponseSchema)
    @jwt_required()
    def get(self, image_id):
        """Get image by ID"""
        image_service = injector.get(ImageService)
        image = image_service.get_by_id(image_id=image_id, team_id=current_user.slack_organization_id)
        if image is None:
            abort(404, message = "Image not found.")
        return image

    @bp.response(204)
    @jwt_required()
    def delete(self, image_id):
        """Delete image"""
        image_service = injector.get(ImageService)
        success = image_service.delete(image_id=image_id, team_id=current_user.slack_organization_id)
        if not success:
            abort(400, message="Something went wrong.")
