"""Change occupation to array in Service

Revision ID: 37b69f904e2c
Revises: a612f27b43f7
Create Date: 2024-08-07 14:12:23.645041

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '37b69f904e2c'
down_revision = 'a612f27b43f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service', 'occupation')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('occupation', mysql.VARCHAR(length=255), nullable=False))
    # ### end Alembic commands ###
