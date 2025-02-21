from app.repositories.restaurant_repository import RestaurantRepository
from app.models.restaurant_schema import RestaurantSchema

class RestaurantService:
    def get(self, filters, page, per_page, team_id):
        return RestaurantRepository.get(filters = filters, page = page, per_page = per_page, team_id = team_id)

    def get_by_id(self, restaurant_id, team_id = None):
        restaurant = RestaurantRepository.get_by_id(restaurant_id)
        if restaurant is None or (team_id is not None and restaurant.slack_organization_id != team_id):
            return None
        return restaurant

    def add(self, data, team_id):
        data.slack_organization_id = team_id
        return RestaurantRepository.upsert(data)

    def update(self, restaurant_id, data, team_id):
        restaurant = RestaurantRepository.get_by_id(restaurant_id)

        if restaurant is None or restaurant.slack_organization_id != team_id:
            return None

        updated_restaurant = RestaurantSchema().load(data=data, instance=restaurant, partial=True)
        return RestaurantRepository.upsert(updated_restaurant)

    def delete(self, restaurant_id, team_id):
        restaurant = RestaurantRepository.get_by_id(restaurant_id)

        if restaurant is not None and restaurant.slack_organization_id == team_id:
            updated_restaurant = RestaurantSchema().load(data={"deleted": True}, instance=restaurant, partial=True)
            RestaurantRepository.upsert(updated_restaurant)
            return True
        return False
