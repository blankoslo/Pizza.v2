from sqlalchemy import Column, Integer, String, Table, ForeignKey

slack_user_group_association_table = Table('slack_user_group_association',
    Column('slack_user_id', String, ForeignKey('slack_users.slack_id')),
    Column('group_id', String, ForeignKey('groups.id'))
)
