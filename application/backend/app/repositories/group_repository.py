from app.models.group import Group
from app.models.mixins import CrudMixin


class GroupRepository(Group, CrudMixin):
    pass
