"""Change occupation to array

Revision ID: 003c723883cd
Revises: bc077453a9fc
Create Date: 2024-08-07 16:14:44.928437

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003c723883cd'
down_revision = 'bc077453a9fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('prices', sa.JSON(), nullable=True))
    op.alter_column('service', 'occupations',
               existing_type=mysql.JSON(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('service', 'occupations',
               existing_type=mysql.JSON(),
               nullable=True)
    op.drop_column('service', 'prices')
    # ### end Alembic commands ###
