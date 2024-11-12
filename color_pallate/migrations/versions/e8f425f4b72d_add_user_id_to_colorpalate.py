"""Add user_id to colorpalate

Revision ID: e8f425f4b72d
Revises: 
Create Date: 2023-10-10 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8f425f4b72d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('color_palette') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_color_palette_user', 'user', ['user_id'], ['id'])


def downgrade():
    with op.batch_alter_table('color_palette') as batch_op:
        batch_op.drop_constraint('fk_color_palette_user', type_='foreignkey')
        batch_op.drop_column('user_id')