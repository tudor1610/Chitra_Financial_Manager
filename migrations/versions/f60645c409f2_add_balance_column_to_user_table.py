"""Add balance column to user table

Revision ID: f60645c409f2
Revises: a02951412f2b
Create Date: 2025-01-06 17:03:09.586957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f60645c409f2'
down_revision = 'a02951412f2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('token', sa.String(length=64), nullable=True))
        batch_op.create_unique_constraint(None, ['token'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('token')

    # ### end Alembic commands ###