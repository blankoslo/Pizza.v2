"""Added delete field to restaurant

Revision ID: 1c295781695a
Revises: ff17a933d7cd
Create Date: 2022-08-23 19:45:21.890137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c295781695a'
down_revision = 'ff17a933d7cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('restaurants', sa.Column('deleted', sa.Boolean(), nullable=False, server_default='f'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('restaurants', 'deleted')
    # ### end Alembic commands ###