from app.models.group_schema import GroupSchema
from app.repositories.group_repository import GroupRepository

class GroupService:
    def get(self, filters, page, per_page, team_id):
        return GroupRepository.get(filters=filters, page=page, per_page=per_page, team_id=team_id)

    def get_by_id(self, group_id, team_id=None):
        group = GroupRepository.get_by_id(group_id)
        if group is None or (team_id is not None and group.slack_organization_id != team_id):
            return None
        return group

    def add(self, data, team_id):
        data.slack_organization_id = team_id
        return GroupRepository.upsert(data)

    def update(self, group_id, data, team_id):
        group = GroupRepository.get_by_id(group_id)

        if group is None or group.slack_organization_id != team_id:
            return None

        updated_group = GroupSchema().load(data=data, instance=group, partial=True)
        return GroupRepository.upsert(updated_group)

    def delete(self, group_id, team_id):
        group = GroupRepository.get_by_id(group_id)

        if group is not None and group.slack_organization_id == team_id:
            GroupRepository.delete(group_id)
