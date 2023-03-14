"""groups

Revision ID: 517fd200010d
Revises: 2fc5d793c575
Create Date: 2023-03-11 16:50:30.607835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '517fd200010d'
down_revision = '2fc5d793c575'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('slack_organization_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['slack_organization_id'], ['slack_organizations.team_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('slack_user_group_association',
    sa.Column('slack_user_id', sa.String(), nullable=False),
    sa.Column('group_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['slack_user_id'], ['slack_users.slack_id'], ),
    sa.PrimaryKeyConstraint('slack_user_id', 'group_id')
    )
    op.add_column('events', sa.Column('group_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'events', 'groups', ['group_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_column('events', 'group_id')
    op.drop_table('slack_user_group_association')
    op.drop_table('groups')
    # ### end Alembic commands ###