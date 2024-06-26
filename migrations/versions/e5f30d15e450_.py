"""empty message

Revision ID: e5f30d15e450
Revises: 7055753edd30
Create Date: 2024-05-13 19:03:28.234761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5f30d15e450'
down_revision = '7055753edd30'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Shows', schema=None) as batch_op:
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Shows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Shows_id_seq"\'::regclass)'), autoincrement=True, nullable=False))

    # ### end Alembic commands ###
