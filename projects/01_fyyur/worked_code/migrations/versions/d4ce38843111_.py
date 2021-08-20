"""empty message

Revision ID: d4ce38843111
Revises: cb10dddd1f09
Create Date: 2021-08-19 21:14:02.439708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4ce38843111'
down_revision = 'cb10dddd1f09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('looking_venue', sa.Boolean(), nullable=True))
    op.drop_column('Artist', 'looking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('looking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'looking_venue')
    # ### end Alembic commands ###
