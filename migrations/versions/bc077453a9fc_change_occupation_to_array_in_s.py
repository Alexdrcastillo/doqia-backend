"""Change occupation to array in S

Revision ID: bc077453a9fc
Revises: 0c365f15dbe6
Create Date: 2024-08-07 16:07:26.246129

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bc077453a9fc'
down_revision = '0c365f15dbe6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('service', 'occupations',
               existing_type=mysql.JSON(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('service', 'occupations',
               existing_type=mysql.JSON(),
               nullable=False)
    # ### end Alembic commands ###
