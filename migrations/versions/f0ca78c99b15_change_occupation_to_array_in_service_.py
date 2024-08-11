"""Change occupation to array in Service mod222e

Revision ID: f0ca78c99b15
Revises: ff184daee5ec
Create Date: 2024-08-07 11:40:17.033116

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f0ca78c99b15'
down_revision = 'ff184daee5ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('occupations', sa.JSON(), nullable=False))
    op.drop_column('service', 'occupation')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('occupation', mysql.VARCHAR(length=255), nullable=False))
    op.drop_column('service', 'occupations')
    # ### end Alembic commands ###
