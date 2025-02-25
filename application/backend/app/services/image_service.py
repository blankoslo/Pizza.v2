from app.models.image import Image
from app.repositories.image_repository import ImageRepository
from app.models.image_schema import ImageSchema

class ImageService:
    def get(self, filters, order_by, page, per_page, team_id):
        _order_by = None
        if order_by:
            _order_by = Image.uploaded_at.asc if order_by == 'ASC' else Image.uploaded_at.desc
        return ImageRepository.get(filters = filters, order_by=_order_by, page = page, per_page = per_page, team_id = team_id)

    def get_by_id(self, image_id, team_id):
        image = ImageRepository.get_by_id(image_id)
        if image is None or image.slack_organization_id != team_id:
            return None
        return image

    def delete(self, image_id, team_id):
        image = ImageRepository.get_by_id(image_id)
        if image is not None and image.slack_organization_id == team_id:
            ImageRepository.delete(image_id)
            return True
        return False

    def add(self, data, team_id):
        image_schema = ImageSchema()
        image = image_schema.load(data=data, partial=True)
        image.slack_organization_id = team_id
        return ImageRepository.upsert(image)
